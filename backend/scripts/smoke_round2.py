import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.agents.critic_agent import CriticAgent
from app.agents.deck_planner_agent import DeckPlannerAgent
from app.agents.grounding_checker import GroundingChecker
from app.agents.paper_summary_agent import PaperSummaryAgent
from app.agents.regenerate_slide_agent import RegenerateSlideAgent
from app.agents.repair_agent import RepairAgent
from app.agents.slide_writer_agent import SlideWriterAgent
from app.llm.providers import MockLLMProvider
from app.ppt.ppt_builder import PPTBuilder
from app.schemas.assets import ExtractedAssets
from app.schemas.common import GenerationSettings
from app.schemas.deck import DeckPlan, PaperSummary, SlideDrafts
from app.schemas.paper import ParsedPaper
from app.schemas.profile import UserProfile
from app.utils.profile_utils import profile_to_settings


def load_fixture(name: str):
    path = ROOT / "tests" / "fixtures" / name
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    profile = UserProfile(**load_fixture("mock_profile_zh_reading_group.json"))
    paper = ParsedPaper(**load_fixture("mock_parsed_paper.json"))
    assets = ExtractedAssets(**load_fixture("mock_extracted_assets.json"))
    settings = profile_to_settings(profile)
    llm = MockLLMProvider(paper)

    summary = PaperSummaryAgent(llm).run(paper)
    plan = DeckPlannerAgent(llm).run(paper, summary, settings, profile, assets)
    drafts = SlideWriterAgent(llm).run(paper, summary, plan, profile, assets)
    grounding = GroundingChecker().run(drafts)
    critic = CriticAgent().run(drafts, grounding, profile)
    repaired, history = RepairAgent().run(paper, drafts, critic, profile, assets, max_loops=2)

    output_dir = ROOT / "storage" / "round2_smoke"
    output_dir.mkdir(parents=True, exist_ok=True)
    pptx_path = output_dir / "final_deck.pptx"
    PPTBuilder().build(pptx_path, summary, plan, repaired, settings)
    if not pptx_path.exists():
        raise RuntimeError("Round 2 smoke failed: PPTX missing after initial build.")

    regenerated = RegenerateSlideAgent(SlideWriterAgent(llm)).run(
        paper,
        summary,
        plan,
        repaired,
        ["slide_02"],
        "Make this slide more visual and reduce text.",
        profile,
        assets,
    )
    PPTBuilder().build(pptx_path, summary, plan, regenerated, settings)
    if not pptx_path.exists():
        raise RuntimeError("Round 2 smoke failed: PPTX missing after slide regeneration.")
    print(f"ROUND2_SMOKE_OK {pptx_path}")


if __name__ == "__main__":
    main()
