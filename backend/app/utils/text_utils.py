import re


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def split_paragraphs(text: str) -> list[str]:
    return [chunk.strip() for chunk in re.split(r"\n\s*\n", text) if chunk.strip()]


def safe_truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: max(limit - 3, 0)].rstrip() + "..."


def truncate_plain(text: str, limit: int) -> str:
    normalized = normalize_whitespace(text)
    if len(normalized) <= limit:
        return normalized
    return normalized[:limit].rstrip(" ，。；：,.;:")


def strip_ellipsis(text: str) -> str:
    return normalize_whitespace(text.replace("...", " ").replace("……", " "))


def contains_cjk(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def count_cjk(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def contains_ellipsis(text: str) -> bool:
    return "..." in text or "……" in text


def normalize_presentation_text(text: str) -> str:
    cleaned = text.replace("\u3000", " ")
    cleaned = cleaned.replace("•", " ").replace("·", " ")
    cleaned = cleaned.replace("“", "\"").replace("”", "\"")
    cleaned = cleaned.replace("‘", "'").replace("’", "'")
    cleaned = cleaned.replace("—", "-").replace("–", "-")
    cleaned = re.sub(r"\s*([,.;:])\s*", r"\1 ", cleaned)
    cleaned = re.sub(r"\s*([，。；：])\s*", r"\1", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return strip_ellipsis(cleaned)


def compress_title(text: str, limit: int = 14) -> str:
    cleaned = normalize_presentation_text(text)
    if not cleaned:
        return "核心内容"
    cleaned = re.sub(r"^[0-9.\-、()\s]+", "", cleaned)
    cleaned = re.sub(r"(overview|summary|analysis|discussion|introduction)$", "", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.replace("（中文）", "").replace("(中文)", "")
    if count_cjk(cleaned) <= limit and len(cleaned) <= max(limit + 4, 18):
        return cleaned.strip(" -_/")
    parts = re.split(r"[：:，,、/\-|\s]+", cleaned)
    cjk_parts = [part for part in parts if count_cjk(part) > 0]
    for part in cjk_parts:
        if 0 < count_cjk(part) <= limit:
            return part
    if count_cjk(cleaned) > 0:
        chars = [ch for ch in cleaned if re.match(r"[\u4e00-\u9fffA-Za-z0-9]", ch)]
        result = ""
        cjk_total = 0
        for ch in chars:
            result += ch
            if re.match(r"[\u4e00-\u9fff]", ch):
                cjk_total += 1
                if cjk_total >= limit:
                    break
        return result or "核心内容"
    return truncate_plain(cleaned, limit)


def split_sentences(text: str, limit: int = 2) -> list[str]:
    if not text:
        return []
    normalized = normalize_presentation_text(text)
    chunks = re.split(r"(?<=[。！？!?\.])\s+|(?<=[。！？!?])|(?<=\.)\s+", normalized)
    sentences = [chunk.strip(" 。；;") for chunk in chunks if chunk.strip(" 。；;")]
    if not sentences:
        sentences = [normalized]
    return sentences[:limit]
