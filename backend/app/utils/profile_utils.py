from __future__ import annotations

from uuid import uuid4

from app.schemas.common import GenerationSettings
from app.schemas.profile import CreateProfileRequest, UserProfile


def default_profiles() -> list[UserProfile]:
    presets = [
        CreateProfileRequest(
            name="Chinese Graduate Reading Group",
            audience="graduate",
            presentation_goal="critique",
            preferred_language="zh",
            tone="academic",
            slide_count_target=14,
            talk_duration_minutes=18,
            math_level="balanced",
            include_speaker_notes=True,
            include_limitations=True,
            include_discussion_questions=True,
            include_source_footers=True,
            theme_id="academic_clean",
            brand_colors=["#1d4ed8", "#0f172a"],
        ),
        CreateProfileRequest(
            name="English Expert Conference Talk",
            audience="expert",
            presentation_goal="persuade",
            preferred_language="en",
            tone="technical",
            slide_count_target=12,
            talk_duration_minutes=15,
            math_level="detailed",
            include_speaker_notes=True,
            include_limitations=True,
            include_discussion_questions=False,
            include_source_footers=True,
            theme_id="dark_modern",
            brand_colors=["#0f172a", "#38bdf8"],
        ),
        CreateProfileRequest(
            name="Bilingual Undergraduate Teaching",
            audience="undergraduate",
            presentation_goal="teach",
            preferred_language="bilingual",
            tone="visual",
            slide_count_target=12,
            talk_duration_minutes=20,
            math_level="simplified",
            include_speaker_notes=True,
            include_limitations=False,
            include_discussion_questions=True,
            include_source_footers=True,
            theme_id="minimalist_white",
            brand_colors=["#0f172a", "#16a34a"],
        ),
        CreateProfileRequest(
            name="Critical Review Lab Meeting",
            audience="lab_meeting",
            presentation_goal="critique",
            preferred_language="en",
            tone="concise",
            slide_count_target=14,
            talk_duration_minutes=12,
            math_level="balanced",
            include_speaker_notes=True,
            include_limitations=True,
            include_discussion_questions=True,
            include_source_footers=True,
            theme_id="academic_clean",
            brand_colors=["#b91c1c", "#0f172a"],
        ),
    ]
    return [UserProfile(id=f"profile_preset_{idx+1}", **payload.model_dump()) for idx, payload in enumerate(presets)]


def profile_to_settings(profile: UserProfile) -> GenerationSettings:
    visual_density = "dense" if profile.audience in {"expert", "thesis_defense"} else "balanced"
    if profile.audience in {"general", "undergraduate"}:
        visual_density = "light"
    return GenerationSettings(
        language=profile.preferred_language,
        audience=profile.audience,
        slide_count=profile.slide_count_target,
        include_speaker_notes=profile.include_speaker_notes,
        include_source_footers=profile.include_source_footers,
        theme=profile.theme_id,
        presentation_goal=profile.presentation_goal,
        tone=profile.tone,
        math_level=profile.math_level,
        include_limitations=profile.include_limitations,
        include_discussion_questions=profile.include_discussion_questions,
        talk_duration_minutes=profile.talk_duration_minutes,
        visual_density=visual_density,
    )


def build_inline_profile(name: str, settings: GenerationSettings) -> UserProfile:
    return UserProfile(
        id=f"profile_inline_{uuid4().hex[:8]}",
        name=name,
        audience=settings.audience,
        presentation_goal=settings.presentation_goal,
        preferred_language=settings.language,
        tone=settings.tone,
        slide_count_target=settings.slide_count,
        talk_duration_minutes=settings.talk_duration_minutes,
        math_level=settings.math_level,
        include_speaker_notes=settings.include_speaker_notes,
        include_limitations=settings.include_limitations,
        include_discussion_questions=settings.include_discussion_questions,
        include_source_footers=settings.include_source_footers,
        theme_id=settings.theme,
        brand_colors=[],
        title_font="Aptos Display",
        body_font="Aptos",
        custom_instructions="",
        long_generation_instruction="",
    )
