from __future__ import annotations

import re
from pathlib import Path
from uuid import uuid4

import fitz

from app.schemas.assets import ExtractedAsset, ExtractedAssets
from app.schemas.paper import ParsedPaper
from app.vision.providers import BaseVisionModel, MockVisionModel
from app.utils.text_utils import normalize_whitespace, safe_truncate


class AssetExtractor:
    def __init__(self, vision_model: BaseVisionModel | None = None) -> None:
        self.vision_model = vision_model or MockVisionModel()

    def extract(self, pdf_path: Path, paper: ParsedPaper, job_dir: Path) -> ExtractedAssets:
        doc = fitz.open(pdf_path)
        assets: list[ExtractedAsset] = []
        asset_dir = job_dir / "assets"
        asset_dir.mkdir(parents=True, exist_ok=True)

        for page_index, page in enumerate(doc, start=1):
            text = page.get_text("text")
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            for idx, line in enumerate(lines):
                if re.match(r"^(Figure|Fig\.)\s*\d+", line, flags=re.IGNORECASE):
                    asset = self._make_asset("figure", page_index, line, lines, idx, asset_dir)
                    assets.append(self.vision_model.describe_asset(asset))
                if re.match(r"^Table\s*\d+", line, flags=re.IGNORECASE):
                    asset = self._make_asset("table", page_index, line, lines, idx, asset_dir)
                    assets.append(self.vision_model.describe_asset(asset))

        ranked = sorted(assets, key=lambda item: item.importance_score, reverse=True)
        return ExtractedAssets(assets=ranked)

    def _make_asset(self, asset_type: str, page_number: int, caption: str, lines: list[str], index: int, asset_dir: Path) -> ExtractedAsset:
        nearby = normalize_whitespace(" ".join(lines[max(0, index - 2) : min(len(lines), index + 3)]))
        asset_id = f"{asset_type}_{uuid4().hex[:8]}"
        image_path = asset_dir / f"{asset_id}.png"
        return ExtractedAsset(
            id=asset_id,
            asset_type=asset_type,
            page_number=page_number,
            original_caption=safe_truncate(caption, 220),
            nearby_text=safe_truncate(nearby, 320),
            image_path=str(image_path),
            source_reference=f"p. {page_number}, {caption.split(':')[0]}",
        )
