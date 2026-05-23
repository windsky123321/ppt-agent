import json

from app.llm.providers import BaseLLMProvider
from app.prompts.templates import SUMMARY_PROMPT
from app.schemas.deck import PaperSummary
from app.schemas.paper import ParsedPaper
from app.utils.paper_utils import build_section_map, bulletize, first_sentences, infer_keywords, pick_primary_text
from app.utils.text_utils import normalize_whitespace, safe_truncate


class PaperSummaryAgent:
    def __init__(self, llm: BaseLLMProvider) -> None:
        self.llm = llm

    def run(self, paper: ParsedPaper) -> PaperSummary:
        if self.llm.__class__.__name__ == "MockLLMProvider":
            return self._run_heuristic(paper)
        prompt = "\n".join(
            [
                SUMMARY_PROMPT,
                "Schema: paper_summary",
                json.dumps(paper.model_dump(), ensure_ascii=False),
            ]
        )
        data = self.llm.generate_json(prompt, "paper_summary")
        return PaperSummary(**data)

    def _run_heuristic(self, paper: ParsedPaper) -> PaperSummary:
        sections = build_section_map(paper)
        abstract = paper.abstract or pick_primary_text(sections, "abstract")
        intro = pick_primary_text(sections, "introduction", fallback=abstract)
        method = pick_primary_text(sections, "method", fallback="Method details are uncertain from the parsed paper.")
        technical = pick_primary_text(sections, "technical", fallback=method)
        experiments = pick_primary_text(sections, "experiments", fallback="Experimental setup is uncertain from the parsed paper.")
        results = pick_primary_text(sections, "results", fallback="")
        discussion = pick_primary_text(sections, "discussion", fallback=results)
        conclusion_text = pick_primary_text(sections, "conclusion", fallback="")
        limitations_text = pick_primary_text(sections, "limitations", fallback=discussion)

        takeaway_parts = first_sentences(abstract or intro, limit=2)
        one_sentence_summary = safe_truncate(" ".join(takeaway_parts), 180) if takeaway_parts else "The paper summary is uncertain from the parsed text."

        problem = first_sentences(intro or abstract, limit=1)
        motivation = first_sentences(intro, limit=2)
        research_gap = self._infer_research_gap(intro, abstract)
        key_contributions = self._derive_contributions(method, results, conclusion_text)
        main_results = bulletize(results or discussion, max_bullets=3) or ["Main results are uncertain from the parsed paper."]
        strengths = self._derive_strengths(method, results, experiments)
        limitations = bulletize(limitations_text, max_bullets=3)
        if not limitations:
            limitations = ["Limitations are uncertain because the parsed paper does not expose a dedicated limitations section."]
        discussion_points = self._derive_discussion_points(research_gap, results, limitations)
        conclusion = safe_truncate(" ".join(first_sentences(conclusion_text or results or abstract, limit=2)) or "Conclusion is uncertain from the parsed paper.", 180)

        return PaperSummary(
            title=paper.title,
            one_sentence_summary=one_sentence_summary,
            problem=problem[0] if problem else "The paper problem is uncertain from the parsed text.",
            motivation=" ".join(motivation) if motivation else "Motivation is uncertain from the parsed text.",
            research_gap=research_gap,
            key_contributions=key_contributions,
            method_overview=safe_truncate(" ".join(first_sentences(method, limit=2)) or "Method overview is uncertain from the parsed paper.", 220),
            experiment_setup=safe_truncate(" ".join(first_sentences(experiments, limit=2)) or "Experimental setup is uncertain from the parsed paper.", 220),
            main_results=main_results,
            strengths=strengths,
            limitations=limitations,
            discussion_points=discussion_points,
            conclusion=conclusion,
            keywords=infer_keywords(paper),
        )

    def _infer_research_gap(self, intro: str, abstract: str) -> str:
        source = intro or abstract
        sentences = first_sentences(source, limit=3)
        for sentence in sentences:
            lowered = sentence.lower()
            if any(marker in lowered for marker in ["however", "limited", "challenge", "difficult", "gap", "problem"]):
                return safe_truncate(sentence, 180)
        return "Research gap is uncertain from the parsed introduction and abstract."

    def _derive_contributions(self, method: str, results: str, conclusion_text: str) -> list[str]:
        candidates = []
        for source in [method, results, conclusion_text]:
            for sentence in bulletize(source, max_bullets=2):
                if sentence not in candidates:
                    candidates.append(sentence)
        return candidates[:3] or ["Key contributions are uncertain from the parsed paper."]

    def _derive_strengths(self, method: str, results: str, experiments: str) -> list[str]:
        strengths = []
        if method and "uncertain" not in method.lower():
            strengths.append("The paper provides a concrete method section that can be presented clearly.")
        if experiments and "uncertain" not in experiments.lower():
            strengths.append("The paper includes an explicit experimental setup section.")
        if results:
            strengths.append("The paper reports result-related evidence that can be grounded to specific sections.")
        return strengths[:3] or ["Strengths are uncertain from the parsed paper."]

    def _derive_discussion_points(self, research_gap: str, results: str, limitations: list[str]) -> list[str]:
        points: list[str] = []
        if research_gap:
            points.append(f"Does the proposed method fully address the stated gap: {safe_truncate(research_gap, 110)}")
        result_sentence = first_sentences(results, limit=1)
        if result_sentence:
            points.append(f"Which reported result matters most for evaluating the paper: {safe_truncate(result_sentence[0], 110)}")
        if limitations:
            points.append(f"Which limitation is most important to discuss: {safe_truncate(limitations[0], 110)}")
        return points[:3] or ["Discussion questions are uncertain from the parsed paper."]
