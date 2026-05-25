import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.config import get_settings

settings = get_settings()

app = FastAPI(title="PPT Agent", version="v0.2.0-dev")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.get("/")
def root():
    index_path = _frontend_dist_dir() / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"name": app.title, "status": "ok"}


def _frontend_dist_dir() -> Path:
    candidates = []
    if getattr(sys, "frozen", False):
        meipass = Path(getattr(sys, "_MEIPASS", Path.cwd()))
        candidates.extend(
            [
                meipass / "frontend" / "dist",
                Path(sys.executable).resolve().parent / "frontend" / "dist",
            ]
        )
    candidates.extend(
        [
            Path.cwd().parent / "frontend" / "dist",
            Path.cwd() / "frontend" / "dist",
            Path(__file__).resolve().parents[2] / "frontend" / "dist",
        ]
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def frontend_dist_available() -> bool:
    return _frontend_dist_dir().joinpath("index.html").exists()


frontend_dist = _frontend_dist_dir()
if frontend_dist.exists():
    assets_dir = frontend_dist / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
