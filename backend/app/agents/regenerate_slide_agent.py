from __future__ import annotations

from app.agents.slide_writer_agent import SlideWriterAgent
from app.schemas.assets import ExtractedAssets
from app.schemas.deck import DeckPlan, PaperSummary, SlideDrafts
from app.schemas.paper import ParsedPaper
from app.schemas.profile import UserProfile


class RegenerateSlideAgent:
    def __init__(self, writer: SlideWriterAgent) -> None:
        self.writer = writer

    def run(
        self,
        paper: ParsedPaper,
        summary: PaperSummary,
        plan: DeckPlan,
        drafts: SlideDrafts,
        slide_ids: list[str],
        instruction: str,
        profile: UserProfile,
        assets: ExtractedAssets,
    ) -> SlideDrafts:
        filtered_plan = plan.model_copy(update={"slides": [slide for slide in plan.slides if slide.slide_id in slide_ids]})
        regenerated = self.writer.run(paper, summary, filtered_plan, profile, assets)
        replacement_map = {slide.slide_id: slide for slide in regenerated.slides if slide.slide_id in slide_ids}
        lowered = instruction.lower()
        patch_mode = any(token in lowered for token in ["update", "revise", "patch", "reduce text", "visual"]) or any(
            token in instruction for token in ["第", "继续优化", "修改", "精修", "调整", "只改"]
        )
        for slide in drafts.slides:
            if slide.slide_id in replacement_map:
                new_slide = replacement_map[slide.slide_id]
                if patch_mode:
                    new_slide.bullets = new_slide.bullets[:3]
                if ("title" in lowered or "标题" in instruction) and new_slide.title:
                    new_slide.title = self.writer._format_title(new_slide.title, profile.preferred_language == "zh")
                if "visual" in lowered and not new_slide.visual_elements and assets and assets.assets:
                    asset = assets.assets[0]
                    new_slide.visual_elements.append(
                        {
                            "type": asset.asset_type,
                            "asset_id": asset.id,
                            "description": asset.short_visual_description,
                            "placement_hint": "right_panel",
                        }
                    )
                slide.title = new_slide.title
                slide.purpose = new_slide.purpose
                slide.key_message = new_slide.key_message
                slide.bullets = new_slide.bullets
                slide.visual_elements = new_slide.visual_elements
                slide.speaker_notes = new_slide.speaker_notes
                slide.source_refs = new_slide.source_refs
                slide.confidence = new_slide.confidence
                slide.unsupported_claims = new_slide.unsupported_claims
        return drafts
