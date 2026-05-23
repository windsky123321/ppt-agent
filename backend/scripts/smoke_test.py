import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.agents.pipeline import PaperToPPTPipeline
from app.schemas.common import GenerationSettings


def main() -> None:
    fixture = ROOT / "tests" / "fixtures" / "sample_paper.pdf"
    if not fixture.exists():
        raise FileNotFoundError(f"Missing fixture: {fixture}")

    pipeline = PaperToPPTPipeline()
    result = pipeline.run(
        pdf_bytes=fixture.read_bytes(),
        original_filename=fixture.name,
        settings=GenerationSettings(),
    )
    candidate_paths = [
        ROOT / "storage" / "decks" / result.deck_id / "final_deck.pptx",
        ROOT / "storage" / result.job_id / "final_deck.pptx",
        Path("storage") / "decks" / result.deck_id / "final_deck.pptx",
        Path("storage") / result.job_id / "final_deck.pptx",
    ]
    pptx_path = next((path for path in candidate_paths if path.exists()), candidate_paths[0])
    if not pptx_path.exists():
        raise RuntimeError("Smoke test failed: final_deck.pptx was not created.")
    print(f"SMOKE_OK {pptx_path}")


if __name__ == "__main__":
    main()
