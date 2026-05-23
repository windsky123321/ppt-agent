import re


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def split_paragraphs(text: str) -> list[str]:
    return [chunk.strip() for chunk in re.split(r"\n\s*\n", text) if chunk.strip()]


def safe_truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: max(limit - 3, 0)].rstrip() + "..."
