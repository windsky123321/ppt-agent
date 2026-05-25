from pathlib import Path

from fastapi import APIRouter, Body, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.agents.instruction_parser_agent import InstructionParserAgent
from app.agents.pipeline import PaperToPPTPipeline
from app.schemas.api import (
    HealthResponse,
    ProfilesResponse,
    PromptTemplatesResponse,
    RegenerateSlideRequest,
    SkillsResponse,
    UploadResponse,
    UsageSummaryResponse,
    UsageTaskResponse,
)
from app.schemas.common import GenerationSettings
from app.schemas.instructions import LongInstructionInput
from app.schemas.profile import CreateProfileRequest, UserProfile
from app.schemas.prompt_template import PromptTemplate
from app.schemas.runtime_config import ModelTestResponse, RuntimeModelConfig, RuntimeModelConfigView
from app.schemas.skill_library import SkillImportResponse, SkillSearchRequest, SkillSearchResponse, SkillTestResponse
from app.storage.config_storage import ConfigStorage
from app.storage.file_storage import FileStorage
from app.storage.profile_storage import ProfileStorage
from app.storage.skill_storage import SkillStorage
from app.storage.usage_storage import UsageStorage
from app.utils.profile_utils import build_inline_profile, profile_to_settings

router = APIRouter(prefix="/api")
pipeline = PaperToPPTPipeline()
storage = FileStorage()
profile_storage = ProfileStorage()
config_storage = ConfigStorage()
skill_storage = SkillStorage()
usage_storage = UsageStorage()
instruction_parser = InstructionParserAgent()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    runtime_config = config_storage.load_model_config()
    return HealthResponse(
        status="ok",
        backend="running",
        version="v0.2.0-dev",
        storage_dir=str(storage.settings.storage_path),
        llm_configured=runtime_config.llm_provider == "mock" or bool(runtime_config.llm_api_key),
        vision_configured=(not runtime_config.enable_vision)
        or runtime_config.vision_provider == "mock"
        or bool(runtime_config.vision_api_key),
    )


@router.post("/papers/upload", response_model=UploadResponse)
async def upload_paper(
    file: UploadFile = File(...),
    profile_id: str | None = Form(default=None),
    deck_mode: str = Form(default="reading_group"),
    long_instruction: str = Form(default=""),
    language: str = Form(default="zh"),
    audience: str = Form(default="graduate"),
    slide_count: int = Form(default=10),
    include_speaker_notes: bool = Form(default=True),
    include_source_footers: bool = Form(default=True),
    theme: str = Form(default="academic_clean"),
) -> UploadResponse:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="仅支持上传 PDF 文件。")

    pdf_bytes = await file.read()
    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="上传的 PDF 为空。")

    runtime_config = config_storage.load_model_config()
    if runtime_config.llm_provider != "mock" and not runtime_config.llm_api_key:
        raise HTTPException(
            status_code=400,
            detail="请先在模型配置中填写 API Key，或切换到 Mock 模式进行流程测试。",
        )

    settings = GenerationSettings(
        language=language,
        audience=audience,
        slide_count=slide_count,
        include_speaker_notes=include_speaker_notes,
        include_source_footers=include_source_footers,
        theme=theme,
        long_instruction=long_instruction,
    )
    profile = None
    parsed_instruction = None
    if profile_id:
        try:
            profile = profile_storage.get_profile(profile_id)
            settings = profile_to_settings(profile)
            settings.long_instruction = long_instruction
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail="未找到指定的配置档。") from exc

    if long_instruction:
        try:
            parsed_instruction = instruction_parser.run(
                LongInstructionInput(raw_text=long_instruction, language_hint=language)
            )
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"长需求解析失败：{exc}") from exc

    try:
        job = pipeline.run(
            pdf_bytes,
            file.filename,
            settings,
            profile=profile or build_inline_profile("Inline Profile", settings),
            deck_mode=deck_mode,
            parsed_instruction=parsed_instruction,
        )
    except ValueError as exc:
        message = str(exc).strip() or "已拦截低质量 PPT，请查看 quality_report.json。"
        if "quality_report" in message or "PPT" in message:
            message = "已拦截低质量 PPT，请查看 quality_report.json。"
        raise HTTPException(status_code=422, detail=message) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"生成流程失败：{exc}") from exc

    return UploadResponse(
        job=job,
        parsed_paper=storage.load_json_artifact(job.job_id, "parsed_paper.json"),
        paper_summary=storage.load_json_artifact(job.job_id, "paper_summary.json"),
        artifacts_url=f"/api/decks/{job.deck_id}/artifacts",
        download_url=f"/api/decks/{job.deck_id}/download",
    )


@router.get("/jobs/{job_id}")
def get_job(job_id: str):
    try:
        return pipeline.get_job_status(job_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="未找到任务。") from exc


@router.get("/decks/{deck_id}/artifacts")
def get_artifacts(deck_id: str):
    job_dir = storage.peek_job_dir(deck_id)
    if not job_dir.exists():
        raise HTTPException(status_code=404, detail="未找到该 deck。")
    status = pipeline.get_job_status(deck_id)
    return {
        "deck_id": deck_id,
        "artifacts": storage.list_artifacts(deck_id),
        "deck_status": status.status,
        "delivery_ready": status.delivery_ready,
        "mock_mode": status.mock_mode,
        "quality_status": status.quality_status,
        "download_artifact_name": status.download_artifact_name,
        "grounding_status": status.grounding_warning_count,
        "critic_approval_status": status.critic_approved,
    }


@router.get("/decks/{deck_id}/artifacts/{artifact_name}")
def download_artifact(deck_id: str, artifact_name: str):
    artifact_path = storage.get_artifact_path(deck_id, artifact_name)
    if not artifact_path.exists():
        raise HTTPException(status_code=404, detail="未找到该产物。")
    return FileResponse(path=artifact_path, filename=artifact_name)


@router.get("/decks/{deck_id}/download")
def download_deck(deck_id: str):
    final_path = storage.get_artifact_path(deck_id, "final_deck.pptx")
    draft_path = storage.get_artifact_path(deck_id, "draft_deck.pptx")
    pptx_path = final_path if final_path.exists() else draft_path
    if not pptx_path.exists():
        raise HTTPException(status_code=404, detail="未找到可下载的 PPT 文件。")
    return FileResponse(
        path=pptx_path,
        filename=pptx_path.name,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
    )


@router.get("/profiles", response_model=ProfilesResponse)
def list_profiles() -> ProfilesResponse:
    return ProfilesResponse(profiles=profile_storage.list_profiles())


@router.post("/profiles", response_model=UserProfile)
def create_profile(payload: CreateProfileRequest) -> UserProfile:
    return profile_storage.create_profile(payload)


@router.get("/profiles/{profile_id}", response_model=UserProfile)
def get_profile(profile_id: str) -> UserProfile:
    try:
        return profile_storage.get_profile(profile_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="未找到该配置档。") from exc


@router.put("/profiles/{profile_id}", response_model=UserProfile)
def update_profile(profile_id: str, payload: CreateProfileRequest) -> UserProfile:
    profile = UserProfile(id=profile_id, **payload.model_dump())
    return profile_storage.save_profile(profile)


@router.delete("/profiles/{profile_id}")
def delete_profile(profile_id: str):
    profile_storage.delete_profile(profile_id)
    return {"deleted": True, "profile_id": profile_id}


@router.post("/decks/{deck_id}/regenerate-slide")
def regenerate_slide(deck_id: str, payload: RegenerateSlideRequest = Body(...)):
    profile = None
    if payload.profile_id:
        try:
            profile = profile_storage.get_profile(payload.profile_id)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail="未找到指定的配置档。") from exc
    try:
        job = pipeline.regenerate_slides(
            deck_id,
            payload.slide_ids,
            payload.instruction,
            profile=profile,
            long_instruction=payload.long_instruction,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="缺少 deck 相关产物。") from exc
    except ValueError as exc:
        message = str(exc).strip() or "已拦截低质量 PPT，请查看 quality_report.json。"
        if "quality_report" in message or "PPT" in message:
            message = "已拦截低质量 PPT，请查看 quality_report.json。"
        raise HTTPException(status_code=422, detail=message) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"精修失败：{exc}") from exc
    return {
        "job": job,
        "download_url": f"/api/decks/{deck_id}/download",
        "artifacts_url": f"/api/decks/{deck_id}/artifacts",
    }


@router.get("/config/model", response_model=RuntimeModelConfigView)
def get_model_config() -> RuntimeModelConfigView:
    config = config_storage.load_model_config()
    return RuntimeModelConfigView(
        llm_provider=config.llm_provider,
        llm_base_url=config.llm_base_url,
        llm_api_key_masked=_mask_key(config.llm_api_key),
        llm_model=config.llm_model,
        fallback_llm_model=config.fallback_llm_model,
        vision_provider=config.vision_provider,
        vision_base_url=config.vision_base_url,
        vision_api_key_masked=_mask_key(config.vision_api_key),
        vision_model=config.vision_model,
        enable_vision=config.enable_vision,
        enable_critic=config.enable_critic,
        enable_repair=config.enable_repair,
        max_repair_loops=config.max_repair_loops,
        reasoning_effort=config.reasoning_effort,
        verbosity=config.verbosity,
        temperature=config.temperature,
        patch_mode=config.patch_mode,
        revision_max_output_tokens=config.revision_max_output_tokens,
        normal_max_output_tokens=config.normal_max_output_tokens,
        output_dir=config.output_dir,
        skills_enabled=config.skills_enabled,
        auto_select_skills=config.auto_select_skills,
        max_skills_per_task=config.max_skills_per_task,
        max_skill_context_tokens=config.max_skill_context_tokens,
        allow_skill_scripts=config.allow_skill_scripts,
        allowed_skill_risk_level=config.allowed_skill_risk_level,
    )


@router.post("/config/model", response_model=RuntimeModelConfigView)
def save_model_config(payload: RuntimeModelConfig) -> RuntimeModelConfigView:
    config_storage.save_model_config(payload)
    return get_model_config()


@router.post("/config/model/test", response_model=ModelTestResponse)
def test_model_config(payload: RuntimeModelConfig) -> ModelTestResponse:
    if payload.llm_provider == "mock":
        return ModelTestResponse(
            success=True,
            message="Mock 模式可用，仅用于流程测试。",
            llm_ok=True,
            vision_ok=(not payload.enable_vision) or payload.vision_provider == "mock",
        )
    if not payload.llm_api_key:
        return ModelTestResponse(
            success=False,
            message="请先填写 API Key 后再进行正式生成。",
            llm_ok=False,
            vision_ok=False,
        )
    fallback_note = ""
    if payload.llm_model == "gpt-5.5":
        fallback_note = f" 若当前运行时不支持 gpt-5.5，将回退到 {payload.fallback_llm_model}。"
    has_llm = bool(payload.llm_base_url and payload.llm_model)
    has_vision = (not payload.enable_vision) or payload.vision_provider == "mock" or bool(
        payload.vision_base_url and payload.vision_model
    )
    return ModelTestResponse(
        success=has_llm,
        message=f"模型配置已保存，基础字段看起来有效。{fallback_note}" if has_llm else "模型配置缺少 base URL 或 model。",
        llm_ok=has_llm,
        vision_ok=has_vision,
    )


@router.post("/instructions/parse")
def parse_instruction(payload: LongInstructionInput):
    return instruction_parser.run(payload)


@router.get("/prompt-templates", response_model=PromptTemplatesResponse)
def list_prompt_templates() -> PromptTemplatesResponse:
    return PromptTemplatesResponse(templates=config_storage.load_prompt_templates())


@router.post("/prompt-templates", response_model=PromptTemplate)
def create_prompt_template(payload: PromptTemplate) -> PromptTemplate:
    return config_storage.upsert_prompt_template(payload)


@router.put("/prompt-templates/{template_id}", response_model=PromptTemplate)
def update_prompt_template(template_id: str, payload: PromptTemplate) -> PromptTemplate:
    template = payload.model_copy(update={"id": template_id})
    return config_storage.upsert_prompt_template(template)


@router.delete("/prompt-templates/{template_id}")
def delete_prompt_template(template_id: str):
    config_storage.delete_prompt_template(template_id)
    return {"deleted": True, "template_id": template_id}


@router.get("/skills", response_model=SkillsResponse)
def list_skills() -> SkillsResponse:
    return SkillsResponse(skills=skill_storage.list_skills())


@router.get("/skills/{skill_id}")
def get_skill(skill_id: str):
    try:
        return skill_storage.get_skill(skill_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="未找到该技能。") from exc


@router.post("/skills/search", response_model=SkillSearchResponse)
def search_skills(payload: SkillSearchRequest):
    from app.skills.search import MockSkillSearchProvider

    results = MockSkillSearchProvider().search(payload)
    return SkillSearchResponse(query=payload, results=results)


@router.post("/skills/import", response_model=SkillImportResponse)
async def import_skill(
    file: UploadFile | None = File(default=None),
    folder_path: str = Form(default=""),
    source_url: str = Form(default=""),
    github_repo: str = Form(default=""),
    preview_only: bool = Form(default=False),
    allow_overwrite: bool = Form(default=False),
):
    try:
        if file is not None:
            import tempfile

            suffix = Path(file.filename or "skill.zip").suffix or ".zip"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as handle:
                handle.write(await file.read())
                temp_path = Path(handle.name)
            return skill_storage.import_from_zip(
                temp_path,
                allow_overwrite=allow_overwrite,
                preview_only=preview_only,
            )
        if folder_path.strip():
            return skill_storage.import_from_folder(
                Path(folder_path.strip()),
                source="folder",
                allow_overwrite=allow_overwrite,
                preview_only=preview_only,
            )
        if source_url.strip():
            return skill_storage.import_from_url(source_url.strip(), preview_only=preview_only)
        if github_repo.strip():
            return skill_storage.import_from_url(github_repo.strip(), preview_only=preview_only)
        raise HTTPException(status_code=400, detail="请提供 zip、文件夹路径、URL 或 GitHub 仓库地址。")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"技能导入失败：{exc}") from exc


@router.post("/skills/{skill_id}/enable")
def enable_skill(skill_id: str):
    try:
        return skill_storage.enable_skill(skill_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="未找到该技能。") from exc


@router.post("/skills/{skill_id}/disable")
def disable_skill(skill_id: str):
    try:
        return skill_storage.disable_skill(skill_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="未找到该技能。") from exc


@router.delete("/skills/{skill_id}")
def delete_skill(skill_id: str):
    skill_storage.delete_skill(skill_id)
    return {"deleted": True, "skill_id": skill_id}


@router.post("/skills/{skill_id}/test", response_model=SkillTestResponse)
def test_skill(skill_id: str):
    try:
        return skill_storage.test_skill(skill_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="未找到该技能。") from exc


@router.get("/usage/summary", response_model=UsageSummaryResponse)
def get_usage_summary() -> UsageSummaryResponse:
    return UsageSummaryResponse(summary=usage_storage.summary())


@router.get("/usage/tasks")
def get_usage_tasks():
    return {"tasks": [task.model_dump() for task in usage_storage.tasks()]}


@router.get("/usage/tasks/{task_id}", response_model=UsageTaskResponse)
def get_usage_task(task_id: str) -> UsageTaskResponse:
    try:
        return UsageTaskResponse(task=usage_storage.task_detail(task_id))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="未找到该任务的 Token 统计。") from exc


@router.get("/usage/export.csv")
def export_usage_csv():
    path = usage_storage.export_csv(usage_storage.root / "usage_export.csv")
    return FileResponse(path=path, filename=path.name, media_type="text/csv")


@router.get("/usage/export.json")
def export_usage_json():
    path = usage_storage.export_json(usage_storage.root / "usage_export.json")
    return FileResponse(path=path, filename=path.name, media_type="application/json")


@router.delete("/usage")
def clear_usage():
    usage_storage.clear()
    return {"deleted": True}


def _mask_key(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:3]}-****{value[-4:]}"
