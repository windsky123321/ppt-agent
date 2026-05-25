from __future__ import annotations

from app.schemas.skill_library import SkillSearchRequest, SkillSearchResult


class MockSkillSearchProvider:
    def __init__(self) -> None:
        self._catalog = [
            SkillSearchResult(
                id="skill_business_report",
                name="商业汇报结构优化",
                description="提供咨询式目录结构、MECE 检查和管理层摘要建议。",
                source="mock",
                author="PPT Agent",
                updated_at="2026-05-25",
                license="MIT",
                tags=["business-report", "writing-polish"],
                capabilities=["business-report", "writing-polish", "token-optimizer"],
                risk_level="low",
                preview_url="mock://skill_business_report",
                installable=True,
            ),
            SkillSearchResult(
                id="skill_academic_defense",
                name="学术答辩辅助",
                description="强化研究问题、方法、实验和局限性表达。",
                source="mock",
                author="PPT Agent",
                updated_at="2026-05-25",
                license="MIT",
                tags=["academic-defense", "slide-critic"],
                capabilities=["academic-defense", "slide-critic", "slide-repair"],
                risk_level="low",
                preview_url="mock://skill_academic_defense",
                installable=True,
            ),
            SkillSearchResult(
                id="skill_chart_generator",
                name="图表表达建议",
                description="提供图表页结构建议和数据展示检查规则。",
                source="mock",
                author="PPT Agent",
                updated_at="2026-05-25",
                license="MIT",
                tags=["chart-generator", "visual-design"],
                capabilities=["chart-generator", "visual-design", "data-analysis"],
                risk_level="low",
                preview_url="mock://skill_chart_generator",
                installable=True,
            ),
        ]

    def search(self, request: SkillSearchRequest) -> list[SkillSearchResult]:
        keyword = request.keyword.strip().lower()
        tags = {item.lower() for item in request.tags}
        capabilities = {item.lower() for item in request.capabilities}
        results: list[SkillSearchResult] = []
        for item in self._catalog:
            haystack = " ".join(
                [item.id, item.name, item.description, " ".join(item.tags), " ".join(item.capabilities)]
            ).lower()
            if keyword and keyword not in haystack:
                continue
            if tags and not tags.intersection({value.lower() for value in item.tags}):
                continue
            if capabilities and not capabilities.intersection({value.lower() for value in item.capabilities}):
                continue
            results.append(item)
        return results
