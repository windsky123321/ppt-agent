from pydantic import BaseModel, Field


class LongInstructionInput(BaseModel):
    raw_text: str
    language_hint: str = "auto"
    save_as_preset: bool = False
    preset_name: str | None = None


class ParsedInstructionSpec(BaseModel):
    detected_language: str = "en"
    audience: str | None = None
    presentation_goal: str | None = None
    preferred_language: str | None = None
    tone: str | None = None
    slide_count_target: int | None = None
    talk_duration_minutes: int | None = None
    math_level: str | None = None
    include_speaker_notes: bool | None = None
    include_limitations: bool | None = None
    include_discussion_questions: bool | None = None
    include_source_footers: bool | None = None
    visual_preference: str | None = None
    sections_to_emphasize: list[str] = Field(default_factory=list)
    sections_to_reduce: list[str] = Field(default_factory=list)
    must_include: list[str] = Field(default_factory=list)
    avoid: list[str] = Field(default_factory=list)
    style_requirements: list[str] = Field(default_factory=list)
    special_requests: list[str] = Field(default_factory=list)
    unclear_requirements: list[str] = Field(default_factory=list)
    conflict_warnings: list[str] = Field(default_factory=list)
    compressed_summary: str = ""


class PromptMergeReport(BaseModel):
    applied_overrides: list[str] = Field(default_factory=list)
    conflict_warnings: list[str] = Field(default_factory=list)
    compressed_instruction: bool = False
    instruction_length: int = 0
