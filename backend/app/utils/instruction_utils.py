from __future__ import annotations

import re

from app.schemas.common import GenerationSettings
from app.schemas.instructions import ParsedInstructionSpec, PromptMergeReport
from app.schemas.profile import UserProfile
from app.utils.text_utils import safe_truncate


def parse_instruction_rule_based(raw_text: str, language_hint: str = "auto") -> ParsedInstructionSpec:
    text = raw_text.strip()
    lowered = text.lower()
    detected = "zh" if re.search(r"[\u4e00-\u9fff]", text) else "en"
    if language_hint in {"zh", "en", "bilingual"}:
        detected = language_hint

    spec = ParsedInstructionSpec(detected_language=detected, compressed_summary=safe_truncate(text, 800))

    if "研究生" in text or "graduate" in lowered:
        spec.audience = "graduate"
    elif "本科" in text or "undergraduate" in lowered:
        spec.audience = "undergraduate"
    elif "答辩" in text or "thesis defense" in lowered:
        spec.audience = "thesis_defense"
    elif "专家" in text or "expert" in lowered or "conference" in lowered:
        spec.audience = "expert"

    if "组会" in text or "reading group" in lowered or "lab meeting" in lowered:
        spec.presentation_goal = "critique"
    elif "教学" in text or "teach" in lowered:
        spec.presentation_goal = "teach"
    elif "conference" in lowered or "会议" in text:
        spec.presentation_goal = "persuade"
    else:
        spec.presentation_goal = "summarize"

    if "中文" in text:
        spec.preferred_language = "zh"
    elif "双语" in text or "bilingual" in lowered:
        spec.preferred_language = "bilingual"
    elif "英文" in text or "english" in lowered:
        spec.preferred_language = "en"

    if "简洁" in text or "concise" in lowered:
        spec.tone = "concise"
    elif "visual" in lowered or "图表" in text or "更直观" in text or "more visual" in lowered:
        spec.tone = "visual"
    elif "technical" in lowered or "技术" in text:
        spec.tone = "technical"
    else:
        spec.tone = "academic"

    slide_match = re.search(r"(\d+)\s*页", text) or re.search(r"(\d+)\s*slides?", lowered)
    if slide_match:
        spec.slide_count_target = int(slide_match.group(1))

    minutes_match = re.search(r"(\d+)\s*分钟", text) or re.search(r"(\d+)\s*min", lowered)
    if minutes_match:
        spec.talk_duration_minutes = int(minutes_match.group(1))

    if "公式只保留" in text or "avoid formulas" in lowered or "simplify formulas" in lowered:
        spec.math_level = "simplified"
    elif "详细公式" in text or "detailed math" in lowered:
        spec.math_level = "detailed"
    else:
        spec.math_level = "balanced"

    if "每页加演讲稿" in text or "speaker notes" in lowered:
        spec.include_speaker_notes = True
    if "局限性" in text or "limitations" in lowered:
        spec.include_limitations = True
    if "讨论问题" in text or "discussion questions" in lowered:
        spec.include_discussion_questions = True
    if "引用页脚" in text or "来源页脚" in text or "source footer" in lowered:
        spec.include_source_footers = True
    if "图和表" in text or "尽量使用论文里的图和表" in text or "more visual" in lowered:
        spec.visual_preference = "use_paper_figures"

    must_include_rules = [
        ("研究问题", "research problem"),
        ("方法", "method"),
        ("框架", "architecture"),
        ("实验结果", "results"),
        ("局限性", "limitations"),
        ("优点", "strengths"),
        ("讨论问题", "discussion questions"),
    ]
    for key, label in must_include_rules:
        if key in text:
            spec.must_include.append(label)

    if "不要逐字翻译" in text or "do not translate literally" in lowered:
        spec.avoid.append("literal_translation")
    if "不要太花" in text or "not flashy" in lowered:
        spec.style_requirements.append("clean_academic")
    if "像我在组会上讲一样自然" in text:
        spec.style_requirements.append("natural_spoken_style")

    if "背景" in text:
        spec.sections_to_emphasize.append("background")
    if "方法" in text:
        spec.sections_to_emphasize.append("method")
    if "实验" in text or "结果" in text:
        spec.sections_to_emphasize.append("results")
    if "减少公式" in text or "少讲公式" in text:
        spec.sections_to_reduce.append("equations")

    return spec


def merge_profile_with_instruction(
    profile: UserProfile,
    settings: GenerationSettings,
    spec: ParsedInstructionSpec,
    deck_mode: str,
) -> tuple[GenerationSettings, PromptMergeReport]:
    merged = settings.model_copy(deep=True)
    report = PromptMergeReport(
        instruction_length=len(settings.long_instruction),
        compressed_instruction=len(settings.long_instruction) > 4000,
    )

    mode_defaults = {
        "Quick Summary": {"slide_count": 8, "include_discussion_questions": False},
        "Reading Group": {"slide_count": 14, "include_discussion_questions": True},
        "Conference Talk": {"slide_count": 12, "include_discussion_questions": False},
        "Thesis Defense Style": {"slide_count": 18, "include_discussion_questions": True},
        "Deep Technical": {"slide_count": 16, "include_discussion_questions": True},
    }
    for key, value in mode_defaults.get(deck_mode, {}).items():
        setattr(merged, key, value)

    if profile.long_generation_instruction and not merged.long_instruction:
        merged.long_instruction = profile.long_generation_instruction

    if spec.preferred_language and spec.preferred_language != merged.language:
        report.conflict_warnings.append(
            f"Long instruction language overrides profile/default language: {merged.language} -> {spec.preferred_language}"
        )
        merged.language = spec.preferred_language  # type: ignore[assignment]
        report.applied_overrides.append("preferred_language")
    if spec.audience and spec.audience != merged.audience:
        report.conflict_warnings.append(
            f"Long instruction audience overrides profile/default audience: {merged.audience} -> {spec.audience}"
        )
        merged.audience = spec.audience  # type: ignore[assignment]
        report.applied_overrides.append("audience")
    if spec.slide_count_target:
        merged.slide_count = spec.slide_count_target
        report.applied_overrides.append("slide_count_target")
    if spec.tone:
        merged.tone = spec.tone  # type: ignore[assignment]
        report.applied_overrides.append("tone")
    if spec.math_level:
        if merged.math_level != spec.math_level:
            report.conflict_warnings.append(
                f"Long instruction math level overrides profile/default math level: {merged.math_level} -> {spec.math_level}"
            )
        merged.math_level = spec.math_level  # type: ignore[assignment]
        report.applied_overrides.append("math_level")
    if spec.talk_duration_minutes:
        merged.talk_duration_minutes = spec.talk_duration_minutes
        report.applied_overrides.append("talk_duration_minutes")

    for attr in ["include_speaker_notes", "include_limitations", "include_discussion_questions", "include_source_footers"]:
        value = getattr(spec, attr)
        if value is not None:
            setattr(merged, attr, value)
            report.applied_overrides.append(attr)

    return merged, report
