from app.agents.deck_planner_agent import DeckPlannerAgent
from app.agents.paper_summary_agent import PaperSummaryAgent
from app.agents.slide_writer_agent import SlideWriterAgent
from app.llm.providers import MockLLMProvider
from app.schemas.common import GenerationSettings
from app.schemas.deck import SlideDrafts
from app.schemas.paper import ParsedPaper


def sample_paper() -> ParsedPaper:
    return ParsedPaper(
        paper_id="paper_1",
        title="Sample Paper",
        authors=["Alice"],
        abstract="This paper studies robust presentation generation for academic papers.",
        sections=[
            {"title": "Introduction", "text": "The paper motivates reliable paper understanding and identifies limitations in manual slide authoring.", "page_start": 1, "page_end": 1},
            {"title": "Method", "text": "The method parses PDFs, extracts sections, and builds editable slides through a structured pipeline.", "page_start": 2, "page_end": 2},
            {"title": "Experiments", "text": "Experiments evaluate local generation quality on sample papers and inspect artifact completeness.", "page_start": 3, "page_end": 3},
            {"title": "Results", "text": "Results show the pipeline produces editable PPTX files with grounded intermediate artifacts.", "page_start": 4, "page_end": 4},
            {"title": "Conclusion", "text": "The paper concludes that a local-first pipeline is feasible for MVP academic presentation generation.", "page_start": 5, "page_end": 5},
        ],
        pages=[{"page_number": 1, "text": "Sample Paper"}],
        figures=[],
        tables=[],
        references=[],
    )


def test_mock_provider_summary():
    provider = MockLLMProvider(sample_paper())
    summary = PaperSummaryAgent(provider).run(sample_paper())
    assert summary.title == "Sample Paper"
    assert "PDF" in summary.method_overview or "解析" in summary.method_overview
    assert "PPT" in " ".join(summary.main_results) or "结果" in " ".join(summary.main_results)
    assert "uncertain" not in summary.method_overview.lower()


def test_mock_provider_slide_drafts():
    provider = MockLLMProvider(sample_paper())
    paper = sample_paper()
    summary = PaperSummaryAgent(provider).run(paper)
    plan = DeckPlannerAgent(provider).run(paper, summary, GenerationSettings(slide_count=12))
    drafts = SlideWriterAgent(provider).run(paper, summary, plan)
    assert isinstance(drafts, SlideDrafts)
    method_slide = next(slide for slide in drafts.slides if slide.slide_type == "method")
    assert any(ref.section_title == "Method" for ref in method_slide.source_refs)
    assert method_slide.speaker_notes
    assert "Confidence" not in method_slide.key_message
