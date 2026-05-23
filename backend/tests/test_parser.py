from pathlib import Path

from app.parser.pdf_parser import PDFParser


def test_pdf_parser_extracts_basic_content():
    fixture = Path(__file__).parent / "fixtures" / "sample_paper.pdf"
    parsed = PDFParser().parse(fixture, paper_id="paper_test")
    assert parsed.paper_id == "paper_test"
    assert parsed.title
    assert parsed.pages
    assert parsed.sections
