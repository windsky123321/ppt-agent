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
    pptx_path = Path("storage") / result.job_id / "final_deck.pptx"
    if not pptx_path.exists():
        raise RuntimeError("Smoke test failed: final_deck.pptx was not created.")
    print(f"SMOKE_OK {pptx_path}")


if __name__ == "__main__":
    main()
