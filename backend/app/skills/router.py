from __future__ import annotations

from datetime import datetime, timezone

from app.schemas.skill_library import SkillManifest, SkillUsageRecord
from app.storage.skill_storage import SkillStorage


STAGE_CAPABILITY_MAP = {
    "PDF parsing": ["pdf-parser"],
    "Outline": ["business-report", "academic-defense"],
    "Slide writing": ["writing-polish", "executive-summary", "visual-design", "ppt-template"],
    "Chart generation": ["chart-generator", "data-analysis"],
    "Critic": ["slide-critic"],
    "Repair": ["slide-repair"],
    "Round 2 revision": ["slide-repair", "writing-polish"],
    "Round 3 patch": ["slide-repair", "token-optimizer"],
    "Token optimization": ["token-optimizer"],
}


class SkillRouter:
    def __init__(self) -> None:
        self.storage = SkillStorage()

    def select_for_stage(
        self,
        stage: str,
        *,
        allow_skill_scripts: bool = False,
        allowed_skill_risk_level: str = "low",
        max_skills_per_task: int = 3,
    ) -> list[SkillManifest]:
        allowed_levels = {"low"} if allowed_skill_risk_level == "low" else {"low", "medium"}
        matches = STAGE_CAPABILITY_MAP.get(stage, [])
        selected: list[SkillManifest] = []
        for skill in self.storage.list_skills():
            if not skill.enabled:
                continue
            if skill.risk_level not in allowed_levels and skill.risk_level != "unknown":
                continue
            if not allow_skill_scripts and any(path.endswith((".py", ".ps1", ".bat", ".sh")) for path in skill.entrypoints):
                continue
            if matches and not set(matches).intersection(skill.capabilities):
                continue
            selected.append(skill)
            if len(selected) >= max_skills_per_task:
                break
        return selected

    def build_stage_guidance(
        self, stage: str, selected: list[SkillManifest], max_skill_context_tokens: int = 800
    ) -> tuple[str, list[SkillUsageRecord]]:
        if not selected:
            return "", []
        lines = [f"技能辅助阶段：{stage}。只采纳下列受控建议，不执行外部脚本。"]
        records: list[SkillUsageRecord] = []
        char_budget = max_skill_context_tokens * 2
        for skill in selected:
            parts: list[str] = []
            if skill.suggestions:
                parts.append("建议：" + "；".join(skill.suggestions[:3]))
            if skill.templates:
                parts.append("模板：" + "；".join(skill.templates[:2]))
            if skill.constraints:
                parts.append("约束：" + "；".join(skill.constraints[:3]))
            rendered = f"[{skill.name}] " + " ".join(parts)
            if sum(len(item) for item in lines) + len(rendered) > char_budget:
                break
            lines.append(rendered)
            records.append(
                SkillUsageRecord(
                    skill_id=skill.id,
                    stage=stage,
                    used_at=datetime.now(timezone.utc).isoformat(),
                    suggestions=skill.suggestions[:3],
                    constraints=skill.constraints[:3],
                )
            )
        return "\n".join(lines), records
