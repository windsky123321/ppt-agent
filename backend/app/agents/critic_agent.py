from __future__ import annotations

from app.schemas.deck import CriticIssue, CriticReport, GroundingReport, SlideDrafts
from app.schemas.profile import UserProfile


class CriticAgent:
    def run(self, drafts: SlideDrafts, grounding_report: GroundingReport, profile: UserProfile) -> CriticReport:
        issues: list[CriticIssue] = []

        for slide in drafts.slides:
            if slide.slide_type in {"content", "method", "result", "results", "limitation", "limitations"} and not slide.source_refs:
                issues.append(
                    self._issue(
                        slide.slide_id,
                        "high",
                        "grounding",
                        "Missing source_refs on grounded slide.",
                        "该内容页缺少来源页码。",
                        "Add conservative section-specific source refs.",
                        True,
                    )
                )
            if len(slide.bullets) > 4:
                issues.append(
                    self._issue(
                        slide.slide_id,
                        "medium",
                        "content",
                        "Too many bullets.",
                        "页面要点过多，请压缩到 2-4 条。",
                        "Reduce to at most 4 concise bullets.",
                        True,
                    )
                )
            if any(len(bullet) > 24 for bullet in slide.bullets):
                issues.append(
                    self._issue(
                        slide.slide_id,
                        "medium",
                        "layout",
                        "Likely text overflow due to long bullets.",
                        "要点可能超出排版空间，请缩短表达。",
                        "Shorten bullets and move detail to notes.",
                        True,
                    )
                )
            if profile.include_speaker_notes and not slide.speaker_notes:
                issues.append(
                    self._issue(
                        slide.slide_id,
                        "medium",
                        "speaker_notes",
                        "Missing speaker notes.",
                        "该页缺少备注，可补充简短讲解提示。",
                        "Add concise presenter notes.",
                        True,
                    )
                )
            if slide.confidence < 0.55:
                issues.append(
                    self._issue(
                        slide.slide_id,
                        "medium",
                        "content",
                        "Low-confidence slide.",
                        "页面依据不足。",
                        "Reduce unsupported claims or strengthen grounding.",
                        True,
                    )
                )
            if slide.unsupported_claims:
                issues.append(
                    self._issue(
                        slide.slide_id,
                        "high",
                        "grounding",
                        f"Unsupported claims present: {'; '.join(slide.unsupported_claims)}",
                        "请减少无来源结论，或补充论文依据。",
                        "Remove unsupported claims or mark uncertainty explicitly.",
                        True,
                    )
                )
            if slide.slide_type in {"result", "results"} and not slide.visual_elements:
                issues.append(
                    self._issue(
                        slide.slide_id,
                        "low",
                        "visual",
                        "Result slide has no visual element.",
                        "结果页缺少图表支撑，可补充图或表。",
                        "Use a ranked figure/table if available.",
                        False,
                    )
                )

        for warning in grounding_report.warnings:
            issues.append(
                self._issue(
                    warning.slide_id,
                    warning.severity,
                    "grounding",
                    warning.message,
                    warning.zh_message or "请补充与论文原文对应的依据。",
                    "Improve section-specific grounding.",
                    warning.severity == "high",
                )
            )

        approved = not any(issue.severity == "high" for issue in issues)
        score = max(0, 100 - len(issues) * 7)
        zh_summary = f"共发现 {len(issues)} 项质量问题，{'已通过' if approved else '未通过'}质量检查。"
        return CriticReport(
            deck_score=score,
            summary=f"Detected {len(issues)} issues across {len(drafts.slides)} slides.",
            zh_summary=zh_summary,
            issues=issues,
            approved=approved,
        )

    def _issue(
        self,
        slide_id: str,
        severity: str,
        category: str,
        description: str,
        zh_message: str,
        suggested_fix: str,
        requires_regeneration: bool,
    ) -> CriticIssue:
        return CriticIssue(
            slide_id=slide_id,
            severity=severity,
            category=category,
            description=description,
            zh_message=zh_message,
            suggested_fix=suggested_fix,
            requires_regeneration=requires_regeneration,
        )
