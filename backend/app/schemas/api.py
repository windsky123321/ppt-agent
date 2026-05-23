from pydantic import BaseModel, Field

from app.schemas.common import GenerationSettings
from app.schemas.deck import JobStatus
from app.schemas.paper import ParsedPaper
from app.schemas.profile import CreateProfileRequest, UserProfile


class UploadResponse(BaseModel):
    job: JobStatus
    parsed_paper: ParsedPaper
    artifacts_url: str
    download_url: str


class HealthResponse(BaseModel):
    status: str


class GenerateRequest(BaseModel):
    settings: GenerationSettings = GenerationSettings()


class UploadGenerationRequest(BaseModel):
    profile_id: str | None = None
    profile: UserProfile | CreateProfileRequest | None = None
    settings: GenerationSettings = Field(default_factory=GenerationSettings)


class RegenerateSlideRequest(BaseModel):
    slide_ids: list[str]
    instruction: str = ""
    profile_id: str | None = None


class ProfilesResponse(BaseModel):
    profiles: list[UserProfile]
