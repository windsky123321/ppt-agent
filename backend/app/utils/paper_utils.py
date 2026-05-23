from __future__ import annotations

from app.schemas.common import SourceRef
from app.schemas.paper import ParsedPaper, Section
from app.utils.text_utils import normalize_whitespace, safe_truncate


SECTION_ALIASES: dict[str, list[str]] = {
    "abstract": ["abstract"],
    "background": ["background", "motivation", "related work"],
    "introduction": ["introduction", "overview"],
    "problem": ["problem", "task", "objective"],
    "method": ["method", "methods", "approach", "model", "framework"],
    "technical": ["architecture", "implementation", "technical", "framework", "model"],
    "experiments": ["experiments", "experimental setup", "evaluation", "dataset"],
    "results": ["results", "analysis", "ablation", "discussion"],
    "discussion": ["discussion", "analysis", "ablation"],
    "limitations": ["limitations", "limitation"],
    "conclusion": ["conclusion", "conclusions", "future work"],
    "references": ["references"],
}


def build_section_map(paper: ParsedPaper) -> dict[str, list[Section]]:
    result: dict[str, list[Section]] = {key: [] for key in SECTION_ALIASES}
    for section in paper.sections:
        title = section.title.lower()
        for key, aliases in SECTION_ALIASES.items():
            if any(alias in title for alias in aliases):
                result[key].append(section)
    if not result["background"] and result["introduction"]:
        result["background"] = result["introduction"][:]
    if not result["problem"] and result["introduction"]:
        result["problem"] = result["introduction"][:]
    if not result["technical"] and result["method"]:
        result["technical"] = result["method"][:]
    if not result["discussion"] and result["results"]:
        result["discussion"] = result["results"][:]
    return result


def pick_primary_text(section_map: dict[str, list[Section]], key: str, fallback: str = "") -> str:
    sections = section_map.get(key, [])
    if sections:
        return normalize_whitespace(" ".join(section.text for section in sections))
    return normalize_whitespace(fallback)


def first_sentences(text: str, limit: int = 2) -> list[str]:
    if not text:
        return []
    parts = [normalize_whitespace(chunk) for chunk in text.replace("?", ".").replace("!", ".").split(".") if normalize_whitespace(chunk)]
    return parts[:limit]


def bulletize(text: str, max_bullets: int = 4) -> list[str]:
    bullets = first_sentences(text, limit=max_bullets)
    return [safe_truncate(sentence, 120) for sentence in bullets if sentence]


def make_source_refs(sections: list[Section], max_refs: int = 2) -> list[SourceRef]:
    refs: list[SourceRef] = []
    for section in sections[:max_refs]:
        refs.append(
            SourceRef(
                page_number=section.page_start if section.page_start > 0 else None,
                section_title=section.title,
                evidence_summary=safe_truncate(normalize_whitespace(section.text), 160),
            )
        )
    return refs


def infer_keywords(paper: ParsedPaper) -> list[str]:
    tokens = []
    for source in [paper.title, paper.abstract]:
        for token in source.replace(",", " ").split():
            clean = token.strip("().:;").lower()
            if len(clean) > 4 and clean not in tokens:
                tokens.append(clean)
    return tokens[:8]
