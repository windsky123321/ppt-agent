import json

from app.llm.providers import BaseLLMProvider
from app.prompts.templates import SLIDE_WRITER_PROMPT
from app.schemas.assets import ExtractedAssets
from app.schemas.deck import DeckPlan, PaperSummary, SlideDraft, SlideDrafts
from app.schemas.paper import ParsedPaper
from app.schemas.profile import UserProfile
from app.utils.paper_utils import build_section_map, bulletize, make_source_refs, pick_primary_text
from app.utils.text_utils import safe_truncate


class SlideWriterAgent:
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
        data = self.llm.generate_json(json.dumps(payload, ensure_ascii=False), "slide_drafts")
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
            draft.purpose = slide.purpose
            drafts.append(draft)
        return SlideDrafts(slides=drafts)

    def _build_slide(
        self,
        slide_type: str,
        title: str,
        key_section: str,
        paper: ParsedPaper,
        summary: PaperSummary,
        section_map,
        asset_ids: list[str],
        assets: ExtractedAssets | None,
        profile: UserProfile | None,
    ) -> SlideDraft:
        ranked_assets = {asset.id: asset for asset in (assets.assets if assets else [])}
        profile_instruction = " ".join(
            [profile.custom_instructions if profile else "", profile.long_generation_instruction if profile else ""]
        ).strip()
        concise_requested = bool(profile and profile.tone == "concise") or "reduce text" in profile_instruction.lower() or "简洁" in profile_instruction
        visual_requested = bool(profile and profile.tone == "visual") or "visual" in profile_instruction.lower() or "图" in profile_instruction or "表" in profile_instruction

        visual_elements = []
        for asset_id in asset_ids[:1]:
            asset = ranked_assets.get(asset_id)
            if asset:
                visual_elements.append(
                    {
                        "type": asset.asset_type,
                        "asset_id": asset.id,
                        "description": asset.short_visual_description or asset.original_caption,
                        "placement_hint": "right_panel" if slide_type in {"method", "technical", "results", "analysis", "backup"} else "footer_callout",
                    }
                )

        if slide_type == "title":
            return SlideDraft(
                slide_id="",
                slide_type=slide_type,
                title=paper.title,
                subtitle=", ".join(paper.authors[:4]) or "Academic paper presentation",
                purpose="Introduce the paper and the active presentation profile.",
                key_message=summary.one_sentence_summary,
                bullets=[],
                speaker_notes=f"Introduce the paper title, authors, and the core topic: {summary.one_sentence_summary}",
                confidence=0.95,
            )

        if slide_type == "divider":
            return SlideDraft(
                slide_id="",
                slide_type=slide_type,
                title=title,
                subtitle="From motivation to technical content",
                purpose="Transition into the next section.",
                key_message="This section shifts from context into the main technical argument.",
                bullets=[],
                speaker_notes="Use this slide as a transition before going deeper into the problem and method.",
                confidence=0.9,
            )

        if slide_type == "backup":
            source_refs = make_source_refs(section_map.get("results", []) or section_map.get("method", []), max_refs=2)
            return SlideDraft(
                slide_id="",
                slide_type=slide_type,
                title="补充证据" if profile and profile.preferred_language == "zh" else title,
                subtitle="Extra grounded material for Q&A",
                purpose="Keep compact backup evidence for deeper discussion.",
                key_message="Use this slide only when the audience asks for deeper evidence or implementation detail.",
                bullets=bulletize(pick_primary_text(section_map, "results", fallback=pick_primary_text(section_map, "method")), max_bullets=4),
                visual_elements=visual_elements,
                speaker_notes="Use this slide as backup material only when questions require more direct evidence from the paper.",
                source_refs=source_refs,
                confidence=0.8 if source_refs else 0.5,
            )

        content_map = {
            "takeaway": (
                summary.one_sentence_summary,
                [
                    summary.problem,
                    summary.method_overview,
                    summary.main_results[0] if summary.main_results else "Results remain uncertain from the parsed paper.",
                ],
                section_map.get("abstract", []) or section_map.get("introduction", []),
            ),
            "background": (
                summary.motivation,
                bulletize(pick_primary_text(section_map, "background", fallback=pick_primary_text(section_map, "introduction")), max_bullets=4),
                section_map.get("background", []) or section_map.get("introduction", []),
            ),
            "problem": (
                summary.problem,
                [summary.problem, summary.research_gap, "Focus on the exact task framing before discussing the method."],
                section_map.get("problem", []) or section_map.get("introduction", []),
            ),
            "contributions": (
                "The paper makes several concrete contributions.",
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
                bulletize(pick_primary_text(section_map, "technical", fallback=pick_primary_text(section_map, "method")), max_bullets=4),
                section_map.get("technical", []) or section_map.get("method", []),
            ),
            "experiments": (
                summary.experiment_setup,
                bulletize(pick_primary_text(section_map, "experiments"), max_bullets=4),
                section_map.get("experiments", []),
            ),
            "results": (
                "The main results should be read directly from the paper evidence.",
                summary.main_results[:4],
                section_map.get("results", []) or section_map.get("experiments", []),
            ),
            "analysis": (
                "Deeper analysis is only included when the paper exposes it.",
                bulletize(pick_primary_text(section_map, "discussion", fallback=pick_primary_text(section_map, "results")), max_bullets=4),
                section_map.get("discussion", []) or section_map.get("results", []),
            ),
            "strengths": (
                "The strengths reflect what the parsed paper supports directly.",
                summary.strengths[:4],
                section_map.get("results", []) or section_map.get("method", []),
            ),
            "limitations": (
                "Limitations are stated conservatively and marked uncertain when weakly grounded.",
                summary.limitations[:4],
                section_map.get("limitations", []) or section_map.get("discussion", []) or section_map.get("results", []),
            ),
            "discussion": (
                "Use these questions to drive group discussion.",
                summary.discussion_points[:4],
                section_map.get("discussion", []) or section_map.get("results", []) or section_map.get("introduction", []),
            ),
            "conclusion": (
                summary.conclusion,
                [summary.conclusion, "Revisit the main contributions and the quality of supporting evidence."],
                section_map.get("conclusion", []) or section_map.get("results", []),
            ),
        }
        key_message, raw_bullets, supporting_sections = content_map.get(
            slide_type,
            (summary.one_sentence_summary, [summary.one_sentence_summary], section_map.get(key_section, [])),
        )
        bullets = [safe_truncate(item, 120) for item in raw_bullets if item][:5]
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

        confidence = 0.85 if source_refs else 0.35
        if any("uncertain" in bullet.lower() for bullet in bullets):
            confidence = min(confidence, 0.55)

        if profile and profile.preferred_language == "zh":
            title = f"{title}（中文）"
        elif profile and profile.preferred_language == "bilingual":
            title = f"{title} / {title}"

        return SlideDraft(
            slide_id="",
            slide_type=slide_type,
            title=title,
            purpose=f"Support the audience with a {slide_type} slide grounded in the paper.",
            key_message=safe_truncate(key_message, 180),
            bullets=bullets,
            visual_elements=visual_elements,
            speaker_notes=self._build_speaker_notes(title, key_message, bullets, source_refs),
            source_refs=source_refs,
            confidence=confidence,
            unsupported_claims=unsupported_claims,
        )

    def _build_speaker_notes(self, title: str, key_message: str, bullets: list[str], source_refs) -> str:
        source_line = ", ".join(ref.section_title or f"p.{ref.page_number}" for ref in source_refs) if source_refs else "no strong section grounding available"
        bullet_line = " ".join(bullets[:3])
        return safe_truncate(
            f"Present '{title}' by leading with: {key_message}. Then walk through: {bullet_line}. Cite {source_line} while explaining what is directly supported versus uncertain.",
            420,
        )
