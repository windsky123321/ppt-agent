from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Theme:
    name: str
    title_font_size: int
    body_font_size: int
    footer_font_size: int
    title_color: Tuple[int, int, int]
    body_color: Tuple[int, int, int]
    accent_color: Tuple[int, int, int]
    background_color: Tuple[int, int, int]
    margin_inch: float


ACADEMIC_CLEAN = Theme(
    name="academic_clean",
    title_font_size=28,
    body_font_size=18,
    footer_font_size=9,
    title_color=(17, 24, 39),
    body_color=(31, 41, 55),
    accent_color=(37, 99, 235),
    background_color=(248, 250, 252),
    margin_inch=0.5,
)

DARK_MODERN = Theme(
    name="dark_modern",
    title_font_size=28,
    body_font_size=18,
    footer_font_size=9,
    title_color=(241, 245, 249),
    body_color=(226, 232, 240),
    accent_color=(56, 189, 248),
    background_color=(15, 23, 42),
    margin_inch=0.5,
)

MINIMALIST_WHITE = Theme(
    name="minimalist_white",
    title_font_size=26,
    body_font_size=17,
    footer_font_size=9,
    title_color=(17, 24, 39),
    body_color=(55, 65, 81),
    accent_color=(22, 163, 74),
    background_color=(255, 255, 255),
    margin_inch=0.6,
)


def get_theme(name: str) -> Theme:
    if name == "dark_modern":
        return DARK_MODERN
    if name == "minimalist_white":
        return MINIMALIST_WHITE
    return ACADEMIC_CLEAN
