"""Main entrypoint for Inspection Paper FastAPI application."""

from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.auth import router as auth_router
from app.api.drive import router as drive_router
from app.api.parser import router as parser_router
from app.api.ai import router as ai_router
from app.core.config import settings

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title=settings.APP_NAME,
    description="Lighthouse International School (LIS) Exam Paper Monitoring System",
    version="1.0.0",
)

# Enable CORS for API flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth_router)
app.include_router(drive_router)
app.include_router(parser_router)
app.include_router(ai_router)

# Mount Static directory
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def serve_index() -> FileResponse:
    """Serve the single-page monitoring dashboard."""
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        return FileResponse(str(BASE_DIR / "code.html"))
    return FileResponse(str(index_file))


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "app": settings.APP_NAME, "env": settings.APP_ENV}
