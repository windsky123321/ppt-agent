from __future__ import annotations

import re
from pathlib import Path

import fitz

from app.schemas.paper import FigureItem, PageContent, ParsedPaper, Section, TableItem
from app.utils.text_utils import normalize_presentation_text, normalize_whitespace, split_paragraphs


class PDFParser:
    def parse(self, pdf_path: Path, paper_id: str) -> ParsedPaper:
        doc = fitz.open(pdf_path)
        pages: list[PageContent] = []
        all_page_text: list[str] = []

        for index, page in enumerate(doc, start=1):
            text = self._clean_page_text(page.get_text("text"))
            pages.append(PageContent(page_number=index, text=text))
            all_page_text.append(text)

        full_text = "\n\n".join(all_page_text)
        title, authors, abstract = self._extract_metadata(full_text)
        sections = self._extract_sections(pages, abstract)
        references = self._extract_references(full_text)
        figures = self._extract_figures(full_text)
        tables = self._extract_tables(full_text)

        return ParsedPaper(
            paper_id=paper_id,
            title=title,
            authors=authors,
            abstract=abstract,
            sections=sections,
            pages=pages,
            figures=figures,
            tables=tables,
            references=references,
        )

    def _extract_metadata(self, full_text: str) -> tuple[str, list[str], str]:
        lines = [line.strip() for line in full_text.splitlines() if line.strip()]
        paragraphs = split_paragraphs(full_text)
        title = self._extract_title(lines, paragraphs)

        authors: list[str] = []
        title_index = next((idx for idx, line in enumerate(lines) if safe_line(line) == title), 0)
        author_candidates: list[str] = []
        for line in lines[title_index + 1 :]:
            lowered = line.lower()
            if lowered.startswith("abstract") or self._looks_like_section_header(line):
                break
            if "@" in line or "google" in lowered or "university" in lowered or self._looks_like_person_line(line):
                cleaned = safe_line(line.replace("∗", "").replace("†", "").replace("‡", ""))
                if cleaned and cleaned not in author_candidates and "@" not in cleaned and "brain" not in lowered and "research" not in lowered and "conference" not in lowered:
                    author_candidates.append(cleaned)
        if author_candidates:
            authors = author_candidates[:12]

        abstract = self._extract_abstract(full_text, lines, paragraphs)
        return title, authors, abstract

    def _extract_sections(self, pages: list[PageContent], abstract: str) -> list[Section]:
        page_sections: list[Section] = []
        for page in pages:
            lines = [line.strip() for line in page.text.splitlines() if line.strip()]
            current_title: str | None = None
            current_body: list[str] = []
            for line in lines:
                if self._looks_like_section_header(line):
                    if current_title and current_body:
                        page_sections.append(
                            Section(
                                title=current_title,
                                text=normalize_whitespace(" ".join(current_body)),
                                page_start=page.page_number,
                                page_end=page.page_number,
                            )
                        )
                    current_title = self._normalize_section_title(line)
                    current_body = []
                elif current_title:
                    current_body.append(line)
            if current_title and current_body:
                page_sections.append(
                    Section(
                        title=current_title,
                        text=normalize_whitespace(" ".join(current_body)),
                        page_start=page.page_number,
                        page_end=page.page_number,
                    )
                )

        if not page_sections:
            combined = "\n\n".join(page.text for page in pages)
            section_titles = [
                "Introduction",
                "Method",
                "Experiments",
                "Results",
                "Conclusion",
            ]
            chunks = split_paragraphs(combined)
            sections: list[Section] = []
            for idx, title in enumerate(section_titles):
                if idx < len(chunks):
                    sections.append(Section(title=title, text=chunks[idx], page_start=1, page_end=min(len(pages), 1)))
            return sections

        if abstract:
            page_sections.insert(0, Section(title="Abstract", text=abstract, page_start=1, page_end=1))
        return page_sections

    def _extract_references(self, full_text: str) -> list[str]:
        lowered = full_text.lower()
        marker = lowered.find("references")
        if marker == -1:
            return []
        ref_text = full_text[marker + len("references") :]
        refs = [normalize_whitespace(line) for line in re.split(r"\[\d+\]|\n", ref_text) if normalize_whitespace(line)]
        return refs[:30]

    def _extract_figures(self, full_text: str) -> list[FigureItem]:
        matches = re.findall(r"(Figure\s+\d+[:.\s-][^\n]+)", full_text, flags=re.IGNORECASE)
        return [FigureItem(label=f"Figure {idx+1}", page_number=1, caption=normalize_whitespace(text)) for idx, text in enumerate(matches[:10])]

    def _extract_tables(self, full_text: str) -> list[TableItem]:
        matches = re.findall(r"(Table\s+\d+[:.\s-][^\n]+)", full_text, flags=re.IGNORECASE)
        return [TableItem(label=f"Table {idx+1}", page_number=1, caption=normalize_whitespace(text)) for idx, text in enumerate(matches[:10])]

    def _clean_page_text(self, text: str) -> str:
        lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
        non_empty = [line for line in lines if line]
        cleaned_lines: list[str] = []
        seen_recent: list[str] = []
        for line in non_empty:
            lowered = line.lower()
            if lowered.startswith("arxiv:") or lowered.startswith("copyright ") or "all rights reserved" in lowered:
                continue
            if re.fullmatch(r"\d+", line):
                continue
            if len(line) <= 2:
                continue
            normalized = normalize_presentation_text(line)
            if normalized in seen_recent[-3:]:
                continue
            cleaned_lines.append(normalized)
            seen_recent.append(normalized)
        non_empty = cleaned_lines
        return "\n".join(non_empty)

    def _extract_abstract(self, full_text: str, lines: list[str], paragraphs: list[str]) -> str:
        abstract_lines: list[str] = []
        in_abstract = False
        for line in lines:
            lowered = line.lower()
            if lowered.startswith("abstract"):
                in_abstract = True
                remainder = re.sub(r"^abstract[:\s-]*", "", line, flags=re.IGNORECASE).strip()
                if remainder:
                    abstract_lines.append(remainder)
                continue
            if in_abstract and self._looks_like_section_header(line):
                break
            if in_abstract:
                abstract_lines.append(line)
        if abstract_lines:
            return normalize_whitespace(" ".join(abstract_lines))

        abstract_match = re.search(r"\bAbstract\b[:\s-]*(.+?)(?=\n(?:\d+(?:\.\d+)*\s+)?[A-Z][^\n]{1,80}\n)", full_text, re.IGNORECASE | re.DOTALL)
        if abstract_match:
            return normalize_whitespace(abstract_match.group(1))
        return paragraphs[2] if len(paragraphs) > 2 else ""

    def _looks_like_section_header(self, line: str) -> bool:
        stripped = line.strip()
        if not stripped or len(stripped) > 120:
            return False
        lowered = stripped.lower()
        if self._looks_like_person_line(stripped):
            return False
        if any(token in lowered for token in ["@google", "@", "gmail.com", "google brain", "google research", "university of", "conference on", "arxiv:", "equal contribution"]):
            return False
        if re.match(r"^\d+(?:\.\d+)*\s+[A-Z][A-Za-z0-9 ,/\-()]{1,80}$", stripped):
            lowered_after_number = re.sub(r"^\d+(?:\.\d+)*\s+", "", stripped).lower()
            if lowered_after_number in {"sample research paper"}:
                return False
            return True
        if re.match(r"^\d+(?:\.\d+)*$", stripped):
            return False
        if "=" in stripped or "·" in stripped or "[" in stripped and "]" not in stripped:
            return False
        if stripped.lower() in {"abstract", "references", "introduction", "method", "methods", "experiments", "results", "conclusion", "limitations"}:
            return True
        if stripped.isupper() and 2 <= len(stripped.split()) <= 8:
            return True
        heading_keywords = {
            "background",
            "motivation",
            "architecture",
            "training",
            "results",
            "discussion",
            "conclusion",
            "limitations",
            "optimizer",
            "regularization",
            "attention",
            "method",
            "methods",
            "experiments",
            "analysis",
        }
        if 1 <= len(stripped.split()) <= 4 and stripped[0].isupper() and not stripped.endswith(".") and stripped.lower() not in {"encoder:", "decoder:"}:
            if stripped.lower() not in {"provided proper attribution is provided, google hereby grants permission to"}:
                lowered_tokens = {token.lower().strip(":") for token in stripped.split()}
                if lowered_tokens & heading_keywords:
                    return True
        return False

    def _normalize_section_title(self, line: str) -> str:
        stripped = re.sub(r"^\d+(?:\.\d+)*\s+", "", line).strip()
        if stripped.isupper():
            return stripped.title()
        return stripped

    def _extract_title(self, lines: list[str], paragraphs: list[str]) -> str:
        for line in lines[:20]:
            lowered = line.lower()
            if lowered.startswith("provided proper attribution"):
                continue
            if lowered.startswith("arxiv:") or "conference" in lowered:
                continue
            if lowered.startswith("abstract"):
                break
            if len(line) > 160:
                continue
            cleaned = safe_line(line.replace("∗", "").replace("†", "").replace("‡", ""))
            if any(token in cleaned.lower() for token in ["google brain", "google research", "university of", "@", "conference on", "arxiv:"]):
                continue
            if self._looks_like_person_line(cleaned):
                continue
            if 3 <= len(cleaned.split()) <= 12 and cleaned[0].isupper():
                return cleaned
        return safe_line(paragraphs[0]) if paragraphs else "Untitled Paper"

    def _looks_like_person_line(self, line: str) -> bool:
        tokens = [token for token in re.split(r"\s+", line.strip()) if token]
        if not 2 <= len(tokens) <= 5:
            return False
        alpha_tokens = [token for token in tokens if token[0].isalpha()]
        if not 2 <= len(alpha_tokens) <= 5:
            return False
        lowered = {token.strip(",.").lower() for token in tokens}
        non_name_terms = {
            "paper",
            "research",
            "attention",
            "model",
            "models",
            "results",
            "abstract",
            "introduction",
            "training",
            "architecture",
            "transformer",
            "translation",
            "provided",
            "proper",
        }
        if lowered & non_name_terms:
            return False
        return all(token[:1].isupper() for token in alpha_tokens)


def safe_line(text: str) -> str:
    return normalize_whitespace(text.replace("\n", " "))[:300]
