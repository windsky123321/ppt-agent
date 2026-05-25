from __future__ import annotations

import re

from app.schemas.deck import QualityIssue, QualityReport, SlideDrafts
from app.utils.text_utils import contains_cjk, contains_ellipsis, count_cjk, normalize_presentation_text


PLACEHOLDER_MARKERS = [
    "uncertain",
    "tbd",
    "not enough information",
    "method details are uncertain",
    "results remain uncertain",
    "discussion questions are uncertain",
    "待补充",
]

GENERIC_BULLETS = {
    "重点展示结果",
    "解释方法细节",
    "讨论设计权衡",
    "提炼原文关键信息",
    "补充关键证据",
}


class SlideQualityChecker:
    def run(self, drafts: SlideDrafts) -> QualityReport:
        issues: list[QualityIssue] = []
        notes: list[str] = []
        for slide in drafts.slides:
            title = normalize_presentation_text(slide.title)
            if slide.slide_type not in {"title", "divider"} and count_cjk(title) > 14:
                issues.append(self._issue(slide, "title_length", "标题过长，应压缩到 14 个中文字符以内。"))
            if slide.slide_type not in {"title", "divider"} and count_cjk(title) == 0:
                issues.append(self._issue(slide, "mixed_language", "正式页标题应使用中文表达。"))
            if self._contains_bad_text(title) or self._contains_bad_text(slide.key_message):
                issues.append(self._issue(slide, "placeholder", "页面存在占位语或不应进入正式稿的提示语。"))
            if "confidence" in title.lower() or "confidence" in slide.key_message.lower():
                issues.append(self._issue(slide, "confidence", "正式页不应出现 Confidence 字样。"))
            if contains_ellipsis(title) or contains_ellipsis(slide.key_message):
                issues.append(self._issue(slide, "ellipsis", "标题或关键信息存在省略号截断。"))

            if slide.slide_type not in {"title", "divider"}:
                if len(slide.bullets) < 2:
                    issues.append(self._issue(slide, "insufficient_content", "页面要点不足，至少需要 2 条有效要点。"))
                if len(slide.bullets) > 4:
                    issues.append(self._issue(slide, "insufficient_content", "页面要点过多，应控制在 2-4 条。"))

            for bullet in slide.bullets:
                cleaned = normalize_presentation_text(bullet)
                lowered = cleaned.lower()
                if contains_ellipsis(cleaned):
                    issues.append(self._issue(slide, "ellipsis", f"要点存在省略号：{cleaned}"))
                if "confidence" in lowered:
                    issues.append(self._issue(slide, "confidence", f"要点存在 Confidence：{cleaned}"))
                if self._contains_bad_text(cleaned):
                    issues.append(self._issue(slide, "placeholder", f"要点存在占位语：{cleaned}"))
                if cleaned in GENERIC_BULLETS or len(cleaned) < 4:
                    issues.append(self._issue(slide, "generic_bullet", f"要点过于空泛：{cleaned}"))
                if contains_cjk(cleaned) and self._looks_mixed_language(cleaned):
                    issues.append(self._issue(slide, "mixed_language", f"要点中英混杂：{cleaned}"))
                if slide.slide_type not in {"title", "divider"} and count_cjk(cleaned) == 0 and not self._allowed_term_line(cleaned):
                    issues.append(self._issue(slide, "mixed_language", f"正式页应以中文表达为主：{cleaned}"))

            if slide.confidence < 0.6:
                notes.append(f"{slide.slide_id or slide.title}: 置信度较低，相关内容已限制在日志与质量报告中。")

        unique_issues = self._deduplicate(issues)
        return QualityReport(
            passed=not unique_issues,
            blocked_export=bool(unique_issues),
            issue_count=len(unique_issues),
            issues=unique_issues,
            low_confidence_notes=notes,
        )

    def _contains_bad_text(self, text: str) -> bool:
        lowered = text.lower()
        return any(marker in lowered or marker in text for marker in PLACEHOLDER_MARKERS)

    def _looks_mixed_language(self, text: str) -> bool:
        english_tokens = re.findall(r"[A-Za-z]{4,}", text)
        return len(english_tokens) >= 2

    def _allowed_term_line(self, text: str) -> bool:
        allowed = {"pdf", "ppt", "pptx", "openai", "windows"}
        tokens = {token.lower() for token in re.findall(r"[A-Za-z]+", text)}
        return bool(tokens) and tokens.issubset(allowed)

    def _issue(self, slide, category: str, message: str) -> QualityIssue:
        return QualityIssue(
            slide_id=slide.slide_id,
            slide_title=slide.title,
            severity="error",
            category=category,
            message=message,
        )

    def _deduplicate(self, issues: list[QualityIssue]) -> list[QualityIssue]:
        seen: set[tuple[str, str, str]] = set()
        deduped: list[QualityIssue] = []
        for issue in issues:
            key = (issue.slide_id, issue.category, issue.message)
            if key in seen:
                continue
            seen.add(key)
            deduped.append(issue)
        return deduped
