import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app import models  # noqa: F401 - registers models with Base
from app.api import entries, lookups, users, auth, snapshots

# Create tables on startup (schema sbfo_ro must already exist in PostgreSQL)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SBFO R&O Tracker API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(entries.router, prefix="/api/entries", tags=["entries"])
app.include_router(lookups.router, prefix="/api/lookups", tags=["lookups"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(snapshots.router, prefix="/api/snapshots", tags=["snapshots"])


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8008, reload=True)
