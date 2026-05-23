import shutil
from pathlib import Path

from app.config import get_settings
from app.schemas.deck import ArtifactItem, JobStatus
from app.utils.json_utils import read_json, write_json


class FileStorage:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_dir = self.settings.storage_path
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.settings.uploads_path.mkdir(parents=True, exist_ok=True)
        self.settings.decks_path.mkdir(parents=True, exist_ok=True)
        self.settings.config_path.mkdir(parents=True, exist_ok=True)
        self.settings.logs_path.mkdir(parents=True, exist_ok=True)

    def get_job_dir(self, job_id: str) -> Path:
        path = self.settings.decks_path / job_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def peek_job_dir(self, job_id: str) -> Path:
        return self.settings.decks_path / job_id

    def get_artifact_path(self, job_id: str, filename: str) -> Path:
        return self.get_job_dir(job_id) / filename

    def save_upload(self, job_id: str, source_path: Path) -> Path:
        target = self.settings.uploads_path / f"{job_id}_original.pdf"
        shutil.copyfile(source_path, target)
        return target

    def save_bytes(self, job_id: str, filename: str, content: bytes) -> Path:
        if filename.lower().endswith(".pdf"):
            path = self.settings.uploads_path / f"{job_id}_{filename}"
        else:
            path = self.get_artifact_path(job_id, filename)
        path.write_bytes(content)
        return path

    def save_json_artifact(self, job_id: str, filename: str, data: dict) -> Path:
        path = self.get_artifact_path(job_id, filename)
        write_json(path, data)
        return path

    def load_json_artifact(self, job_id: str, filename: str) -> dict:
        return read_json(self.get_artifact_path(job_id, filename))

    def list_artifacts(self, job_id: str) -> list[ArtifactItem]:
        names = [
            "original.pdf",
            "parsed_paper.json",
            "extracted_assets.json",
            "paper_summary.json",
            "deck_plan.json",
            "slide_drafts.json",
            "grounding_report.json",
            "critic_report.json",
            "repair_history.json",
            "user_instruction_raw.md",
            "user_instruction_spec.json",
            "merged_generation_config.json",
            "prompt_merge_report.json",
            "final_deck.pptx",
            "job_status.json",
        ]
        items: list[ArtifactItem] = []
        for name in names:
            path = self.get_artifact_path(job_id, name)
            modified = path.stat().st_mtime if path.exists() else None
            items.append(
                ArtifactItem(
                    name=name,
                    path=str(path),
                    exists=path.exists(),
                    modified_time=modified,
                    download_url=f"/api/decks/{job_id}/artifacts/{name}" if path.exists() else None,
                )
            )
        return items

    def save_job_status(self, status: JobStatus) -> Path:
        path = self.get_artifact_path(status.job_id, "job_status.json")
        write_json(path, status.model_dump())
        return path

    def load_job_status(self, job_id: str) -> JobStatus:
        return JobStatus(**self.load_json_artifact(job_id, "job_status.json"))

    def save_text_artifact(self, job_id: str, filename: str, content: str) -> Path:
        path = self.get_artifact_path(job_id, filename)
        path.write_text(content, encoding="utf-8")
        return path

    def touch_job_stage(self, job_id: str, stage: str, message: str = "", profile_id: str | None = None) -> JobStatus:
        path = self.get_artifact_path(job_id, "job_status.json")
        if path.exists():
            status = JobStatus(**read_json(path))
        else:
            status = JobStatus(job_id=job_id, status="processing", paper_id=job_id, deck_id=job_id)
        status.current_stage = stage
        if message:
            status.message = message
        if profile_id:
            status.profile_id = profile_id
        self.save_job_status(status)
        return status
