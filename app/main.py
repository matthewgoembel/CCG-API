from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .settings import settings
from .db import init_db
from .routers import progress, stats, achievements, leaderboard

app = FastAPI(title="Cool Cyber Games API", version="v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def _startup():
    init_db()

app.include_router(progress.router, prefix="/v1", tags=["progress"])
app.include_router(stats.router, prefix="/v1", tags=["stats"])
app.include_router(achievements.router, prefix="/v1", tags=["achievements"])
app.include_router(leaderboard.router, prefix="/v1", tags=["leaderboard"])
