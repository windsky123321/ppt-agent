from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas.assets import ExtractedAsset


class BaseVisionModel(ABC):
    @abstractmethod
    def describe_asset(self, asset: ExtractedAsset) -> ExtractedAsset:
        raise NotImplementedError


class MockVisionModel(BaseVisionModel):
    def describe_asset(self, asset: ExtractedAsset) -> ExtractedAsset:
        caption = asset.original_caption or asset.nearby_text or f"{asset.asset_type.title()} on page {asset.page_number}"
        lowered = caption.lower()
        usage = "unused"
        if "figure" in lowered or "architecture" in lowered or "attention" in lowered:
            usage = "method"
        if "result" in lowered or "bleu" in lowered or "table" in lowered:
            usage = "result"
        asset.short_visual_description = caption[:180]
        asset.technical_interpretation = (asset.nearby_text or caption)[:220]
        asset.why_it_matters = f"This {asset.asset_type} appears relevant to explaining the paper's {usage} evidence."
        asset.suggested_slide_usage = usage
        asset.importance_score = min(1.0, 0.45 + (0.2 if usage in {"method", "result"} else 0.0) + (0.1 if asset.asset_type == "table" else 0.0))
        return asset
