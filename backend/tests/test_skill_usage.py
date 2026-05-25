from __future__ import annotations

import json
import zipfile
from pathlib import Path

from app.schemas.skill_library import SkillSearchRequest
from app.schemas.usage import UsageRecord
from app.skills.router import SkillRouter
from app.skills.search import MockSkillSearchProvider
from app.storage.skill_storage import SkillStorage
from app.storage.usage_storage import UsageStorage


def _write_skill_folder(base: Path, skill_id: str = "skill_demo", include_python: bool = False) -> Path:
    folder = base / skill_id
    (folder / "prompts").mkdir(parents=True, exist_ok=True)
    (folder / "templates").mkdir(parents=True, exist_ok=True)
    manifest = {
        "id": skill_id,
        "name": "演示技能",
        "description": "用于测试的本地技能。",
        "version": "0.1.0",
        "source": "local",
        "author": "pytest",
        "tags": ["business-report"],
        "capabilities": ["business-report", "writing-polish"],
        "entrypoints": ["scripts/tool.py"] if include_python else [],
        "suggestions": ["标题更短", "结论前置"],
        "constraints": ["不要改动未请求页面"],
    }
    (folder / "skill.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (folder / "README.md").write_text("# 演示技能\n\n仅用于测试。\n", encoding="utf-8")
    (folder / "prompts" / "outline.md").write_text("请强化商业结构。", encoding="utf-8")
    if include_python:
        (folder / "scripts").mkdir(parents=True, exist_ok=True)
        (folder / "scripts" / "tool.py").write_text("import os\nprint(os.environ)\n", encoding="utf-8")
    return folder


def test_skill_registry_created():
    storage = SkillStorage()
    assert storage.root.exists()
    assert storage.registry_path.exists()
    assert storage.installed_dir.exists()


def test_skill_import_enable_disable_delete(tmp_path: Path):
    storage = SkillStorage()
    folder = _write_skill_folder(tmp_path)
    imported = storage.import_from_folder(folder)
    assert imported.skill.enabled is False
    enabled = storage.enable_skill(imported.skill.id)
    assert enabled.enabled is True
    disabled = storage.disable_skill(imported.skill.id)
    assert disabled.enabled is False
    storage.delete_skill(imported.skill.id)
    assert all(skill.id != imported.skill.id for skill in storage.list_skills())


def test_skill_import_zip_and_path_traversal_blocked(tmp_path: Path):
    storage = SkillStorage()
    folder = _write_skill_folder(tmp_path, "zip_skill")
    zip_path = tmp_path / "zip_skill.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        for file_path in folder.rglob("*"):
            if file_path.is_file():
                archive.write(file_path, arcname=f"{folder.name}/{file_path.relative_to(folder)}")
    imported = storage.import_from_zip(zip_path)
    assert imported.skill.id == "zip_skill"

    evil_zip = tmp_path / "evil.zip"
    with zipfile.ZipFile(evil_zip, "w") as archive:
        archive.writestr("../escape.txt", "bad")
    try:
        storage.import_from_zip(evil_zip)
        assert False, "expected traversal rejection"
    except ValueError as exc:
        assert "非法路径" in str(exc)


def test_high_risk_skill_default_disabled(tmp_path: Path):
    storage = SkillStorage()
    folder = _write_skill_folder(tmp_path, "risky_skill", include_python=True)
    imported = storage.import_from_folder(folder, preview_only=True)
    assert imported.skill.enabled is False
    assert imported.skill.trusted is False
    assert imported.skill.risk_level in {"medium", "high"}


def test_skill_router_limits_and_skips_disabled(tmp_path: Path):
    storage = SkillStorage()
    for index in range(4):
        folder = _write_skill_folder(tmp_path / f"skill_{index}", f"skill_{index}")
        storage.import_from_folder(folder)
        storage.enable_skill(f"skill_{index}")
    router = SkillRouter()
    selected = router.select_for_stage("Outline", max_skills_per_task=3)
    assert len(selected) == 3
    guidance, records = router.build_stage_guidance("Outline", selected, max_skill_context_tokens=50)
    assert len(records) <= 3
    assert len(guidance) <= 100


def test_usage_storage_summary_export_and_clear():
    storage = UsageStorage()
    storage.record(
        UsageRecord(
            task_id="task_1",
            session_id="task_1",
            model="mock",
            fallback_model="",
            stage="Outline",
            prompt_tokens=None,
            completion_tokens=None,
            total_tokens=None,
            request_count=1,
            duration_ms=12,
            mode="mock",
            slide_count=8,
            mock=True,
            provider_usage_available=False,
        )
    )
    summary = storage.summary()
    assert summary.total_records == 1
    assert summary.unknown_usage_records == 1
    csv_path = storage.export_csv(storage.root / "usage.csv")
    json_path = storage.export_json(storage.root / "usage.json")
    assert csv_path.exists()
    assert json_path.exists()
    storage.clear()
    assert storage.list_records() == []


def test_mock_skill_search_provider():
    results = MockSkillSearchProvider().search(SkillSearchRequest(keyword="business", tags=[], capabilities=[]))
    assert any(item.id == "skill_business_report" for item in results)


def test_skill_and_usage_api_endpoints(tmp_path: Path):
    from fastapi.testclient import TestClient

    from app.main import app

    folder = _write_skill_folder(tmp_path, "api_skill")
    client = TestClient(app)

    zip_path = tmp_path / "api_skill.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        for file_path in folder.rglob("*"):
            if file_path.is_file():
                archive.write(file_path, arcname=f"{folder.name}/{file_path.relative_to(folder)}")
    with zip_path.open("rb") as handle:
        imported = client.post("/api/skills/import", files={"file": ("api_skill.zip", handle, "application/zip")})
    assert imported.status_code == 200, imported.text

    skills = client.get("/api/skills")
    assert skills.status_code == 200
    assert any(item["id"] == "api_skill" for item in skills.json()["skills"])

    search = client.post("/api/skills/search", json={"keyword": "chart", "tags": [], "capabilities": []})
    assert search.status_code == 200
    assert isinstance(search.json()["results"], list)

    enabled = client.post("/api/skills/api_skill/enable")
    assert enabled.status_code == 200
    assert enabled.json()["enabled"] is True

    tested = client.post("/api/skills/api_skill/test")
    assert tested.status_code == 200
    assert tested.json()["ok"] is True

    usage_summary = client.get("/api/usage/summary")
    assert usage_summary.status_code == 200
    assert "summary" in usage_summary.json()

    usage_tasks = client.get("/api/usage/tasks")
    assert usage_tasks.status_code == 200
    assert "tasks" in usage_tasks.json()
