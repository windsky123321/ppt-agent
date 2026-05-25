from __future__ import annotations

import hashlib
import json
import logging
import shutil
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from app.runtime_paths import skills_root
from app.schemas.skill_library import SkillImportResponse, SkillManifest, SkillRegistry, SkillTestResponse
from app.utils.json_utils import read_json, write_json


logger = logging.getLogger(__name__)

MAX_SKILL_FILE_BYTES = 5 * 1024 * 1024


class SkillStorage:
    def __init__(self) -> None:
        self.root = Path()
        self.registry_path = Path()
        self.installed_dir = Path()
        self.ensure_structure()

    def ensure_structure(self) -> None:
        self._sync_paths()
        self.installed_dir.mkdir(parents=True, exist_ok=True)
        if not self.registry_path.exists():
            write_json(self.registry_path, SkillRegistry().model_dump())

    def list_skills(self) -> list[SkillManifest]:
        self.ensure_structure()
        registry = SkillRegistry(**read_json(self.registry_path))
        return registry.skills

    def get_skill(self, skill_id: str) -> SkillManifest:
        for skill in self.list_skills():
            if skill.id == skill_id:
                return skill
        raise FileNotFoundError(skill_id)

    def import_from_folder(
        self,
        folder_path: Path,
        *,
        source: str = "folder",
        allow_overwrite: bool = False,
        preview_only: bool = False,
    ) -> SkillImportResponse:
        self._sync_paths()
        folder = folder_path.resolve()
        if not folder.exists() or not folder.is_dir():
            raise ValueError("未找到技能目录。")
        manifest, warnings = self._load_and_scan_manifest(folder, source=source)
        if preview_only:
            return SkillImportResponse(skill=manifest, warnings=warnings, preview_only=True)
        self._install_folder(folder, manifest, allow_overwrite=allow_overwrite)
        logger.info("skill installed: %s source=%s risk=%s", manifest.id, source, manifest.risk_level)
        return SkillImportResponse(skill=manifest, warnings=warnings, preview_only=False)

    def import_from_zip(
        self, zip_path: Path, *, allow_overwrite: bool = False, preview_only: bool = False
    ) -> SkillImportResponse:
        self._sync_paths()
        if not zip_path.exists():
            raise ValueError("未找到技能压缩包。")
        with tempfile.TemporaryDirectory(prefix="ppt_skill_") as temp_dir:
            temp_root = Path(temp_dir)
            with zipfile.ZipFile(zip_path) as archive:
                self._safe_extract_zip(archive, temp_root)
            extracted = self._normalize_import_root(temp_root)
            return self.import_from_folder(
                extracted,
                source="zip",
                allow_overwrite=allow_overwrite,
                preview_only=preview_only,
            )

    def import_from_url(self, source_url: str, *, preview_only: bool = False) -> SkillImportResponse:
        self._sync_paths()
        if not source_url.startswith("mock://") and "github.com" not in source_url:
            raise ValueError("当前版本仅支持 mock URL 或 GitHub 仓库占位导入。")
        skill_id = source_url.split("/")[-1].replace(":", "_").replace(".", "_")
        manifest = SkillManifest(
            id=skill_id,
            name=f"导入技能 {skill_id}",
            description="通过安全占位导入的外部技能，默认禁用且不可信。",
            version="0.1.0",
            source=source_url,
            author="外部来源",
            homepage=source_url,
            tags=["external"],
            capabilities=["writing-polish"],
            enabled=False,
            trusted=False,
            risk_level="unknown",
            installed_at=datetime.now(timezone.utc).isoformat(),
            checksum=hashlib.sha256(source_url.encode("utf-8")).hexdigest(),
            suggestions=["保持结构清晰", "避免无依据扩写"],
            constraints=["默认不执行脚本", "默认不读取用户文件", "默认不联网"],
        )
        warnings = ["该来源使用安全占位导入，当前不会联网下载。"]
        if preview_only:
            return SkillImportResponse(skill=manifest, warnings=warnings, preview_only=True)
        self._save_manifest_folder(manifest)
        return SkillImportResponse(skill=manifest, warnings=warnings, preview_only=False)

    def enable_skill(self, skill_id: str) -> SkillManifest:
        return self._mutate_skill(skill_id, enabled=True)

    def disable_skill(self, skill_id: str) -> SkillManifest:
        return self._mutate_skill(skill_id, enabled=False)

    def delete_skill(self, skill_id: str) -> None:
        self._sync_paths()
        skill_dir = self.installed_dir / skill_id
        if skill_dir.exists():
            shutil.rmtree(skill_dir)
        registry = [item for item in self.list_skills() if item.id != skill_id]
        write_json(self.registry_path, SkillRegistry(skills=registry).model_dump())
        logger.info("skill deleted: %s", skill_id)

    def touch_last_used(self, skill_id: str) -> None:
        self._mutate_skill(skill_id, last_used_at=datetime.now(timezone.utc).isoformat())

    def test_skill(self, skill_id: str) -> SkillTestResponse:
        skill = self.get_skill(skill_id)
        return SkillTestResponse(
            skill_id=skill_id,
            ok=True,
            message="技能可用。当前版本只会读取静态建议，不会执行外部脚本。",
            suggestions=skill.suggestions[:3],
            constraints=skill.constraints[:3],
        )

    def _mutate_skill(self, skill_id: str, **changes: object) -> SkillManifest:
        self._sync_paths()
        skills = self.list_skills()
        updated: list[SkillManifest] = []
        target: SkillManifest | None = None
        for skill in skills:
            if skill.id == skill_id:
                target = skill.model_copy(update=changes)
                updated.append(target)
            else:
                updated.append(skill)
        if target is None:
            raise FileNotFoundError(skill_id)
        write_json(self.registry_path, SkillRegistry(skills=updated).model_dump())
        manifest_path = self.installed_dir / skill_id / "skill.json"
        if manifest_path.exists():
            write_json(manifest_path, target.model_dump())
        logger.info("skill updated: %s changes=%s", skill_id, ",".join(changes.keys()))
        return target

    def _install_folder(self, folder: Path, manifest: SkillManifest, *, allow_overwrite: bool) -> None:
        target = self.installed_dir / manifest.id
        if target.exists() and not allow_overwrite:
            raise ValueError("技能已存在，默认不允许覆盖。")
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(folder, target)
        write_json(target / "skill.json", manifest.model_dump())
        skills = [item for item in self.list_skills() if item.id != manifest.id]
        skills.append(manifest)
        write_json(self.registry_path, SkillRegistry(skills=skills).model_dump())

    def _save_manifest_folder(self, manifest: SkillManifest) -> None:
        self._sync_paths()
        target = self.installed_dir / manifest.id
        target.mkdir(parents=True, exist_ok=True)
        readme_path = target / "README.md"
        if not readme_path.exists():
            readme_path.write_text(f"# {manifest.name}\n\n{manifest.description}\n", encoding="utf-8")
        write_json(target / "skill.json", manifest.model_dump())
        skills = [item for item in self.list_skills() if item.id != manifest.id]
        skills.append(manifest)
        write_json(self.registry_path, SkillRegistry(skills=skills).model_dump())

    def _load_and_scan_manifest(self, folder: Path, *, source: str) -> tuple[SkillManifest, list[str]]:
        manifest_path = folder / "skill.json"
        skill_markdown = folder / "SKILL.md"
        if manifest_path.exists():
            manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
        elif skill_markdown.exists():
            first_line = skill_markdown.read_text(encoding="utf-8").splitlines()[0].lstrip("# ").strip()
            manifest_data = {
                "id": folder.name,
                "name": first_line or folder.name,
                "description": "从 SKILL.md 自动生成的技能清单。",
                "version": "0.1.0",
            }
        else:
            raise ValueError("技能包缺少 skill.json 或 SKILL.md。")
        warnings, risk_level = self._scan_risk(folder)
        checksum = self._checksum_dir(folder)
        manifest_payload = dict(manifest_data)
        manifest_payload["source"] = manifest_payload.get("source") or source
        manifest_payload["enabled"] = False
        manifest_payload["trusted"] = False
        manifest_payload["risk_level"] = risk_level
        manifest_payload["installed_at"] = datetime.now(timezone.utc).isoformat()
        manifest_payload["checksum"] = checksum
        manifest = SkillManifest(**manifest_payload)
        return manifest, warnings

    def _safe_extract_zip(self, archive: zipfile.ZipFile, target: Path) -> None:
        for info in archive.infolist():
            if info.file_size > MAX_SKILL_FILE_BYTES:
                raise ValueError("技能包包含过大的文件，已拒绝导入。")
            name = Path(info.filename)
            if name.is_absolute() or ".." in name.parts:
                raise ValueError("技能包包含非法路径，已拒绝导入。")
        archive.extractall(target)

    def _normalize_import_root(self, target: Path) -> Path:
        entries = [entry for entry in target.iterdir() if entry.name != "__MACOSX"]
        if len(entries) == 1 and entries[0].is_dir():
            return entries[0]
        return target

    def _scan_risk(self, folder: Path) -> tuple[list[str], str]:
        warnings: list[str] = []
        risk_score = 0
        for path in folder.rglob("*"):
            if path.is_dir():
                continue
            suffix = path.suffix.lower()
            if suffix in {".exe", ".dll", ".so"}:
                warnings.append(f"检测到二进制文件：{path.name}")
                risk_score = max(risk_score, 3)
            elif suffix in {".bat", ".ps1", ".sh"}:
                warnings.append(f"检测到可执行脚本：{path.name}")
                risk_score = max(risk_score, 3)
            elif suffix == ".py":
                warnings.append(f"检测到 Python 脚本：{path.name}")
                risk_score = max(risk_score, 2)
            if path.stat().st_size > MAX_SKILL_FILE_BYTES:
                warnings.append(f"文件过大：{path.name}")
                risk_score = max(risk_score, 2)
            if suffix in {".md", ".txt", ".json", ".py"}:
                text = path.read_text(encoding="utf-8", errors="ignore")
                if any(token in text for token in ["httpx.", "requests.", "urllib", "socket.", "aiohttp"]):
                    warnings.append(f"疑似联网逻辑：{path.name}")
                    risk_score = max(risk_score, 2)
                if any(token in text for token in ["os.environ", "getenv(", "OPENAI_API_KEY", "VISION_API_KEY"]):
                    warnings.append(f"疑似环境变量读取：{path.name}")
                    risk_score = max(risk_score, 2)
                if any(token in text for token in ["shutil.rmtree", "os.remove", "Path.unlink", "Remove-Item"]):
                    warnings.append(f"疑似删除文件操作：{path.name}")
                    risk_score = max(risk_score, 3)
                if any(token in text for token in ["C:\\Windows", "/etc/", "System32", "AppData"]):
                    warnings.append(f"疑似访问系统目录：{path.name}")
                    risk_score = max(risk_score, 2)
        if risk_score >= 3:
            return warnings, "high"
        if risk_score == 2:
            return warnings, "medium"
        if risk_score == 1:
            return warnings, "low"
        return warnings, "low" if not warnings else "unknown"

    def _checksum_dir(self, folder: Path) -> str:
        hasher = hashlib.sha256()
        for path in sorted(item for item in folder.rglob("*") if item.is_file()):
            hasher.update(str(path.relative_to(folder)).encode("utf-8"))
            hasher.update(path.read_bytes())
        return hasher.hexdigest()

    def _sync_paths(self) -> None:
        self.root = skills_root()
        self.registry_path = self.root / "registry.json"
        self.installed_dir = self.root / "installed"
