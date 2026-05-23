import json

from app.llm.providers import BaseLLMProvider
from app.prompts.templates import DECK_PLAN_PROMPT
from app.schemas.assets import ExtractedAssets
from app.schemas.common import GenerationSettings
from app.schemas.deck import DeckPlan, PaperSummary
from app.schemas.paper import ParsedPaper
from app.schemas.profile import UserProfile
from app.utils.paper_utils import build_section_map


class DeckPlannerAgent:
    def __init__(self, llm: BaseLLMProvider) -> None:
        self.llm = llm

    def run(self, paper: ParsedPaper, summary: PaperSummary, settings: GenerationSettings, profile: UserProfile | None = None, assets: ExtractedAssets | None = None) -> DeckPlan:
        if self.llm.__class__.__name__ == "MockLLMProvider":
            return self._run_heuristic(paper, summary, settings, profile, assets)
        payload = {"paper_summary": summary.model_dump(), **settings.model_dump()}
        prompt = json.dumps(payload, ensure_ascii=False)
        prompt = f"{DECK_PLAN_PROMPT}\nSchema: deck_plan\n{prompt}"
        data = self.llm.generate_json(json.dumps(payload, ensure_ascii=False), "deck_plan")
        return DeckPlan(**data)

    def _run_heuristic(self, paper: ParsedPaper, summary: PaperSummary, settings: GenerationSettings, profile: UserProfile | None, assets: ExtractedAssets | None) -> DeckPlan:
        section_map = build_section_map(paper)
        instruction_text = (settings.long_instruction or "") + " " + ((profile.custom_instructions if profile else "") or "")
        lowered_instruction = instruction_text.lower()
        wants_backup = "backup" in lowered_instruction or "答辩" in instruction_text or (settings.slide_count >= 18)
        quick_mode = settings.slide_count <= 8
        blueprint = [
            ("title", "Title", "Introduce the paper, authors, and context.", ""),
            ("takeaway", "One-Slide Takeaway", "State the main idea and outcome in one slide.", "abstract"),
            ("divider", "Problem Setting", "Transition into the paper motivation and problem framing.", "introduction"),
            ("background", "Background / Motivation", "Explain why the problem matters.", "background"),
            ("problem", "Research Problem", "Define the specific problem tackled by the paper.", "problem"),
            ("contributions", "Key Contributions", "Summarize the main contributions.", "method"),
            ("method", "Method Overview", "Present the method at a high level.", "method"),
            ("technical", "Technical Details / Architecture", "Cover the technical design choices.", "technical"),
            ("experiments", "Experimental Setup", "Describe evaluation setup, datasets, and metrics.", "experiments"),
            ("results", "Main Results", "Present the main result evidence from the paper.", "results"),
            ("analysis", "Analysis / Ablation", "Discuss deeper analysis if available.", "discussion"),
            ("strengths", "Strengths", "Highlight why the work is compelling.", "results"),
            ("limitations", "Limitations", "Be explicit about weaknesses and open risks.", "limitations"),
            ("discussion", "Discussion Questions", "Frame useful reading-group discussion points.", "discussion"),
            ("conclusion", "Conclusion", "Close with the final assessment and takeaway.", "conclusion"),
        ]
        if wants_backup:
            blueprint.append(("backup", "Backup Evidence", "Keep extra grounded evidence available for discussion.", "results"))

        if quick_mode:
            blueprint = [
                ("title", "Title", "Introduce the paper quickly.", ""),
                ("takeaway", "One-Slide Takeaway", "State the main idea and outcome in one slide.", "abstract"),
                ("background", "Background / Motivation", "Explain why the problem matters.", "background"),
                ("method", "Method Overview", "Present the method at a high level.", "method"),
                ("results", "Main Results", "Present the main result evidence from the paper.", "results"),
                ("limitations", "Limitations", "Be explicit about weaknesses and open risks.", "limitations"),
                ("discussion", "Discussion Questions", "Frame useful discussion points.", "discussion"),
                ("conclusion", "Conclusion", "Close with the final assessment and takeaway.", "conclusion"),
            ]

        slides = []
        asset_lookup = {}
        for asset in (assets.assets if assets else []):
            asset_lookup.setdefault(asset.suggested_slide_usage, []).append(asset.id)
        for slide_type, title, purpose, key_section in blueprint:
            if slide_type not in {"title", "takeaway", "contributions", "strengths", "discussion", "conclusion"}:
                if not section_map.get(key_section) and key_section not in {"background", "problem", "technical", "discussion", "limitations"}:
                    continue
                if slide_type == "analysis" and not (section_map.get("discussion") or section_map.get("results")):
                    continue
                if slide_type == "limitations" and not summary.limitations:
                    continue
                if slide_type == "discussion" and not settings.include_discussion_questions:
                    continue
            slides.append(
                {
                    "slide_id": f"slide_{len(slides)+1:02d}",
                    "slide_type": slide_type,
                    "title": title,
                    "purpose": purpose,
                    "key_section": key_section,
                    "asset_ids": asset_lookup.get(slide_type, [])[:1] or asset_lookup.get("method" if slide_type in {"method", "technical"} else "result", [])[:1],
                }
            )
            if len(slides) >= settings.slide_count:
                break

        return DeckPlan(
            deck_title=paper.title,
            target_audience=settings.audience,
            language=settings.language,
            slide_count=len(slides),
            slides=slides,
        )
