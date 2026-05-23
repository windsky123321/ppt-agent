from pydantic import BaseModel, Field

from app.schemas.common import GenerationSettings
from app.schemas.deck import JobStatus
from app.schemas.instructions import LongInstructionInput, ParsedInstructionSpec
from app.schemas.paper import ParsedPaper
from app.schemas.prompt_template import PromptTemplate
from app.schemas.profile import CreateProfileRequest, UserProfile
from app.schemas.runtime_config import ModelTestResponse, RuntimeModelConfig, RuntimeModelConfigView


class UploadResponse(BaseModel):
    job: JobStatus
    parsed_paper: ParsedPaper
    artifacts_url: str
    download_url: str


class HealthResponse(BaseModel):
    status: str
    backend: str = "running"
    version: str = ""
    storage_dir: str = ""
    llm_configured: bool = False
    vision_configured: bool = False


class GenerateRequest(BaseModel):
    settings: GenerationSettings = GenerationSettings()


class UploadGenerationRequest(BaseModel):
    profile_id: str | None = None
    profile: UserProfile | CreateProfileRequest | None = None
    settings: GenerationSettings = Field(default_factory=GenerationSettings)
    deck_mode: str = "Reading Group"
    long_instruction: str = ""
    parsed_instruction: ParsedInstructionSpec | None = None


class RegenerateSlideRequest(BaseModel):
    slide_ids: list[str]
    instruction: str = ""
    long_instruction: str = ""
    profile_id: str | None = None


class ProfilesResponse(BaseModel):
    profiles: list[UserProfile]


class PromptTemplatesResponse(BaseModel):
    templates: list[PromptTemplate]
