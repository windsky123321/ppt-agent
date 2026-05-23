from app.schemas.common import GenerationSettings
from app.schemas.deck import DeckPlan, PaperSummary, SlideDrafts


def test_paper_summary_schema():
    summary = PaperSummary(
        title="Test",
        one_sentence_summary="A test summary.",
        problem="Problem",
        motivation="Motivation",
        research_gap="Gap",
        key_contributions=["One"],
        method_overview="Method",
        experiment_setup="Experiments",
        main_results=["Result"],
        strengths=["Strength"],
        limitations=["Limitation"],
        discussion_points=["Question"],
        conclusion="Conclusion",
        keywords=["test"],
    )
    assert summary.title == "Test"


def test_deck_plan_schema():
    plan = DeckPlan(
        deck_title="Deck",
        target_audience="graduate",
        language="en",
        slide_count=10,
        slides=[
            {"slide_id": "slide_01", "slide_type": "title", "title": "Title", "purpose": "Purpose"},
        ],
    )
    assert plan.slides[0].slide_type == "title"


def test_slide_draft_schema():
    drafts = SlideDrafts(
        slides=[
            {
                "slide_id": "slide_01",
                "title": "Title",
                "subtitle": "",
                "key_message": "Message",
                "bullets": ["A", "B"],
                "speaker_notes": "Notes",
                "source_refs": [{"page_number": 1, "section_title": "Abstract", "evidence_summary": "Evidence"}],
                "confidence": 0.8,
                "unsupported_claims": [],
            }
        ]
    )
    assert drafts.slides[0].source_refs[0].page_number == 1


def test_generation_settings_defaults():
    settings = GenerationSettings()
    assert settings.theme == "academic_clean"
