from pydantic import BaseModel, Field

from app.schemas.common import AudienceOption, LanguageOption, MathLevelOption, PresentationGoalOption, ThemeOption, ToneOption


class UserProfile(BaseModel):
    id: str
    name: str
    audience: AudienceOption
    presentation_goal: PresentationGoalOption
    preferred_language: LanguageOption
    tone: ToneOption
    slide_count_target: int = Field(ge=5, le=40)
    talk_duration_minutes: int = Field(ge=3, le=120)
    math_level: MathLevelOption
    include_speaker_notes: bool = True
    include_limitations: bool = True
    include_discussion_questions: bool = True
    include_source_footers: bool = True
    theme_id: ThemeOption = "academic_clean"
    brand_colors: list[str] = Field(default_factory=list)
    title_font: str = "Aptos Display"
    body_font: str = "Aptos"
    custom_instructions: str = ""
    long_generation_instruction: str = ""


class CreateProfileRequest(BaseModel):
    name: str
    audience: AudienceOption = "graduate"
    presentation_goal: PresentationGoalOption = "summarize"
    preferred_language: LanguageOption = "en"
    tone: ToneOption = "academic"
    slide_count_target: int = 12
    talk_duration_minutes: int = 12
    math_level: MathLevelOption = "balanced"
    include_speaker_notes: bool = True
    include_limitations: bool = True
    include_discussion_questions: bool = True
    include_source_footers: bool = True
    theme_id: ThemeOption = "academic_clean"
    brand_colors: list[str] = Field(default_factory=list)
    title_font: str = "Aptos Display"
    body_font: str = "Aptos"
    custom_instructions: str = ""
    long_generation_instruction: str = ""
