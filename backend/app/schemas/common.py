from typing import Literal

from pydantic import BaseModel, Field


LanguageOption = Literal["zh", "en", "bilingual"]
AudienceOption = Literal["general", "undergraduate", "graduate", "expert", "investor", "lab_meeting", "thesis_defense"]
ThemeOption = Literal["academic_clean", "dark_modern", "minimalist_white"]
PresentationGoalOption = Literal["summarize", "explain", "teach", "critique", "persuade", "compare"]
ToneOption = Literal["academic", "concise", "visual", "storytelling", "technical"]
MathLevelOption = Literal["simplified", "balanced", "detailed"]


class GenerationSettings(BaseModel):
    language: LanguageOption = "en"
    audience: AudienceOption = "graduate"
    slide_count: int = Field(default=10, ge=5, le=30)
    include_speaker_notes: bool = True
    include_source_footers: bool = True
    theme: ThemeOption = "academic_clean"
    presentation_goal: PresentationGoalOption = "summarize"
    tone: ToneOption = "academic"
    math_level: MathLevelOption = "balanced"
    include_limitations: bool = True
    include_discussion_questions: bool = True
    talk_duration_minutes: int = Field(default=12, ge=3, le=120)
    visual_density: str = "balanced"


class SourceRef(BaseModel):
    paper_id: str = ""
    page_number: int | None = None
    section_title: str = ""
    figure_or_table_id: str | None = None
    evidence_summary: str
