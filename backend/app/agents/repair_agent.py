from __future__ import annotations

from app.schemas.assets import ExtractedAssets
from app.schemas.deck import CriticReport, RepairHistory, RepairHistoryItem, SlideDraft, SlideDrafts
from app.schemas.paper import ParsedPaper
from app.schemas.profile import UserProfile
from app.utils.paper_utils import build_section_map, make_source_refs
from app.utils.text_utils import safe_truncate


class RepairAgent:
    def run(
        self,
        paper: ParsedPaper,
        drafts: SlideDrafts,
        critic_report: CriticReport,
        profile: UserProfile,
        assets: ExtractedAssets,
        max_loops: int,
    ) -> tuple[SlideDrafts, RepairHistory]:
        section_map = build_section_map(paper)
        history = RepairHistory()
        current = drafts

        for loop_index in range(max_loops):
            repair_ids: list[str] = []
            before = len(critic_report.issues)
            for issue in critic_report.issues:
                slide = next((item for item in current.slides if item.slide_id == issue.slide_id), None)
                if not slide:
                    continue
                updated = self._repair_slide(slide, issue.category, section_map, profile, assets)
                if updated:
                    repair_ids.append(slide.slide_id)
            after = max(0, before - len(repair_ids))
            history.loops.append(
                RepairHistoryItem(
                    loop_index=loop_index + 1,
                    repaired_slide_ids=repair_ids,
                    issue_count_before=before,
                    issue_count_after=after,
                    notes="Applied deterministic repairs to flagged slides.",
                )
            )
            if not repair_ids:
                break
        return current, history

    def _repair_slide(self, slide: SlideDraft, category: str, section_map, profile: UserProfile, assets: ExtractedAssets) -> bool:
        changed = False
        if category == "content" and len(slide.bullets) > 5:
            slide.bullets = slide.bullets[:5]
            changed = True
        if category == "layout":
            slide.bullets = [safe_truncate(bullet, 110) for bullet in slide.bullets[:5]]
            changed = True
        if category == "speaker_notes" and profile.include_speaker_notes and not slide.speaker_notes:
            slide.speaker_notes = f"Explain the key message: {slide.key_message}"
            changed = True
        if category == "grounding" and not slide.source_refs:
            key = slide.slide_type if slide.slide_type in section_map else "introduction"
            slide.source_refs = make_source_refs(section_map.get(key, []) or section_map.get("introduction", []), max_refs=2)
            changed = bool(slide.source_refs)
        if slide.unsupported_claims:
            slide.unsupported_claims = []
            slide.bullets = [bullet for bullet in slide.bullets if "unsupported" not in bullet.lower()]
            changed = True
        if not slide.visual_elements and slide.slide_type in {"method", "result"} and assets.assets:
            ranked = next((asset for asset in assets.assets if asset.suggested_slide_usage in {slide.slide_type, "result", "method"}), None)
            if ranked:
                slide.visual_elements.append(
                    {
                        "type": ranked.asset_type,
                        "asset_id": ranked.id,
                        "description": ranked.short_visual_description,
                        "placement_hint": "right_panel",
                    }
                )
                changed = True
        return changed
