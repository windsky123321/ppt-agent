from app.schemas.deck import GroundingReport, GroundingWarning, SlideDrafts


class GroundingChecker:
    def run(self, drafts: SlideDrafts) -> GroundingReport:
        warnings: list[GroundingWarning] = []

        for slide in drafts.slides:
            if self._looks_like_content_slide(slide):
                if not slide.source_refs:
                    warnings.append(
                        GroundingWarning(
                            slide_id=slide.slide_id,
                            severity="high",
                            message="Content slide is missing source_refs.",
                        )
                    )
                elif all((ref.section_title or "").lower() == "abstract" for ref in slide.source_refs):
                    warnings.append(
                        GroundingWarning(
                            slide_id=slide.slide_id,
                            severity="medium",
                            message="All source_refs point only to Abstract.",
                        )
                    )

            if slide.unsupported_claims:
                warnings.append(
                    GroundingWarning(
                        slide_id=slide.slide_id,
                        severity="high",
                        message=f"Unsupported claims flagged: {'; '.join(slide.unsupported_claims)}",
                    )
                )

        return GroundingReport(slide_count=len(drafts.slides), warnings=warnings)

    def _looks_like_content_slide(self, slide) -> bool:
        return slide.slide_type in {"content", "method", "technical", "result", "analysis", "limitations", "limitation", "contributions", "background", "problem", "strengths"}
