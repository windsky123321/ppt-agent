from pydantic import BaseModel, Field


class ExtractedAsset(BaseModel):
    id: str
    asset_type: str
    page_number: int
    bbox: dict | list | None = None
    original_caption: str
    nearby_text: str = ""
    image_path: str = ""
    short_visual_description: str = ""
    technical_interpretation: str = ""
    why_it_matters: str = ""
    suggested_slide_usage: str = "unused"
    importance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    source_reference: str = ""


class ExtractedAssets(BaseModel):
    assets: list[ExtractedAsset] = Field(default_factory=list)
