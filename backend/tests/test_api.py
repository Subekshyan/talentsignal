from pathlib import Path

from fastapi.testclient import TestClient

from app.db import Base, SessionLocal, engine
from app.main import app
from app import models

SAMPLES = Path(__file__).resolve().parents[2] / "data" / "samples"


def test_health_and_match():
    with TestClient(app) as client:
        assert client.get("/health").json() == {"status": "ok"}
        body = {
            "cv_text": (SAMPLES / "cv_sample.txt").read_text(),
            "jd_text": (SAMPLES / "jd_data_analyst.txt").read_text(),
            "method": "keyword",
        }
        r = client.post("/api/match", json=body)
        assert r.status_code == 200
        data = r.json()
        assert 0 <= data["score"] <= 100
        assert "not a probability" in data["disclaimer"]

        assert client.post("/api/match", json={**body, "method": "bogus"}).status_code == 400


def test_models_create_and_track_application():
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        user = models.User(email="a@example.com", password_hash="x")
        job = models.JobListing(title="Junior Data Analyst", description="d", source_url="https://example.com/job/1")
        db.add_all([user, job])
        db.commit()
        db.add(models.JobApplication(user_id=user.id, job_id=job.id))
        db.commit()
        app_row = db.query(models.JobApplication).one()
        assert app_row.status == "saved"
        assert job.status == "unknown"
