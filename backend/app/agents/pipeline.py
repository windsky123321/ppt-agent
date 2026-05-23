from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from app.agents.critic_agent import CriticAgent
from app.agents.deck_planner_agent import DeckPlannerAgent
from app.agents.grounding_checker import GroundingChecker
from app.agents.instruction_parser_agent import InstructionParserAgent
from app.agents.paper_summary_agent import PaperSummaryAgent
from app.agents.pipeline_models import PipelineArtifacts
from app.agents.regenerate_slide_agent import RegenerateSlideAgent
from app.agents.repair_agent import RepairAgent
from app.agents.slide_writer_agent import SlideWriterAgent
from app.config import get_settings
from app.llm.providers import MockLLMProvider, create_llm_provider
from app.parser.asset_extractor import AssetExtractor
from app.parser.pdf_parser import PDFParser
from app.ppt.ppt_builder import PPTBuilder
from app.schemas.assets import ExtractedAssets
from app.schemas.common import GenerationSettings
from app.schemas.deck import DeckPlan, JobStatus, PaperSummary, SlideDrafts
from app.schemas.instructions import LongInstructionInput, ParsedInstructionSpec, PromptMergeReport
from app.schemas.paper import ParsedPaper
from app.schemas.profile import UserProfile
from app.schemas.runtime_config import RuntimeModelConfig
from app.storage.config_storage import ConfigStorage
from app.storage.file_storage import FileStorage
from app.storage.profile_storage import ProfileStorage
from app.utils.instruction_utils import merge_profile_with_instruction
from app.utils.profile_utils import build_inline_profile, default_profiles, profile_to_settings


class PaperToPPTPipeline:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.storage = FileStorage()
        self.config_storage = ConfigStorage()
        self.profile_storage = ProfileStorage()
        self.parser = PDFParser()
        self.asset_extractor = AssetExtractor()
        self.ppt_builder = PPTBuilder()
        self.critic = CriticAgent()
        self.repair = RepairAgent()
        self.regenerator = RegenerateSlideAgent(SlideWriterAgent(create_llm_provider()))
        self.instruction_parser = InstructionParserAgent()
        self._ensure_default_profiles()

    def run(self, pdf_bytes: bytes, original_filename: str, settings: GenerationSettings, profile: UserProfile | None = None, deck_mode: str = "Reading Group", parsed_instruction: ParsedInstructionSpec | None = None) -> JobStatus:
        job_id = f"job_{uuid4().hex[:12]}"
        deck_id = job_id
        paper_id = job_id
        active_profile = profile or build_inline_profile("Inline Profile", settings)
        if settings.long_instruction and parsed_instruction is None:
            parsed_instruction = self.instruction_parser.run(LongInstructionInput(raw_text=settings.long_instruction))
        merge_report = PromptMergeReport()
        if parsed_instruction:
            settings, merge_report = merge_profile_with_instruction(active_profile, settings, parsed_instruction, deck_mode)
        status = JobStatus(job_id=job_id, status="processing", paper_id=paper_id, deck_id=deck_id, message="Starting pipeline", profile_id=active_profile.id)
        self.storage.save_job_status(status)
        self.storage.touch_job_stage(job_id, "Uploading", "Saving uploaded PDF", active_profile.id)
        if settings.long_instruction:
            self.storage.save_text_artifact(job_id, "user_instruction_raw.md", settings.long_instruction)
        if parsed_instruction:
            self.storage.save_json_artifact(job_id, "user_instruction_spec.json", parsed_instruction.model_dump())
            self.storage.save_json_artifact(job_id, "prompt_merge_report.json", merge_report.model_dump())
        self.storage.save_json_artifact(job_id, "merged_generation_config.json", settings.model_dump())

        pdf_path = self.storage.save_bytes(job_id, "original.pdf", pdf_bytes)

        self.storage.touch_job_stage(job_id, "Parsing paper", "Parsing PDF into structured paper", active_profile.id)
        parsed_paper = self.parser.parse(pdf_path, paper_id=paper_id)
        self.storage.save_json_artifact(job_id, "parsed_paper.json", parsed_paper.model_dump())

        runtime_config = self.config_storage.load_model_config()
        llm = create_llm_provider(parsed_paper, runtime_config=runtime_config)
        if isinstance(llm, MockLLMProvider):
            llm.bind_paper(parsed_paper)

        self.storage.touch_job_stage(job_id, "Extracting figures and tables", "Extracting multimodal assets", active_profile.id)
        extracted_assets = self.asset_extractor.extract(pdf_path, parsed_paper, self.storage.get_job_dir(job_id))
        self.storage.save_json_artifact(job_id, "extracted_assets.json", extracted_assets.model_dump())

        if settings.long_instruction:
            self.storage.touch_job_stage(job_id, "Parsing long instruction", "Parsing long-form user requirement", active_profile.id)
            self.storage.touch_job_stage(job_id, "Merging profile and instruction", "Applying instruction overrides safely", active_profile.id)
        self.storage.touch_job_stage(job_id, "Summarizing paper", "Creating grounded paper summary", active_profile.id)
        summary = PaperSummaryAgent(llm).run(parsed_paper)
        self.storage.save_json_artifact(job_id, "paper_summary.json", summary.model_dump())

        self.storage.touch_job_stage(job_id, "Planning deck", "Planning deck structure from profile and paper", active_profile.id)
        plan = DeckPlannerAgent(llm).run(parsed_paper, summary, settings, active_profile, extracted_assets)
        self.storage.save_json_artifact(job_id, "deck_plan.json", plan.model_dump())

        self.storage.touch_job_stage(job_id, "Writing slides", "Writing grounded slide drafts", active_profile.id)
        drafts = SlideWriterAgent(llm).run(parsed_paper, summary, plan, active_profile, extracted_assets)
        self.storage.save_json_artifact(job_id, "slide_drafts.json", drafts.model_dump())

        self.storage.touch_job_stage(job_id, "Checking grounding", "Running grounding checker", active_profile.id)
        grounding_report = GroundingChecker().run(drafts)
        self.storage.save_json_artifact(job_id, "grounding_report.json", grounding_report.model_dump())

        critic_report = None
        repair_history = None
        if self.settings.enable_critic:
            self.storage.touch_job_stage(job_id, "Running critic", "Critiquing deck quality", active_profile.id)
            critic_report = self.critic.run(drafts, grounding_report, active_profile)
            self.storage.save_json_artifact(job_id, "critic_report.json", critic_report.model_dump())
        if self.settings.enable_repair and critic_report and critic_report.issues:
            self.storage.touch_job_stage(job_id, "Repairing issues", "Applying deterministic slide repairs", active_profile.id)
            drafts, repair_history = self.repair.run(parsed_paper, drafts, critic_report, active_profile, extracted_assets, self.settings.max_repair_loops)
            self.storage.save_json_artifact(job_id, "slide_drafts.json", drafts.model_dump())
            self.storage.save_json_artifact(job_id, "repair_history.json", repair_history.model_dump())
            grounding_report = GroundingChecker().run(drafts)
            self.storage.save_json_artifact(job_id, "grounding_report.json", grounding_report.model_dump())
            critic_report = self.critic.run(drafts, grounding_report, active_profile)
            self.storage.save_json_artifact(job_id, "critic_report.json", critic_report.model_dump())

        self.storage.touch_job_stage(job_id, "Building PPTX", "Building editable PowerPoint", active_profile.id)
        output_path = self.storage.get_artifact_path(job_id, "final_deck.pptx")
        self.ppt_builder.build(output_path, summary, plan, drafts, settings)

        complete = JobStatus(
            job_id=job_id,
            status="completed",
            paper_id=paper_id,
            deck_id=deck_id,
            message=f"Generated deck for {original_filename}",
            artifacts=self.storage.list_artifacts(job_id),
            profile_id=active_profile.id,
            current_stage="Complete",
            critic_approved=critic_report.approved if critic_report else None,
            grounding_warning_count=len(grounding_report.warnings),
        )
        self.storage.save_job_status(complete)
        return complete

    def get_job_status(self, job_id: str) -> JobStatus:
        status = self.storage.load_job_status(job_id)
        status.artifacts = self.storage.list_artifacts(job_id)
        return status

    def regenerate_slides(self, deck_id: str, slide_ids: list[str], instruction: str, profile: UserProfile | None = None, long_instruction: str = "") -> JobStatus:
        parsed_paper = self.storage.load_json_artifact(deck_id, "parsed_paper.json")
        extracted_assets = self.storage.load_json_artifact(deck_id, "extracted_assets.json")
        paper_summary = self.storage.load_json_artifact(deck_id, "paper_summary.json")
        deck_plan = self.storage.load_json_artifact(deck_id, "deck_plan.json")
        slide_drafts = self.storage.load_json_artifact(deck_id, "slide_drafts.json")
        merged_generation_config = self.storage.load_json_artifact(deck_id, "merged_generation_config.json")
        current_status = self.storage.load_job_status(deck_id)
        active_profile = profile or self._resolve_profile(current_status.profile_id) or build_inline_profile("Inline Profile", GenerationSettings())
        if long_instruction:
            parsed_spec = self.instruction_parser.run(LongInstructionInput(raw_text=long_instruction))
            self.storage.save_text_artifact(deck_id, "user_instruction_raw.md", long_instruction)
            self.storage.save_json_artifact(deck_id, "user_instruction_spec.json", parsed_spec.model_dump())

        llm = create_llm_provider(runtime_config=self.config_storage.load_model_config())
        drafts_model = RegenerateSlideAgent(SlideWriterAgent(llm)).run(
            ParsedPaper(**parsed_paper),
            PaperSummary(**paper_summary),
            DeckPlan(**deck_plan),
            SlideDrafts(**slide_drafts),
            slide_ids,
            instruction,
            active_profile,
            ExtractedAssets(**extracted_assets),
        )
        self.storage.save_json_artifact(deck_id, "slide_drafts.json", drafts_model.model_dump())
        grounding_report = GroundingChecker().run(drafts_model)
        self.storage.save_json_artifact(deck_id, "grounding_report.json", grounding_report.model_dump())
        critic_report = self.critic.run(drafts_model, grounding_report, active_profile)
        self.storage.save_json_artifact(deck_id, "critic_report.json", critic_report.model_dump())
        output_path = self.storage.get_artifact_path(deck_id, "final_deck.pptx")
        self.ppt_builder.build(output_path, PaperSummary(**paper_summary), DeckPlan(**deck_plan), drafts_model, GenerationSettings(**merged_generation_config))
        current_status.artifacts = self.storage.list_artifacts(deck_id)
        current_status.message = f"Regenerated slides: {', '.join(slide_ids)}"
        current_status.critic_approved = critic_report.approved
        current_status.grounding_warning_count = len(grounding_report.warnings)
        self.storage.save_job_status(current_status)
        return current_status

    def _resolve_profile(self, profile_id: str | None) -> UserProfile | None:
        if not profile_id:
            return None
        try:
            return self.profile_storage.get_profile(profile_id)
        except Exception:
            return next((profile for profile in default_profiles() if profile.id == profile_id), None)

    def _ensure_default_profiles(self) -> None:
        existing_ids = {profile.id for profile in self.profile_storage.list_profiles()}
        for profile in default_profiles():
            if profile.id not in existing_ids:
                self.profile_storage.save_profile(profile)
