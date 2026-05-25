from pathlib import Path

from fastapi.testclient import TestClient

from app.api import routes
from app.main import app
from app.schemas.deck import CriticIssue, CriticReport, RepairHistory


ROOT = Path(__file__).resolve().parents[2]


def test_critic_failure_marks_quality_failed(monkeypatch):
    client = TestClient(app)
    fixture = Path(__file__).parent / "fixtures" / "sample_paper.pdf"
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

    failed_report = CriticReport(
        deck_score=58,
        summary="Critic 审核未通过。",
        zh_summary="质量检查未通过，建议继续精修。",
        approved=False,
        issues=[
            CriticIssue(
                slide_id="slide_02",
                severity="high",
                category="confidence_marker",
                description="Confidence should not appear.",
                zh_message="页面出现 Confidence 字样。",
                suggested_fix="删除置信度文案并补充论文依据。",
                requires_regeneration=True,
            )
        ],
    )

    monkeypatch.setattr(routes.pipeline.critic, "run", lambda *args, **kwargs: failed_report)
    monkeypatch.setattr(routes.pipeline.repair, "run", lambda *args, **kwargs: (args[1], RepairHistory()))

    with fixture.open("rb") as handle:
        response = client.post(
            "/api/papers/upload",
            data={"deck_mode": "reading_group", "language": "zh"},
            files={"file": ("sample_paper.pdf", handle, "application/pdf")},
        )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["job"]["status"] == "quality_failed"
    assert payload["job"]["delivery_ready"] is False
    assert payload["job"]["download_artifact_name"] == "draft_deck.pptx"
    artifact_names = {item["name"] for item in payload["job"]["artifacts"] if item["exists"]}
    assert "draft_deck.pptx" in artifact_names
    assert "final_deck.pptx" not in artifact_names


def test_frontend_localizes_mock_and_labels():
    status_text = (ROOT / "frontend" / "src" / "components" / "StatusPanel.tsx").read_text(encoding="utf-8")
    artifacts_text = (ROOT / "frontend" / "src" / "components" / "ArtifactsPanel.tsx").read_text(encoding="utf-8")
    labels_text = (ROOT / "frontend" / "src" / "utils" / "labels.ts").read_text(encoding="utf-8")
    warnings_text = (ROOT / "frontend" / "src" / "components" / "WarningsPanel.tsx").read_text(encoding="utf-8")
    preview_text = (ROOT / "frontend" / "src" / "components" / "OutlinePreview.tsx").read_text(encoding="utf-8")
    model_config_text = (ROOT / "frontend" / "src" / "components" / "ModelConfigPanel.tsx").read_text(encoding="utf-8")

    assert "当前为 Mock 模式，仅用于流程测试，生成内容不是正式质量。" in status_text
    assert "下载测试文件" in artifacts_text
    assert "下载草稿 PPT" in artifacts_text
    assert 'reading_group: "论文精读"' in labels_text
    assert 'thesis_defense: "毕业答辩"' in labels_text
    assert 'completed: "已完成"' in labels_text
    assert 'quality_failed: "质量未通过"' in labels_text
    assert "issue.zh_message || issue.description" in warnings_text
    assert 'Abstract: "摘要"' in labels_text
    assert "paperSummary.one_sentence_summary" in preview_text
    assert "请填写 API Key 后再进行正式生成。" in model_config_text
    assert "Mock 模式不会调用真实模型，只用于测试上传、生成、下载流程。" in model_config_text
