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
                            zh_message="该内容页缺少来源页码。",
                        )
                    )
                elif all((ref.section_title or "").lower() == "abstract" for ref in slide.source_refs):
                    warnings.append(
                        GroundingWarning(
                            slide_id=slide.slide_id,
                            severity="medium",
                            message="All source_refs point only to Abstract.",
                            zh_message="该页来源仅指向摘要，依据不足。",
                        )
                    )

            if slide.unsupported_claims:
                warnings.append(
                    GroundingWarning(
                        slide_id=slide.slide_id,
                        severity="high",
                        message=f"Unsupported claims flagged: {'; '.join(slide.unsupported_claims)}",
                        zh_message="存在缺少原文支撑的结论，请减少主观推断。",
                    )
                )

        return GroundingReport(slide_count=len(drafts.slides), warnings=warnings)

    def _looks_like_content_slide(self, slide) -> bool:
        return slide.slide_type in {"content", "method", "technical", "result", "analysis", "limitations", "limitation", "contributions", "background", "problem", "strengths"}
