import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.agents.critic_agent import CriticAgent
from app.agents.deck_planner_agent import DeckPlannerAgent
from app.agents.grounding_checker import GroundingChecker
from app.agents.paper_summary_agent import PaperSummaryAgent
from app.agents.regenerate_slide_agent import RegenerateSlideAgent
from app.agents.repair_agent import RepairAgent
from app.agents.slide_writer_agent import SlideWriterAgent
from app.llm.providers import MockLLMProvider
from app.main import app
from app.schemas.assets import ExtractedAsset, ExtractedAssets
from app.schemas.common import GenerationSettings
from app.schemas.deck import CriticReport, SlideDrafts
from app.schemas.paper import ParsedPaper
from app.schemas.profile import CreateProfileRequest, UserProfile
from app.storage.profile_storage import ProfileStorage
from app.utils.profile_utils import profile_to_settings
from app.vision.providers import MockVisionModel


def load_fixture(name: str):
    path = Path(__file__).parent / "fixtures" / name
    return json.loads(path.read_text(encoding="utf-8"))


def load_profile() -> UserProfile:
    return UserProfile(**load_fixture("mock_profile_zh_reading_group.json"))


def load_paper() -> ParsedPaper:
    return ParsedPaper(**load_fixture("mock_parsed_paper.json"))


def load_assets() -> ExtractedAssets:
    return ExtractedAssets(**load_fixture("mock_extracted_assets.json"))


def test_profile_validation_and_mapping():
    profile = load_profile()
    settings = profile_to_settings(profile)
    assert settings.language == "zh"
    assert settings.slide_count == 14
    assert settings.include_discussion_questions is True


def test_profile_crud(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("STORAGE_DIR", str(tmp_path / "storage"))
    storage = ProfileStorage()
    created = storage.create_profile(CreateProfileRequest(name="Test Profile"))
    fetched = storage.get_profile(created.id)
    assert fetched.name == "Test Profile"
    fetched.name = "Updated Profile"
    storage.save_profile(fetched)
    assert storage.get_profile(created.id).name == "Updated Profile"
    storage.delete_profile(created.id)
    assert all(profile.id != created.id for profile in storage.list_profiles())


def test_mock_vision_and_asset_ranking():
    asset = ExtractedAsset(
        id="asset_1",
        asset_type="figure",
        page_number=2,
        original_caption="Figure 1: Architecture overview.",
        nearby_text="The method architecture uses grounded steps.",
        source_reference="p. 2, Fig. 1",
    )
    described = MockVisionModel().describe_asset(asset)
    assert described.importance_score > 0
    assert described.suggested_slide_usage == "method"


def test_profile_affects_deck_plan_and_slide_language():
    paper = load_paper()
    profile = load_profile()
    settings = profile_to_settings(profile)
    llm = MockLLMProvider(paper)
    summary = PaperSummaryAgent(llm).run(paper)
    plan = DeckPlannerAgent(llm).run(paper, summary, settings, profile, load_assets())
    drafts = SlideWriterAgent(llm).run(paper, summary, plan, profile, load_assets())
    assert plan.slide_count >= 10
    assert any("（中文）" in slide.title for slide in drafts.slides if slide.slide_type != "title")


def test_critic_and_repair_loop_behavior():
    paper = load_paper()
    profile = load_profile()
    drafts = SlideDrafts(**load_fixture("mock_slide_drafts.json"))
    grounding = GroundingChecker().run(drafts)
    critic = CriticAgent().run(drafts, grounding, profile)
    assert isinstance(critic, CriticReport)
    repaired, history = RepairAgent().run(paper, drafts, critic, profile, load_assets(), max_loops=2)
    assert history.loops
    repaired_slide = next(slide for slide in repaired.slides if slide.slide_id == "slide_02")
    assert repaired_slide.speaker_notes
    assert repaired_slide.source_refs or repaired_slide.visual_elements


def test_selected_slide_regeneration_and_artifact_endpoint(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("STORAGE_DIR", str(tmp_path / "storage"))
    client = TestClient(app)
    profile_response = client.post("/api/profiles", json={"name": "Round2 Profile", "preferred_language": "en"})
    assert profile_response.status_code == 200
    fixture = Path(__file__).parent / "fixtures" / "sample_paper.pdf"
    with fixture.open("rb") as handle:
        upload = client.post(
            "/api/papers/upload",
            data={"profile_id": profile_response.json()["id"]},
            files={"file": ("sample_paper.pdf", handle, "application/pdf")},
        )
    assert upload.status_code == 200, upload.text
    deck_id = upload.json()["job"]["deck_id"]
    regen = client.post(
        f"/api/decks/{deck_id}/regenerate-slide",
        json={"slide_ids": ["slide_02"], "instruction": "Make this slide more visual and reduce text."},
    )
    assert regen.status_code == 200, regen.text
    artifacts = client.get(f"/api/decks/{deck_id}/artifacts")
    assert artifacts.status_code == 200
    artifact_names = {item["name"] for item in artifacts.json()["artifacts"] if item["exists"]}
    assert "critic_report.json" in artifact_names
    assert "final_deck.pptx" in artifact_names
