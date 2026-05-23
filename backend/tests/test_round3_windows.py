import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.instructions import ParsedInstructionSpec
from app.storage.config_storage import ConfigStorage
from app.utils.instruction_utils import merge_profile_with_instruction, parse_instruction_rule_based
from app.utils.profile_utils import default_profiles, profile_to_settings


def load_text_fixture(name: str) -> str:
    return (Path(__file__).parent / "fixtures" / name).read_text(encoding="utf-8")


def load_json_fixture(name: str) -> dict:
    return json.loads((Path(__file__).parent / "fixtures" / name).read_text(encoding="utf-8"))


def test_runtime_model_config_masking_and_prompt_templates(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("STORAGE_DIR", str(tmp_path / "storage"))
    client = TestClient(app)
    saved = client.post(
        "/api/config/model",
        json={
            "llm_provider": "mock",
            "llm_base_url": "",
            "llm_api_key": "sk-test-secret",
            "llm_model": "mock-model",
            "vision_provider": "mock",
            "vision_base_url": "",
            "vision_api_key": "vision-secret",
            "vision_model": "mock-vision-model",
            "enable_vision": True,
            "enable_critic": True,
            "enable_repair": True,
            "max_repair_loops": 2,
        },
    )
    assert saved.status_code == 200

    fetched = client.get("/api/config/model")
    assert fetched.status_code == 200
    assert "****" in fetched.json()["llm_api_key_masked"]

    templates = client.get("/api/prompt-templates")
    assert templates.status_code == 200
    assert len(templates.json()["templates"]) >= 1


def test_long_instruction_parse_and_merge():
    spec = parse_instruction_rule_based(load_text_fixture("long_instruction_zh_reading_group.txt"), "zh")
    assert spec.preferred_language == "zh"
    assert spec.audience == "graduate"
    assert spec.include_speaker_notes is True
    assert "literal_translation" in spec.avoid

    profile = default_profiles()[0]
    settings = profile_to_settings(profile)
    settings.long_instruction = load_text_fixture("long_instruction_zh_reading_group.txt")
    merged, report = merge_profile_with_instruction(profile, settings, spec, "Reading Group")
    assert merged.language == "zh"
    assert merged.include_discussion_questions is True
    assert "slide_count_target" in report.applied_overrides


def test_instruction_parse_endpoint_and_generation_artifacts(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("STORAGE_DIR", str(tmp_path / "storage"))
    client = TestClient(app)

    parsed = client.post(
        "/api/instructions/parse",
        json={"raw_text": load_text_fixture("long_instruction_zh_reading_group.txt"), "language_hint": "zh"},
    )
    assert parsed.status_code == 200
    ParsedInstructionSpec(**parsed.json())

    fixture = Path(__file__).parent / "fixtures" / "sample_paper.pdf"
    with fixture.open("rb") as handle:
        upload = client.post(
            "/api/papers/upload",
            data={"deck_mode": "Reading Group", "long_instruction": load_text_fixture("long_instruction_zh_reading_group.txt")},
            files={"file": ("sample_paper.pdf", handle, "application/pdf")},
        )
    assert upload.status_code == 200, upload.text
    deck_id = upload.json()["job"]["deck_id"]
    artifacts = client.get(f"/api/decks/{deck_id}/artifacts")
    assert artifacts.status_code == 200
    artifact_names = {item["name"] for item in artifacts.json()["artifacts"] if item["exists"]}
    assert "user_instruction_raw.md" in artifact_names
    assert "user_instruction_spec.json" in artifact_names
    assert "merged_generation_config.json" in artifact_names
    assert "prompt_merge_report.json" in artifact_names


def test_instruction_fixture_schema():
    parsed = load_json_fixture("parsed_instruction_spec.json")
    ParsedInstructionSpec(**parsed)
    assert ConfigStorage().default_prompt_templates()
