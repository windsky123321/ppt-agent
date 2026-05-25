from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def test_mock_e2e_generation_download_and_artifacts():
    client = TestClient(app)
    reset = client.post(
        "/api/config/model",
        json={
            "llm_provider": "mock",
            "llm_base_url": "",
            "llm_api_key": "",
            "llm_model": "gpt-5.5",
            "fallback_llm_model": "gpt-4.1-mini",
            "vision_provider": "mock",
            "vision_base_url": "",
            "vision_api_key": "",
            "vision_model": "gpt-4.1-mini",
            "enable_vision": True,
            "enable_critic": True,
            "enable_repair": True,
            "max_repair_loops": 2,
            "reasoning_effort": "low",
            "verbosity": "low",
            "temperature": 0.2,
            "patch_mode": True,
            "revision_max_output_tokens": 1200,
            "normal_max_output_tokens": 4000,
            "output_dir": "storage/decks",
            "skills_enabled": True,
            "auto_select_skills": True,
            "max_skills_per_task": 3,
            "max_skill_context_tokens": 800,
            "allow_skill_scripts": False,
            "allowed_skill_risk_level": "low",
        },
    )
    assert reset.status_code == 200

    fixture = Path(__file__).parent / "fixtures" / "sample_paper.pdf"
    long_instruction = (Path(__file__).parent / "fixtures" / "long_instruction_zh_reading_group.txt").read_text(encoding="utf-8")

    with fixture.open("rb") as handle:
        upload = client.post(
            "/api/papers/upload",
            data={
                "deck_mode": "reading_group",
                "language": "zh",
                "long_instruction": long_instruction,
            },
            files={"file": ("sample_paper.pdf", handle, "application/pdf")},
        )

    assert upload.status_code == 200, upload.text
    payload = upload.json()
    deck_id = payload["job"]["deck_id"]
    assert payload["job"]["mock_mode"] is True
    assert payload["job"]["download_artifact_name"] == "draft_deck.pptx"
    assert payload["download_url"].endswith(f"/api/decks/{deck_id}/download")

    artifacts = client.get(f"/api/decks/{deck_id}/artifacts")
    assert artifacts.status_code == 200
    artifact_payload = artifacts.json()
    artifact_names = {item["name"] for item in artifact_payload["artifacts"] if item["exists"]}
    assert artifact_payload["mock_mode"] is True
    assert artifact_payload["delivery_ready"] is False
    assert artifact_payload["quality_status"] == "mock"
    assert "draft_deck.pptx" in artifact_names
    assert "final_deck.pptx" not in artifact_names
    assert "job_status.json" in artifact_names
    assert "merged_generation_config.json" in artifact_names
    assert "user_instruction_spec.json" in artifact_names

    download = client.get(f"/api/decks/{deck_id}/download")
    assert download.status_code == 200
    assert "draft_deck.pptx" in download.headers["content-disposition"]
    assert download.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )
    assert len(download.content) > 0


def test_model_api_keys_are_masked_and_not_leaked_in_response():
    client = TestClient(app)
    secret = "sk-live-should-not-leak"

    saved = client.post(
        "/api/config/model",
        json={
            "llm_provider": "openai",
            "llm_base_url": "https://api.openai.com/v1",
            "llm_api_key": secret,
            "llm_model": "gpt-5.5",
            "fallback_llm_model": "gpt-4.1-mini",
            "vision_provider": "mock",
            "vision_base_url": "",
            "vision_api_key": "",
            "vision_model": "gpt-4.1-mini",
            "enable_vision": True,
            "enable_critic": True,
            "enable_repair": True,
            "max_repair_loops": 2,
            "reasoning_effort": "low",
            "verbosity": "low",
            "temperature": 0.2,
            "patch_mode": True,
            "revision_max_output_tokens": 1200,
            "normal_max_output_tokens": 4000,
            "output_dir": "storage/decks",
            "skills_enabled": True,
            "auto_select_skills": True,
            "max_skills_per_task": 3,
            "max_skill_context_tokens": 800,
            "allow_skill_scripts": False,
            "allowed_skill_risk_level": "low",
        },
    )
    assert saved.status_code == 200
    assert secret not in saved.text

    fetched = client.get("/api/config/model")
    assert fetched.status_code == 200
    assert secret not in fetched.text
    assert "****" in fetched.json()["llm_api_key_masked"]

    reset = client.post(
        "/api/config/model",
        json={
            "llm_provider": "mock",
            "llm_base_url": "",
            "llm_api_key": "",
            "llm_model": "gpt-5.5",
            "fallback_llm_model": "gpt-4.1-mini",
            "vision_provider": "mock",
            "vision_base_url": "",
            "vision_api_key": "",
            "vision_model": "gpt-4.1-mini",
            "enable_vision": True,
            "enable_critic": True,
            "enable_repair": True,
            "max_repair_loops": 2,
            "reasoning_effort": "low",
            "verbosity": "low",
            "temperature": 0.2,
            "patch_mode": True,
            "revision_max_output_tokens": 1200,
            "normal_max_output_tokens": 4000,
            "output_dir": "storage/decks",
            "skills_enabled": True,
            "auto_select_skills": True,
            "max_skills_per_task": 3,
            "max_skill_context_tokens": 800,
            "allow_skill_scripts": False,
            "allowed_skill_risk_level": "low",
        },
    )
    assert reset.status_code == 200
