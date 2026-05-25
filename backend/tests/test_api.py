from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def test_upload_endpoint_creates_mock_draft_artifacts():
    fixture = Path(__file__).parent / "fixtures" / "sample_paper.pdf"
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
    with fixture.open("rb") as handle:
        response = client.post(
            "/api/papers/upload",
            data={"deck_mode": "reading_group", "language": "zh"},
            files={"file": ("sample_paper.pdf", handle, "application/pdf")},
        )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["job"]["mock_mode"] is True
    assert payload["job"]["status"] == "completed_with_warnings"
    assert payload["job"]["download_artifact_name"] == "draft_deck.pptx"
    assert payload["paper_summary"] is not None
    artifact_names = {item["name"] for item in payload["job"]["artifacts"] if item["exists"]}
    assert "parsed_paper.json" in artifact_names
    assert "draft_deck.pptx" in artifact_names
    assert "grounding_report.json" in artifact_names
    assert "final_deck.pptx" not in artifact_names


def test_real_generation_requires_api_key():
    fixture = Path(__file__).parent / "fixtures" / "sample_paper.pdf"
    client = TestClient(app)

    save_response = client.post(
        "/api/config/model",
        json={
            "llm_provider": "openai",
            "llm_base_url": "https://api.openai.com/v1",
            "llm_api_key": "",
            "llm_model": "gpt-5.5",
            "fallback_llm_model": "gpt-4.1-mini",
            "vision_provider": "openai",
            "vision_base_url": "https://api.openai.com/v1",
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
    assert save_response.status_code == 200

    with fixture.open("rb") as handle:
        response = client.post(
            "/api/papers/upload",
            data={"deck_mode": "reading_group", "language": "zh"},
            files={"file": ("sample_paper.pdf", handle, "application/pdf")},
        )
    assert response.status_code == 400
    assert "API Key" in response.json()["detail"]
