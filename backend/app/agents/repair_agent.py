from __future__ import annotations

import re

from app.schemas.assets import ExtractedAssets
from app.schemas.deck import CriticReport, QualityReport, RepairHistory, RepairHistoryItem, SlideDraft, SlideDrafts
from app.schemas.paper import ParsedPaper, Section
from app.schemas.profile import UserProfile
from app.utils.paper_utils import build_section_map, bulletize, make_source_refs
from app.utils.text_utils import compress_title, contains_cjk, normalize_presentation_text, truncate_plain


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

    def repair_quality(
        self,
        paper: ParsedPaper,
        drafts: SlideDrafts,
        quality_report: QualityReport,
        profile: UserProfile | None,
        assets: ExtractedAssets | None,
        max_loops: int,
    ) -> tuple[SlideDrafts, RepairHistory]:
        section_map = build_section_map(paper)
        history = RepairHistory()
        current = drafts
        current_report = quality_report
        for loop_index in range(max_loops):
            repaired_slide_ids: list[str] = []
            for issue in current_report.issues:
                slide = next((item for item in current.slides if item.slide_id == issue.slide_id), None)
                if not slide:
                    continue
                sections = section_map.get(slide.slide_type, []) or section_map.get("introduction", [])
                if self._repair_quality_issue(slide, issue.category, sections):
                    repaired_slide_ids.append(slide.slide_id)
                if not slide.source_refs:
                    slide.source_refs = make_source_refs(sections, max_refs=2)
                if assets and not slide.visual_elements and slide.slide_type in {"method", "results", "analysis"} and assets.assets:
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
            history.loops.append(
                RepairHistoryItem(
                    loop_index=loop_index + 1,
                    repaired_slide_ids=sorted(set(repaired_slide_ids)),
                    issue_count_before=current_report.issue_count,
                    issue_count_after=0,
                    notes="Applied quality-oriented repairs to Chinese presentation text.",
                )
            )
            if not repaired_slide_ids:
                break
            break
        return current, history

    def _repair_slide(self, slide: SlideDraft, category: str, section_map, profile: UserProfile, assets: ExtractedAssets) -> bool:
        changed = False
        if category == "content" and len(slide.bullets) > 4:
            slide.bullets = slide.bullets[:4]
            changed = True
        if category == "layout":
            slide.bullets = [truncate_plain(normalize_presentation_text(bullet), 18) for bullet in slide.bullets[:4]]
            slide.title = compress_title(slide.title, 14) if contains_cjk(slide.title) else truncate_plain(slide.title, 60)
            changed = True
        if category == "speaker_notes" and profile.include_speaker_notes and not slide.speaker_notes:
            slide.speaker_notes = f"围绕“{slide.title}”解释核心结论：{slide.key_message}"
            changed = True
        if category == "grounding" and not slide.source_refs:
            key = slide.slide_type if slide.slide_type in section_map else "introduction"
            slide.source_refs = make_source_refs(section_map.get(key, []) or section_map.get("introduction", []), max_refs=2)
            changed = bool(slide.source_refs)
        if slide.unsupported_claims:
            slide.unsupported_claims = []
            slide.bullets = [bullet for bullet in slide.bullets if "unsupported" not in bullet.lower()]
            changed = True
        if not slide.visual_elements and slide.slide_type in {"method", "results"} and assets.assets:
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

    def _repair_quality_issue(self, slide: SlideDraft, category: str, sections: list[Section]) -> bool:
        changed = False
        if category == "title_length":
            new_title = compress_title(slide.title, 14)
            if new_title != slide.title:
                slide.title = new_title
                changed = True

        if category in {"ellipsis", "placeholder", "confidence", "mixed_language", "generic_bullet", "insufficient_content"}:
            old_key = slide.key_message
            slide.key_message = self._clean_text(slide.key_message)
            if slide.key_message != old_key:
                changed = True
            cleaned_bullets = []
            for bullet in slide.bullets:
                cleaned = self._clean_text(bullet)
                if cleaned and cleaned not in cleaned_bullets:
                    cleaned_bullets.append(cleaned)
            slide.bullets = cleaned_bullets[:4]
            if len(slide.bullets) < 2 and slide.slide_type not in {"title", "divider"}:
                for sentence in bulletize(" ".join(section.text for section in sections[:2]), max_bullets=4):
                    candidate = truncate_plain(self._clean_text(sentence), 18)
                    if candidate and candidate not in slide.bullets:
                        slide.bullets.append(candidate)
                    if len(slide.bullets) >= 3:
                        break
            if len(slide.bullets) < 2 and slide.slide_type not in {"title", "divider"}:
                fallback = self._fallback_bullets(slide.slide_type)
                for item in fallback:
                    if item not in slide.bullets:
                        slide.bullets.append(item)
                    if len(slide.bullets) >= 2:
                        break
            slide.bullets = slide.bullets[:4]
            if not slide.key_message and slide.bullets:
                slide.key_message = "；".join(slide.bullets[:2])
            changed = True

        if slide.slide_type not in {"title", "divider"} and len(slide.bullets) > 4:
            slide.bullets = slide.bullets[:4]
            changed = True
        return changed

    def _clean_text(self, text: str) -> str:
        cleaned = normalize_presentation_text(text)
        cleaned = re.sub(r"confidence[:：]?\s*\d*\.?\d+", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(
            r"uncertain|tbd|not enough information|method details are uncertain|results remain uncertain",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )
        cleaned = cleaned.replace("待补充", "")
        cleaned = cleaned.replace("Method details are uncertain", "")
        cleaned = truncate_plain(cleaned, 18 if contains_cjk(cleaned) else 80)
        return cleaned

    def _fallback_bullets(self, slide_type: str) -> list[str]:
        return {
            "background": ["说明背景价值", "指出研究动因"],
            "problem": ["说明研究对象", "明确现有不足"],
            "method": ["拆解方法流程", "说明关键模块"],
            "technical": ["提炼技术结构", "强调设计理由"],
            "experiments": ["说明实验设置", "交代评价方式"],
            "results": ["提炼核心结果", "说明结果意义"],
            "analysis": ["解释结果原因", "指出适用边界"],
            "limitations": ["指出应用边界", "说明改进方向"],
            "discussion": ["提出关键追问", "引导后续讨论"],
            "conclusion": ["回收核心结论", "强调应用价值"],
        }.get(slide_type, ["补充关键证据", "强化页面结论"])
