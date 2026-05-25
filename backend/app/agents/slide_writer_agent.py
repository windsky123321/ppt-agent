import json
import re

from app.llm.providers import BaseLLMProvider
from app.prompts.templates import SLIDE_WRITER_PROMPT
from app.schemas.assets import ExtractedAssets
from app.schemas.deck import DeckPlan, PaperSummary, SlideDraft, SlideDrafts
from app.schemas.paper import ParsedPaper, Section
from app.schemas.profile import UserProfile
from app.utils.paper_utils import build_section_map, bulletize, make_source_refs, pick_primary_text
from app.utils.text_utils import compress_title, contains_cjk, normalize_presentation_text, truncate_plain


class SlideWriterAgent:
    TITLE_MAP = {
        "title": "论文汇报",
        "divider": "章节过渡",
        "takeaway": "核心结论",
        "background": "研究背景",
        "problem": "问题定义",
        "contributions": "论文贡献",
        "method": "方法概览",
        "technical": "技术细节",
        "experiments": "实验设计",
        "results": "实验结果",
        "analysis": "结果分析",
        "strengths": "论文优势",
        "limitations": "研究局限",
        "discussion": "讨论问题",
        "conclusion": "总结结论",
        "backup": "补充证据",
    }

    def __init__(self, llm: BaseLLMProvider) -> None:
        self.llm = llm

    def run(
        self,
        paper: ParsedPaper,
        summary: PaperSummary,
        plan: DeckPlan,
        profile: UserProfile | None = None,
        assets: ExtractedAssets | None = None,
    ) -> SlideDrafts:
        if self.llm.__class__.__name__ == "MockLLMProvider":
            return self._run_heuristic(paper, summary, plan, profile, assets)
        payload = {
            "parsed_paper": paper.model_dump(),
            "paper_summary": summary.model_dump(),
            "deck_plan": plan.model_dump(),
        }
        prompt = f"{SLIDE_WRITER_PROMPT}\nSchema: slide_drafts\n{json.dumps(payload, ensure_ascii=False)}"
        data = self.llm.generate_json(prompt, "slide_drafts")
        return SlideDrafts(**data)

    def _run_heuristic(
        self,
        paper: ParsedPaper,
        summary: PaperSummary,
        plan: DeckPlan,
        profile: UserProfile | None,
        assets: ExtractedAssets | None,
    ) -> SlideDrafts:
        section_map = build_section_map(paper)
        drafts: list[SlideDraft] = []
        for slide in plan.slides:
            draft = self._build_slide(
                slide.slide_type,
                slide.title,
                slide.key_section,
                paper,
                summary,
                section_map,
                slide.asset_ids,
                assets,
                profile,
            )
            draft.slide_id = slide.slide_id
            draft.slide_type = slide.slide_type
            draft.purpose = slide.purpose or draft.purpose
            drafts.append(draft)
        return SlideDrafts(slides=drafts)

    def _build_slide(
        self,
        slide_type: str,
        title: str,
        key_section: str,
        paper: ParsedPaper,
        summary: PaperSummary,
        section_map: dict[str, list[Section]],
        asset_ids: list[str],
        assets: ExtractedAssets | None,
        profile: UserProfile | None,
    ) -> SlideDraft:
        ranked_assets = {asset.id: asset for asset in (assets.assets if assets else [])}
        profile_instruction = " ".join(
            [profile.custom_instructions if profile else "", profile.long_generation_instruction if profile else ""]
        ).strip()
        concise_requested = (
            bool(profile and profile.tone == "concise")
            or "reduce text" in profile_instruction.lower()
            or "精炼" in profile_instruction
            or "简洁" in profile_instruction
        )
        visual_requested = (
            bool(profile and profile.tone == "visual")
            or "visual" in profile_instruction.lower()
            or "图" in profile_instruction
            or "表" in profile_instruction
        )
        chinese_mode = True if profile is None else profile.preferred_language != "en"

        visual_elements = []
        for asset_id in asset_ids[:1]:
            asset = ranked_assets.get(asset_id)
            if asset:
                visual_elements.append(
                    {
                        "type": asset.asset_type,
                        "asset_id": asset.id,
                        "description": asset.short_visual_description or asset.original_caption,
                        "placement_hint": "right_panel"
                        if slide_type in {"method", "technical", "results", "analysis", "backup"}
                        else "footer_callout",
                    }
                )

        if slide_type == "title":
            return SlideDraft(
                slide_id="",
                slide_type=slide_type,
                title=self._title_slide_title(paper.title, summary),
                subtitle="、".join(paper.authors[:4]) or "论文汇报",
                purpose="介绍论文主题与汇报重点。",
                key_message=truncate_plain(summary.one_sentence_summary, 80),
                bullets=[],
                speaker_notes=self._maybe_notes(profile, f"开场说明论文主题、作者与核心结论：{summary.one_sentence_summary}"),
                confidence=0.95,
            )

        if slide_type == "divider":
            return SlideDraft(
                slide_id="",
                slide_type=slide_type,
                title=self._format_title(title, chinese_mode),
                subtitle="从问题背景过渡到核心方法",
                purpose="承接上一部分并进入下一主题。",
                key_message="下面开始聚焦论文的核心方法、证据与结论。",
                bullets=[],
                speaker_notes=self._maybe_notes(profile, "这一页只做过渡，提醒听众接下来进入关键方法与结果。"),
                confidence=0.9,
            )

        if slide_type == "backup":
            source_refs = make_source_refs(section_map.get("results", []) or section_map.get("method", []), max_refs=2)
            return SlideDraft(
                slide_id="",
                slide_type=slide_type,
                title="补充证据",
                subtitle="答疑时按需展开",
                purpose="保留可追溯的补充证据。",
                key_message="仅在答疑或追问时展示，补充结果或方法细节。",
                bullets=self._ensure_meaningful_bullets(
                    self._compact_bullets(
                        bulletize(
                            pick_primary_text(section_map, "results", fallback=pick_primary_text(section_map, "method")),
                            max_bullets=4,
                        ),
                        chinese_mode,
                    ),
                    section_map.get("results", []) or section_map.get("method", []),
                    slide_type,
                ),
                visual_elements=visual_elements,
                speaker_notes=self._maybe_notes(profile, "仅在需要补充原文证据时展示这一页。"),
                source_refs=source_refs,
                confidence=0.8 if source_refs else 0.5,
            )

        content_map = {
            "takeaway": (
                summary.one_sentence_summary,
                [
                    summary.problem,
                    summary.method_overview,
                    summary.main_results[0] if summary.main_results else "结果信息有限，需回到原文结果章节核对。",
                ],
                section_map.get("abstract", []) or section_map.get("introduction", []),
            ),
            "background": (
                summary.motivation,
                bulletize(
                    pick_primary_text(section_map, "background", fallback=pick_primary_text(section_map, "introduction")),
                    max_bullets=4,
                ),
                section_map.get("background", []) or section_map.get("introduction", []),
            ),
            "problem": (
                summary.problem,
                [summary.problem, summary.research_gap, "先说清研究对象、业务场景与评价目标。"],
                section_map.get("problem", []) or section_map.get("introduction", []),
            ),
            "contributions": (
                "论文贡献应围绕方法、结果与应用价值来概括。",
                summary.key_contributions[:4],
                section_map.get("method", []) or section_map.get("conclusion", []),
            ),
            "method": (
                summary.method_overview,
                bulletize(pick_primary_text(section_map, "method"), max_bullets=4),
                section_map.get("method", []),
            ),
            "technical": (
                summary.method_overview,
                bulletize(
                    pick_primary_text(section_map, "technical", fallback=pick_primary_text(section_map, "method")),
                    max_bullets=4,
                ),
                section_map.get("technical", []) or section_map.get("method", []),
            ),
            "experiments": (
                summary.experiment_setup,
                bulletize(pick_primary_text(section_map, "experiments"), max_bullets=4),
                section_map.get("experiments", []),
            ),
            "results": (
                "结果页只保留能直接支撑结论的核心证据。",
                summary.main_results[:4],
                section_map.get("results", []) or section_map.get("experiments", []),
            ),
            "analysis": (
                "分析页重点解释结果原因、边界与可迁移性。",
                bulletize(
                    pick_primary_text(section_map, "discussion", fallback=pick_primary_text(section_map, "results")),
                    max_bullets=4,
                ),
                section_map.get("discussion", []) or section_map.get("results", []),
            ),
            "strengths": (
                "优势页只概括原文能支撑的强项。",
                summary.strengths[:4],
                section_map.get("results", []) or section_map.get("method", []),
            ),
            "limitations": (
                "局限页只保留原文可支撑的风险与边界。",
                summary.limitations[:4],
                section_map.get("limitations", []) or section_map.get("discussion", []) or section_map.get("results", []),
            ),
            "discussion": (
                "讨论页用于引导老师或同学继续追问价值与边界。",
                summary.discussion_points[:4],
                section_map.get("discussion", []) or section_map.get("results", []) or section_map.get("introduction", []),
            ),
            "conclusion": (
                summary.conclusion,
                [summary.conclusion, "回到论文贡献、结果证据与应用价值。"],
                section_map.get("conclusion", []) or section_map.get("results", []),
            ),
        }
        key_message, raw_bullets, supporting_sections = content_map.get(
            slide_type,
            (summary.one_sentence_summary, [summary.one_sentence_summary], section_map.get(key_section, [])),
        )
        bullets = self._compact_bullets([truncate_plain(item, 120) for item in raw_bullets if item], chinese_mode)
        bullets = self._ensure_meaningful_bullets(bullets, supporting_sections or section_map.get(key_section, []), slide_type)
        unsupported_claims = [bullet for bullet in bullets if "positive results" in bullet.lower() and not section_map.get("results")]
        source_refs = make_source_refs(supporting_sections or section_map.get(key_section, []), max_refs=2)

        if concise_requested:
            bullets = bullets[:3]
        if visual_requested and not visual_elements and assets:
            for asset in assets.assets:
                if asset.suggested_slide_usage in {slide_type, "method", "result"}:
                    visual_elements.append(
                        {
                            "type": asset.asset_type,
                            "asset_id": asset.id,
                            "description": asset.short_visual_description or asset.original_caption,
                            "placement_hint": "right_panel",
                        }
                    )
                    break

        confidence = 0.85 if source_refs else 0.45
        title = self._format_title(title, chinese_mode)
        key_message = self._normalize_key_message(key_message, bullets)

        return SlideDraft(
            slide_id="",
            slide_type=slide_type,
            title=title,
            purpose=f"围绕{title}输出可汇报的中文要点。",
            key_message=key_message,
            bullets=bullets,
            visual_elements=visual_elements,
            speaker_notes=self._maybe_notes(profile, self._build_speaker_notes(title, key_message, bullets, source_refs)),
            source_refs=source_refs,
            confidence=confidence,
            unsupported_claims=unsupported_claims,
        )

    def _build_speaker_notes(self, title: str, key_message: str, bullets: list[str], source_refs) -> str:
        source_line = "、".join(ref.section_title or f"第{ref.page_number}页" for ref in source_refs) if source_refs else "原文支撑较弱"
        bullet_line = "；".join(bullets[:3])
        return truncate_plain(
            f"先用一句话讲清“{title}”的核心结论：{key_message}。再依次展开：{bullet_line}。引用{source_line}，只讲原文能支撑的内容。",
            420,
        )

    def _compact_bullets(self, bullets: list[str], chinese_mode: bool) -> list[str]:
        limited = bullets[:4]
        max_len = 18 if chinese_mode else 80
        compacted: list[str] = []
        for bullet in limited:
            candidate = normalize_presentation_text(bullet.strip())
            candidate = re.sub(r"^(the paper|this paper|we|authors?)\s+", "", candidate, flags=re.IGNORECASE)
            candidate = candidate.replace("Confidence", "")
            candidate = self._clean_generated_bullet(candidate)
            candidate = truncate_plain(candidate, max_len)
            if candidate and candidate not in compacted:
                compacted.append(candidate)
        return compacted[:4]

    def _format_title(self, title: str, chinese_mode: bool) -> str:
        normalized = normalize_presentation_text(title).lower()
        if normalized in self.TITLE_MAP:
            return self.TITLE_MAP[normalized]
        if "experimental" in normalized or "experiment" in normalized:
            return "实验设计"
        for key, mapped in self.TITLE_MAP.items():
            if key in normalized:
                return mapped
        if chinese_mode or contains_cjk(title):
            return compress_title(title, 14)
        return truncate_plain(normalize_presentation_text(title), 60)

    def _maybe_notes(self, profile: UserProfile | None, notes: str) -> str:
        if profile and not profile.include_speaker_notes:
            return ""
        return notes

    def _normalize_key_message(self, key_message: str, bullets: list[str]) -> str:
        cleaned = normalize_presentation_text(key_message)
        cleaned = re.sub(r"confidence[:：]?\s*\d*\.?\d+", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"uncertain|not enough information", "", cleaned, flags=re.IGNORECASE)
        if cleaned and not contains_cjk(cleaned):
            cleaned = self._localize_english_bullet(cleaned)
        if not cleaned and bullets:
            cleaned = bullets[0]
        if len(cleaned) < 8 and bullets:
            cleaned = "；".join(bullets[:2])
        return truncate_plain(cleaned, 90)

    def _ensure_meaningful_bullets(self, bullets: list[str], sections: list[Section], slide_type: str) -> list[str]:
        filtered: list[str] = []
        for bullet in bullets:
            cleaned = normalize_presentation_text(bullet)
            lowered = cleaned.lower()
            if any(
                marker in lowered
                for marker in [
                    "uncertain",
                    "confidence",
                    "method details are uncertain",
                    "results remain uncertain",
                    "not enough information",
                ]
            ):
                continue
            if any(marker in cleaned for marker in ["待补充", "……", "...", "Method details are uncertain"]):
                continue
            if cleaned in {"重点展示结果", "解释方法细节", "讨论设计权衡"}:
                continue
            if cleaned:
                filtered.append(cleaned)

        if len(filtered) < 2:
            source_text = " ".join(section.text for section in sections[:2]) if sections else ""
            for sentence in bulletize(source_text, max_bullets=4):
                candidate = self._clean_generated_bullet(sentence)
                if candidate and candidate not in filtered:
                    filtered.append(candidate)
                if len(filtered) >= 3:
                    break

        if slide_type not in {"title", "divider"} and len(filtered) < 2:
            fallback_map = {
                "background": ["说明背景价值", "指出研究动因"],
                "problem": ["说明研究对象", "明确现有不足"],
                "method": ["拆解方法流程", "说明关键模块"],
                "technical": ["提炼技术结构", "说明设计理由"],
                "experiments": ["说明实验设置", "交代评价方式"],
                "results": ["提炼核心结果", "说明结果意义"],
                "analysis": ["解释结果原因", "指出适用边界"],
                "limitations": ["指出应用边界", "说明改进方向"],
                "discussion": ["聚焦关键追问", "引导后续讨论"],
                "conclusion": ["回收核心结论", "强调应用价值"],
            }
            for candidate in fallback_map.get(slide_type, ["补充关键证据", "强化页面结论"]):
                if candidate not in filtered:
                    filtered.append(candidate)
                if len(filtered) >= 2:
                    break
        return filtered[:4]

    def _title_slide_title(self, paper_title: str, summary: PaperSummary) -> str:
        if contains_cjk(paper_title):
            return compress_title(paper_title, 14)
        if summary.keywords:
            keyword = summary.keywords[0]
            if keyword:
                return compress_title(f"{keyword}研究", 14)
        return "论文研究汇报"

    def _localize_english_bullet(self, text: str) -> str:
        keywords = re.findall(r"[A-Za-z0-9-]{3,}", text)
        ignored = {"the", "this", "that", "these", "those", "with", "from", "into", "through"}
        usable = [token for token in keywords if token.lower() not in ignored]
        focus = usable[0].upper() if usable else "核心流程"
        if "result" in text.lower():
            return f"给出{focus}结果"
        if "method" in text.lower() or "pipeline" in text.lower():
            return f"说明{focus}流程"
        if "experiment" in text.lower():
            return f"验证{focus}效果"
        if "conclusion" in text.lower():
            return f"总结{focus}结论"
        return f"围绕{focus}展开"

    def _clean_generated_bullet(self, text: str) -> str:
        candidate = normalize_presentation_text(text)
        if not contains_cjk(candidate):
            candidate = self._localize_english_bullet(candidate)
        return truncate_plain(candidate, 18)
