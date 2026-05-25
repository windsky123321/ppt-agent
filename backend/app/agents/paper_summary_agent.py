import json
import re

from app.llm.providers import BaseLLMProvider
from app.prompts.templates import SUMMARY_PROMPT
from app.schemas.deck import PaperSummary
from app.schemas.paper import ParsedPaper
from app.utils.paper_utils import build_section_map, bulletize, first_sentences, infer_keywords, pick_primary_text
from app.utils.text_utils import compress_title, normalize_presentation_text, truncate_plain


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
        method = pick_primary_text(sections, "method", fallback="")
        technical = pick_primary_text(sections, "technical", fallback=method)
        experiments = pick_primary_text(sections, "experiments", fallback="")
        results = pick_primary_text(sections, "results", fallback="")
        discussion = pick_primary_text(sections, "discussion", fallback=results)
        conclusion_text = pick_primary_text(sections, "conclusion", fallback="")
        limitations_text = pick_primary_text(sections, "limitations", fallback=discussion)
        topic = self._topic_label(paper)

        one_sentence_summary = f"论文围绕{topic}提出了一套可落地方案，并通过实验结果验证其有效性。"

        problem = first_sentences(intro or abstract, limit=1)
        research_gap = self._infer_research_gap(intro, abstract)
        key_contributions = self._derive_contributions(method, results, conclusion_text)
        main_results = bulletize(results or discussion, max_bullets=3) or ["结果部分信息有限，建议回看原文结果章节。"]
        strengths = self._derive_strengths(method, results, experiments)
        limitations = bulletize(limitations_text, max_bullets=3)
        if not limitations:
            limitations = ["原文未单列局限性，需要结合讨论章节补充判断。"]
        discussion_points = self._derive_discussion_points(research_gap, results, limitations)
        conclusion = truncate_plain("；".join(first_sentences(conclusion_text or results or abstract, limit=2)) or "论文结论信息有限，建议结合全文复核。", 180)

        return PaperSummary(
            title=normalize_presentation_text(paper.title) or compress_title(paper.paper_id),
            one_sentence_summary=one_sentence_summary,
            problem=f"论文聚焦{topic}这一核心问题，希望提升方案效果、稳定性或可用性。",
            motivation=f"研究动机在于回应现有方案的不足，并给出更清晰的{topic}实现路径。",
            research_gap=research_gap,
            key_contributions=key_contributions,
            method_overview=f"方法上围绕{topic}构建完整流程，覆盖解析、规划、生成与结果校验等关键环节。",
            experiment_setup=f"实验部分主要验证{topic}方案在样例数据上的效果、稳定性与输出质量。",
            main_results=main_results,
            strengths=strengths,
            limitations=limitations,
            discussion_points=discussion_points,
            conclusion=conclusion or f"结论表明，该方案能够较完整地支撑{topic}相关任务的生成与汇报。",
            keywords=infer_keywords(paper),
        )

    def _infer_research_gap(self, intro: str, abstract: str) -> str:
        source = intro or abstract
        sentences = first_sentences(source, limit=3)
        for sentence in sentences:
            lowered = sentence.lower()
            if any(marker in lowered for marker in ["however", "limited", "challenge", "difficult", "gap", "problem"]):
                return "现有研究在任务边界、流程稳定性或结果质量上仍存在明显不足。"
        for sentence in sentences:
            if any(marker in sentence for marker in ["但", "然而", "难点", "挑战", "不足", "局限"]):
                return "现有研究在任务边界、流程稳定性或结果质量上仍存在明显不足。"
        return "现有研究仍存在问题界定不清、方法不足或证据不充分的空缺。"

    def _derive_contributions(self, method: str, results: str, conclusion_text: str) -> list[str]:
        candidates = []
        for source in [method, results, conclusion_text]:
            for sentence in bulletize(source, max_bullets=2):
                localized = self._localize_evidence(sentence, "贡献")
                if localized not in candidates:
                    candidates.append(localized)
        return candidates[:3] or ["提出了围绕核心问题的整体方案。", "补齐了从输入到输出的关键流程。", "给出了可验证的实验结果。"]

    def _derive_strengths(self, method: str, results: str, experiments: str) -> list[str]:
        strengths = []
        if method:
            strengths.append("方法部分结构较完整，适合拆解成关键流程与模块。")
        if experiments:
            strengths.append("实验设置较明确，便于说明数据、对比与评价方式。")
        if results:
            strengths.append("结果章节提供了可直接引用的证据，便于支撑核心结论。")
        return strengths[:3] or ["原文具备基础汇报信息，但仍需人工复核关键结论。"]

    def _derive_discussion_points(self, research_gap: str, results: str, limitations: list[str]) -> list[str]:
        points: list[str] = []
        if research_gap:
            points.append("论文提出的方法是否真正覆盖了既有空缺与关键场景？")
        result_sentence = first_sentences(results, limit=1)
        if result_sentence:
            points.append("哪一项实验结果最能直接支撑核心结论？")
        if limitations:
            points.append("当前方案最值得继续追问的局限是什么？")
        return points[:3] or ["建议围绕问题价值、方法边界与结果可信度展开讨论。"]

    def _topic_label(self, paper: ParsedPaper) -> str:
        for keyword in infer_keywords(paper):
            candidate = re.sub(r"[^A-Za-z0-9\u4e00-\u9fff-]", "", keyword)
            if candidate:
                return candidate
        return "论文主题"

    def _localize_evidence(self, sentence: str, prefix: str) -> str:
        topic = re.findall(r"[A-Za-z0-9-]{3,}", sentence)
        focus = topic[0].upper() if topic else "核心方案"
        return f"{prefix}层面强调{focus}相关流程与结果。"
