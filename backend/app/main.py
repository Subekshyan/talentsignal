from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from talentsignal_matching import METHODS, analyze

from . import models  # noqa: F401  (registers tables)
from .db import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)  # dev only; use Alembic for real deployments
    yield


app = FastAPI(title="TalentSignal API", version="0.1.0", lifespan=lifespan)


class MatchRequest(BaseModel):
    cv_text: str = Field(min_length=20)
    jd_text: str = Field(min_length=20)
    method: str = "hybrid"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/match")
def match(req: MatchRequest):
    """Stateless matching endpoint (Phase 1 bridge). Later versions will read the
    CV and job from the database and persist a MatchRun."""
    if req.method not in METHODS:
        raise HTTPException(400, f"method must be one of {list(METHODS)}")
    try:
        return analyze(req.cv_text, req.jd_text, req.method).to_dict()
    except RuntimeError as exc:  # e.g. sentence-transformers missing for method=sbert
        raise HTTPException(503, str(exc)) from exc
