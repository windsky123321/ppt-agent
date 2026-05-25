from pydantic import BaseModel, Field

from app.schemas.common import SourceRef


class PaperSummary(BaseModel):
    title: str
    one_sentence_summary: str
    problem: str
    motivation: str
    research_gap: str
    key_contributions: list[str] = Field(default_factory=list)
    method_overview: str
    experiment_setup: str
    main_results: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    discussion_points: list[str] = Field(default_factory=list)
    conclusion: str
    keywords: list[str] = Field(default_factory=list)


class DeckPlanSlide(BaseModel):
    slide_id: str
    slide_type: str
    title: str
    purpose: str
    key_section: str = ""
    asset_ids: list[str] = Field(default_factory=list)


class DeckPlan(BaseModel):
    deck_title: str
    target_audience: str
    language: str
    slide_count: int
    slides: list[DeckPlanSlide]


class VisualElement(BaseModel):
    type: str = "none"
    asset_id: str | None = None
    description: str = ""
    placement_hint: str = ""


class SlideDraft(BaseModel):
    slide_id: str
    slide_type: str = "content"
    title: str
    subtitle: str = ""
    purpose: str = ""
    key_message: str = ""
    bullets: list[str] = Field(default_factory=list)
    visual_elements: list[VisualElement] = Field(default_factory=list)
    speaker_notes: str = ""
    source_refs: list[SourceRef] = Field(default_factory=list)
    confidence: float = 0.6
    unsupported_claims: list[str] = Field(default_factory=list)


class SlideDrafts(BaseModel):
    slides: list[SlideDraft]


class GroundingWarning(BaseModel):
    slide_id: str
    severity: str
    message: str
    zh_message: str = ""


class GroundingReport(BaseModel):
    slide_count: int
    warnings: list[GroundingWarning] = Field(default_factory=list)


class ArtifactItem(BaseModel):
    name: str
    path: str
    exists: bool
    modified_time: float | None = None
    download_url: str | None = None


class JobStatus(BaseModel):
    job_id: str
    status: str
    paper_id: str
    deck_id: str
    message: str = ""
    artifacts: list[ArtifactItem] = Field(default_factory=list)
    profile_id: str | None = None
    current_stage: str = ""
    critic_approved: bool | None = None
    grounding_warning_count: int | None = None
    mock_mode: bool = False
    delivery_ready: bool = False
    quality_status: str = "pending"
    download_artifact_name: str = "final_deck.pptx"


class CriticIssue(BaseModel):
    slide_id: str
    severity: str
    category: str
    description: str
    zh_message: str = ""
    suggested_fix: str
    requires_regeneration: bool


class CriticReport(BaseModel):
    deck_score: int
    summary: str
    zh_summary: str = ""
    issues: list[CriticIssue] = Field(default_factory=list)
    approved: bool = False


class RepairHistoryItem(BaseModel):
    loop_index: int
    repaired_slide_ids: list[str] = Field(default_factory=list)
    issue_count_before: int = 0
    issue_count_after: int = 0
    notes: str = ""


class RepairHistory(BaseModel):
    loops: list[RepairHistoryItem] = Field(default_factory=list)


class QualityIssue(BaseModel):
    slide_id: str
    slide_title: str
    severity: str
    category: str
    message: str


class QualityReport(BaseModel):
    passed: bool = True
    blocked_export: bool = False
    issue_count: int = 0
    issues: list[QualityIssue] = Field(default_factory=list)
    low_confidence_notes: list[str] = Field(default_factory=list)
