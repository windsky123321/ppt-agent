from pathlib import Path

from app.ppt.ppt_builder import PPTBuilder
from app.schemas.common import GenerationSettings
from app.schemas.deck import DeckPlan, PaperSummary, SlideDrafts


def test_ppt_builder_generates_file(tmp_path: Path):
    builder = PPTBuilder()
    summary = PaperSummary(
        title="Sample Paper",
        one_sentence_summary="Summary",
        problem="Problem",
        motivation="Motivation",
        research_gap="Gap",
        key_contributions=["One", "Two"],
        method_overview="Method",
        experiment_setup="Experiments",
        main_results=["Result"],
        strengths=["Strength"],
        limitations=["Limitation"],
        discussion_points=["Question"],
        conclusion="Conclusion",
        keywords=["sample"],
    )
    plan = DeckPlan(
        deck_title="Sample Paper",
        target_audience="graduate",
        language="en",
        slide_count=2,
        slides=[
            {"slide_id": "slide_01", "slide_type": "title", "title": "Title", "purpose": "Purpose", "key_section": ""},
            {"slide_id": "slide_02", "slide_type": "results", "title": "Results", "purpose": "Purpose", "key_section": "results"},
        ],
    )
    drafts = SlideDrafts(
        slides=[
            {"slide_id": "slide_01", "slide_type": "title", "title": "Sample Paper", "subtitle": "Subtitle", "key_message": "Summary", "purpose": "Intro", "bullets": [], "speaker_notes": "Note", "source_refs": [], "confidence": 0.9, "unsupported_claims": []},
            {"slide_id": "slide_02", "slide_type": "result", "title": "Results", "subtitle": "", "key_message": "Key result", "purpose": "Show results", "bullets": ["A", "B"], "speaker_notes": "Note", "source_refs": [{"paper_id": "paper_1", "page_number": 1, "section_title": "Results", "evidence_summary": "Evidence"}], "confidence": 0.9, "unsupported_claims": []},
        ]
    )
    output = tmp_path / "deck.pptx"
    builder.build(output, summary, plan, drafts, GenerationSettings())
    assert output.exists()
    assert output.stat().st_size > 0
