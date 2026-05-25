from app.agents.quality_checker import SlideQualityChecker
from app.agents.repair_agent import RepairAgent
from app.schemas.assets import ExtractedAssets
from app.schemas.deck import QualityReport, SlideDraft, SlideDrafts
from app.schemas.paper import ParsedPaper


def sample_bad_drafts() -> SlideDrafts:
    return SlideDrafts(
        slides=[
            SlideDraft(
                slide_id="slide_01",
                slide_type="results",
                title="这是一个特别长而且明显超出限制的中文标题",
                key_message="Confidence: 0.3",
                bullets=["Method details are uncertain...", "重点展示结果"],
            )
        ]
    )


def sample_paper() -> ParsedPaper:
    return ParsedPaper(
        paper_id="paper_quality",
        title="示例论文",
        authors=["Alice"],
        abstract="本文研究如何将论文内容稳定转换为中文汇报幻灯片。",
        sections=[
            {"title": "Introduction", "text": "论文关注中文汇报质量，指出现有方法存在标题过长、信息空泛等问题。", "page_start": 1, "page_end": 1},
            {"title": "Method", "text": "方法包括内容清洗、中文改写、质量检查与自动修复。", "page_start": 2, "page_end": 2},
            {"title": "Results", "text": "结果表明生成内容更完整，且不再包含占位语和省略号。", "page_start": 3, "page_end": 3},
        ],
        pages=[{"page_number": 1, "text": "示例论文"}],
        figures=[],
        tables=[],
        references=[],
    )


def test_quality_checker_flags_bad_slides():
    report = SlideQualityChecker().run(sample_bad_drafts())
    assert not report.passed
    categories = {issue.category for issue in report.issues}
    assert "title_length" in categories
    assert "confidence" in categories
    assert "placeholder" in categories
    assert "generic_bullet" in categories


def test_repair_agent_fixes_quality_issues():
    drafts, history = RepairAgent().repair_quality(
        sample_paper(),
        sample_bad_drafts(),
        QualityReport(
            passed=False,
            blocked_export=True,
            issue_count=4,
            issues=SlideQualityChecker().run(sample_bad_drafts()).issues,
        ),
        None,
        ExtractedAssets(),
        max_loops=1,
    )
    slide = drafts.slides[0]
    assert history.loops
    assert len(slide.bullets) >= 2
    assert "Confidence" not in slide.key_message
    assert "uncertain" not in " ".join(slide.bullets).lower()
    assert len(slide.title) <= 14
