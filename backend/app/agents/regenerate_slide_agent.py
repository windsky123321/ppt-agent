from __future__ import annotations

from app.agents.slide_writer_agent import SlideWriterAgent
from app.schemas.assets import ExtractedAssets
from app.schemas.deck import DeckPlan, SlideDrafts
from app.schemas.paper import ParsedPaper
from app.schemas.profile import UserProfile
from app.schemas.deck import PaperSummary


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
        regenerated = self.writer.run(paper, summary, plan)
        replacement_map = {slide.slide_id: slide for slide in regenerated.slides if slide.slide_id in slide_ids}
        for slide in drafts.slides:
            if slide.slide_id in replacement_map:
                new_slide = replacement_map[slide.slide_id]
                if instruction:
                    if "reduce text" in instruction.lower():
                        new_slide.bullets = new_slide.bullets[:3]
                    if "visual" in instruction.lower() and not new_slide.visual_elements and assets.assets:
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
