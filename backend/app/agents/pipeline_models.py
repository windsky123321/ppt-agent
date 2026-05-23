from pydantic import BaseModel

from app.schemas.assets import ExtractedAssets
from app.schemas.deck import CriticReport, DeckPlan, GroundingReport, JobStatus, PaperSummary, RepairHistory, SlideDrafts
from app.schemas.paper import ParsedPaper
from app.schemas.profile import UserProfile


class PipelineArtifacts(BaseModel):
    job: JobStatus
    profile: UserProfile
    parsed_paper: ParsedPaper
    extracted_assets: ExtractedAssets
    paper_summary: PaperSummary
    deck_plan: DeckPlan
    slide_drafts: SlideDrafts
    grounding_report: GroundingReport
    critic_report: CriticReport | None = None
    repair_history: RepairHistory | None = None
