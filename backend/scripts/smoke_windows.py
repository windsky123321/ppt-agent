import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient

from app.main import app


def main() -> None:
    client = TestClient(app)

    health = client.get("/api/health")
    assert health.status_code == 200

    model_config = {
        "llm_provider": "mock",
        "llm_base_url": "https://api.openai.com/v1",
        "llm_api_key": "",
        "llm_model": "mock-model",
        "vision_provider": "mock",
        "vision_base_url": "https://api.openai.com/v1",
        "vision_api_key": "",
        "vision_model": "mock-vision-model",
        "enable_vision": True,
        "enable_critic": True,
        "enable_repair": True,
        "max_repair_loops": 2,
    }
    saved = client.post("/api/config/model", json=model_config)
    assert saved.status_code == 200
    tested = client.post("/api/config/model/test", json=model_config)
    assert tested.status_code == 200
    assert tested.json()["success"] is True

    templates = client.get("/api/prompt-templates")
    assert templates.status_code == 200
    assert len(templates.json()["templates"]) >= 1

    long_instruction = (ROOT / "tests" / "fixtures" / "long_instruction_zh_reading_group.txt").read_text(encoding="utf-8")
    parsed_instruction = client.post("/api/instructions/parse", json={"raw_text": long_instruction, "language_hint": "zh", "save_as_preset": False})
    assert parsed_instruction.status_code == 200

    profile = client.post("/api/profiles", json={"name": "Windows Smoke Profile", "preferred_language": "zh"})
    assert profile.status_code == 200
    profile_id = profile.json()["id"]

    fixture = ROOT / "tests" / "fixtures" / "sample_paper.pdf"
    with fixture.open("rb") as handle:
        upload = client.post(
            "/api/papers/upload",
            data={"profile_id": profile_id, "deck_mode": "reading_group", "long_instruction": long_instruction},
            files={"file": ("sample_paper.pdf", handle, "application/pdf")},
        )
    assert upload.status_code == 200, upload.text
    upload_payload = upload.json()
    deck_id = upload_payload["job"]["deck_id"]
    artifacts = client.get(f"/api/decks/{deck_id}/artifacts")
    assert artifacts.status_code == 200
    artifact_payload = artifacts.json()
    artifact_names = {item["name"] for item in artifact_payload["artifacts"] if item["exists"]}
    assert "user_instruction_raw.md" in artifact_names
    assert "user_instruction_spec.json" in artifact_names
    assert "merged_generation_config.json" in artifact_names
    assert artifact_payload["download_artifact_name"] == "draft_deck.pptx"
    assert "draft_deck.pptx" in artifact_names

    regen = client.post(
        f"/api/decks/{deck_id}/regenerate-slide",
        json={"slide_ids": ["slide_02"], "instruction": "Make this slide more visual and reduce text.", "long_instruction": long_instruction, "profile_id": profile_id},
    )
    assert regen.status_code == 200, regen.text
    print(f"WINDOWS_SMOKE_OK {deck_id}")


if __name__ == "__main__":
    main()
