from pathlib import Path

from app.agents.deck_planner_agent import DeckPlannerAgent
from app.agents.paper_summary_agent import PaperSummaryAgent
from app.agents.regenerate_slide_agent import RegenerateSlideAgent
from app.agents.slide_writer_agent import SlideWriterAgent
from app.llm.providers import MockLLMProvider
from app.parser.pdf_parser import PDFParser
from app.schemas.assets import ExtractedAssets
from app.schemas.common import GenerationSettings
from app.schemas.profile import UserProfile


def load_sample_paper():
    fixture = Path(__file__).parent / "fixtures" / "sample_paper.pdf"
    return PDFParser().parse(fixture, paper_id="paper_low_token")


def build_profile(include_notes: bool = False) -> UserProfile:
    return UserProfile(
        id="profile_low_token",
        name="Low Token Exec",
        audience="graduate",
        presentation_goal="summarize",
        preferred_language="zh",
        tone="concise",
        slide_count_target=8,
        talk_duration_minutes=10,
        math_level="balanced",
        include_speaker_notes=include_notes,
        include_limitations=True,
        include_discussion_questions=False,
        include_source_footers=True,
        theme_id="academic_clean",
        brand_colors=["#1d4ed8"],
        title_font="Microsoft YaHei",
        body_font="Microsoft YaHei",
        custom_instructions="请使用管理层汇报风格，表达精炼，重点清晰。",
        long_generation_instruction="总页数 8 页，中文，像商业汇报一样简洁专业。",
    )


def test_scenario_a_first_generation_quality():
    paper = load_sample_paper()
    profile = build_profile(include_notes=False)
    llm = MockLLMProvider(paper)
    summary = PaperSummaryAgent(llm).run(paper)
    plan = DeckPlannerAgent(llm).run(paper, summary, GenerationSettings(slide_count=8, include_speaker_notes=False), profile)
    drafts = SlideWriterAgent(llm).run(paper, summary, plan, profile)

    assert len(drafts.slides) >= 8
    content_slides = [slide for slide in drafts.slides if slide.slide_type not in {"title", "divider"}]
    assert any(slide.key_message for slide in content_slides)
    for slide in content_slides:
        assert len(slide.bullets) <= 3
        for bullet in slide.bullets:
            assert len(bullet) <= 18
    assert all(slide.title.strip() for slide in drafts.slides)
    assert all(len(slide.title) <= 20 for slide in drafts.slides if slide.slide_type != "title")


def test_scenario_b_second_round_only_selected_slides_change():
    paper = load_sample_paper()
    profile = build_profile(include_notes=False)
    llm = MockLLMProvider(paper)
    summary = PaperSummaryAgent(llm).run(paper)
    plan = DeckPlannerAgent(llm).run(paper, summary, GenerationSettings(slide_count=8, include_speaker_notes=False), profile)
    drafts = SlideWriterAgent(llm).run(paper, summary, plan, profile)
    before = {slide.slide_id: (slide.title, list(slide.bullets)) for slide in drafts.slides}

    updated = RegenerateSlideAgent(SlideWriterAgent(llm)).run(
        paper,
        summary,
        plan,
        drafts,
        ["slide_03", "slide_05"],
        "继续优化，只改第 3 页和第 5 页，Make this slide more visual and reduce text.",
        profile,
        assets=ExtractedAssets(),
    )
    after = {slide.slide_id: (slide.title, list(slide.bullets)) for slide in updated.slides}

    changed = [slide_id for slide_id in after if after[slide_id] != before[slide_id]]
    assert set(changed).issubset({"slide_03", "slide_05"})
    unchanged = [slide_id for slide_id in after if slide_id not in {"slide_03", "slide_05"} and after[slide_id] == before[slide_id]]
    assert len(unchanged) == len([slide_id for slide_id in after if slide_id not in {"slide_03", "slide_05"}])


def test_scenario_c_third_round_only_slide_five_and_length_limits():
    paper = load_sample_paper()
    profile = build_profile(include_notes=False)
    llm = MockLLMProvider(paper)
    summary = PaperSummaryAgent(llm).run(paper)
    plan = DeckPlannerAgent(llm).run(paper, summary, GenerationSettings(slide_count=8, include_speaker_notes=False), profile)
    drafts = SlideWriterAgent(llm).run(paper, summary, plan, profile)
    before = {slide.slide_id: (slide.title, list(slide.bullets)) for slide in drafts.slides}

    updated = RegenerateSlideAgent(SlideWriterAgent(llm)).run(
        paper,
        summary,
        plan,
        drafts,
        ["slide_05"],
        "第 3 轮精修，只改 Slide 5 标题和 bullet，patch，reduce text，标题更短。",
        profile,
        assets=ExtractedAssets(),
    )

    changed = [slide for slide in updated.slides if (slide.title, list(slide.bullets)) != before[slide.slide_id]]
    assert len(changed) == 1
    assert changed[0].slide_id == "slide_05"
    assert len(changed[0].title) <= 20
    assert len(changed[0].bullets) <= 3
    for bullet in changed[0].bullets:
        assert len(bullet) <= 18
