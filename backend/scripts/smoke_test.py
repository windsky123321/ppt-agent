import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.agents.pipeline import PaperToPPTPipeline
from app.schemas.common import GenerationSettings
from app.storage.file_storage import FileStorage


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
    artifact_name = result.download_artifact_name or "final_deck.pptx"
    pptx_path = FileStorage().get_artifact_path(result.job_id, artifact_name)
    if not pptx_path.exists():
        raise RuntimeError(f"Smoke test failed: {artifact_name} was not created.")
    print(f"SMOKE_OK {pptx_path}")


if __name__ == "__main__":
    main()
