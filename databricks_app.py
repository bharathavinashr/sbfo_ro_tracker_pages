"""
Databricks App Entry Point for SBFO R&O Tracker.
Serves the FastAPI backend + Vue frontend (from frontend/dist) as a single app.
"""
import os
import sys
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

# Force DBX auth mode when running inside Databricks Apps
os.environ["AUTH_MODE"] = "DBX"

# Add backend to Python path so 'app' package resolves correctly
backend_path = Path(__file__).parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

# Import FastAPI app from backend
original_cwd = os.getcwd()
try:
    os.chdir(str(backend_path))
    import main
    app = main.app
finally:
    os.chdir(original_cwd)

# Allow all origins (Databricks Apps proxy handles auth)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Locate frontend/dist
def find_frontend_dist() -> Path | None:
    search_bases = [
        Path(__file__).parent,
        Path.cwd(),
        Path("/app/python/source_code"),
    ]
    for base in search_bases:
        dist = base / "frontend" / "dist"
        if dist.exists() and (dist / "index.html").exists():
            return dist
    return None

frontend_dist = find_frontend_dist()

if frontend_dist:
    print(f"✓ Frontend found at: {frontend_dist}")

    # Mount /assets static files
    assets_dir = frontend_dist / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/")
    async def root():
        return FileResponse(str(frontend_dist / "index.html"))

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Let API and built-in doc routes pass through
        if full_path.startswith(("api/", "docs", "redoc", "openapi.json", "assets/")):
            return {"detail": "Not found"}
        return FileResponse(str(frontend_dist / "index.html"))
else:
    print("✗ frontend/dist not found — run 'cd frontend && npm run build' first")

    @app.get("/")
    async def root():
        return {
            "error": "Frontend not built.",
            "fix": "Run 'cd frontend && npm run build'",
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
