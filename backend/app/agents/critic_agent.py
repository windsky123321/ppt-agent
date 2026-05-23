from __future__ import annotations

from app.schemas.deck import CriticIssue, CriticReport, GroundingReport, SlideDrafts
from app.schemas.profile import UserProfile


class CriticAgent:
    def run(self, drafts: SlideDrafts, grounding_report: GroundingReport, profile: UserProfile) -> CriticReport:
        issues: list[CriticIssue] = []

        for slide in drafts.slides:
            if slide.slide_type in {"content", "method", "result", "limitation"} and not slide.source_refs:
                issues.append(self._issue(slide.slide_id, "high", "grounding", "Missing source_refs on grounded slide.", "Add conservative section-specific source refs.", True))
            if len(slide.bullets) > 5:
                issues.append(self._issue(slide.slide_id, "medium", "content", "Too many bullets.", "Reduce to at most 5 concise bullets.", True))
            if any(len(bullet) > 140 for bullet in slide.bullets):
                issues.append(self._issue(slide.slide_id, "medium", "layout", "Likely text overflow due to long bullets.", "Shorten bullets and move detail to notes.", True))
            if profile.include_speaker_notes and not slide.speaker_notes:
                issues.append(self._issue(slide.slide_id, "medium", "speaker_notes", "Missing speaker notes.", "Add concise presenter notes.", True))
            if slide.confidence < 0.45:
                issues.append(self._issue(slide.slide_id, "medium", "content", "Low-confidence slide.", "Reduce unsupported claims or strengthen grounding.", True))
            if slide.unsupported_claims:
                issues.append(self._issue(slide.slide_id, "high", "grounding", f"Unsupported claims present: {'; '.join(slide.unsupported_claims)}", "Remove unsupported claims or mark uncertainty explicitly.", True))
            if slide.slide_type == "result" and not slide.visual_elements:
                issues.append(self._issue(slide.slide_id, "low", "visual", "Result slide has no visual element.", "Use a ranked figure/table if available.", False))

        for warning in grounding_report.warnings:
            issues.append(self._issue(warning.slide_id, warning.severity, "grounding", warning.message, "Improve section-specific grounding.", warning.severity == "high"))

        approved = not any(issue.severity == "high" for issue in issues)
        score = max(0, 100 - len(issues) * 7)
        return CriticReport(
            deck_score=score,
            summary=f"Detected {len(issues)} issues across {len(drafts.slides)} slides.",
            issues=issues,
            approved=approved,
        )

    def _issue(self, slide_id: str, severity: str, category: str, description: str, suggested_fix: str, requires_regeneration: bool) -> CriticIssue:
        return CriticIssue(
            slide_id=slide_id,
            severity=severity,
            category=category,
            description=description,
            suggested_fix=suggested_fix,
            requires_regeneration=requires_regeneration,
        )
