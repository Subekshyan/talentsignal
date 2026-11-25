"""SQLAlchemy models, following docs/er_diagram.md.

Dev uses create_all(); switch to Alembic migrations before the first real deployment.
Deleting a user cascades to their CVs, parsed sections, match runs and tracking rows.
"""
from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy import (JSON, Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text,
                        UniqueConstraint, Uuid, func)
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


def pk() -> Mapped[uuid.UUID]:
    return mapped_column(Uuid, primary_key=True, default=uuid.uuid4)


def fk(table: str, nullable: bool = False, ondelete: str = "CASCADE"):
    return mapped_column(Uuid, ForeignKey(f"{table}.id", ondelete=ondelete), nullable=nullable, index=True)


def now():
    return mapped_column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = pk()
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[dt.datetime] = now()


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"
    id: Mapped[uuid.UUID] = pk()
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    experience_level: Mapped[str | None] = mapped_column(String(50))
    preferred_roles: Mapped[str | None] = mapped_column(Text)
    preferred_locations: Mapped[str | None] = mapped_column(Text)


class CVDocument(Base):
    __tablename__ = "cv_documents"
    id: Mapped[uuid.UUID] = pk()
    user_id: Mapped[uuid.UUID] = fk("users")
    file_path: Mapped[str] = mapped_column(String(500))
    file_type: Mapped[str] = mapped_column(String(10))
    uploaded_at: Mapped[dt.datetime] = now()
    delete_after: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True))  # retention rule


class ParsedCVSection(Base):
    __tablename__ = "parsed_cv_sections"
    id: Mapped[uuid.UUID] = pk()
    cv_id: Mapped[uuid.UUID] = fk("cv_documents")
    section_type: Mapped[str] = mapped_column(String(30))
    raw_text: Mapped[str] = mapped_column(Text)
    user_verified: Mapped[bool] = mapped_column(Boolean, default=False)


class Skill(Base):
    __tablename__ = "skills"
    id: Mapped[uuid.UUID] = pk()
    name: Mapped[str] = mapped_column(String(100), unique=True)
    category: Mapped[str | None] = mapped_column(String(30))
    aliases: Mapped[str | None] = mapped_column(Text)


class CandidateSkill(Base):
    __tablename__ = "candidate_skills"
    profile_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("candidate_profiles.id", ondelete="CASCADE"), primary_key=True)
    skill_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True)
    source: Mapped[str | None] = mapped_column(String(30))  # parsed | user_added
    user_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)


class Education(Base):
    __tablename__ = "education"
    id: Mapped[uuid.UUID] = pk()
    profile_id: Mapped[uuid.UUID] = fk("candidate_profiles")
    degree: Mapped[str | None] = mapped_column(String(100))
    field: Mapped[str | None] = mapped_column(String(100))
    end_year: Mapped[int | None] = mapped_column(Integer)


class Experience(Base):
    __tablename__ = "experience"
    id: Mapped[uuid.UUID] = pk()
    profile_id: Mapped[uuid.UUID] = fk("candidate_profiles")
    title: Mapped[str] = mapped_column(String(150))
    kind: Mapped[str] = mapped_column(String(20), default="employment")  # employment | internship
    start_date: Mapped[dt.date | None] = mapped_column(Date)
    end_date: Mapped[dt.date | None] = mapped_column(Date)


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[uuid.UUID] = pk()
    profile_id: Mapped[uuid.UUID] = fk("candidate_profiles")
    title: Mapped[str] = mapped_column(String(150))
    description: Mapped[str | None] = mapped_column(Text)


class Certification(Base):
    __tablename__ = "certifications"
    id: Mapped[uuid.UUID] = pk()
    profile_id: Mapped[uuid.UUID] = fk("candidate_profiles")
    name: Mapped[str] = mapped_column(String(150))
    issuer: Mapped[str | None] = mapped_column(String(150))


class Company(Base):
    __tablename__ = "companies"
    id: Mapped[uuid.UUID] = pk()
    name: Mapped[str] = mapped_column(String(200), unique=True)
    website: Mapped[str | None] = mapped_column(String(300))


class JobSource(Base):
    __tablename__ = "job_sources"
    id: Mapped[uuid.UUID] = pk()
    name: Mapped[str] = mapped_column(String(100))
    base_url: Mapped[str | None] = mapped_column(String(300))
    access_method: Mapped[str] = mapped_column(String(30), default="manual")  # manual | search_api | feed | crawl
    allowed: Mapped[bool] = mapped_column(Boolean, default=False)  # only True once permission is verified


class JobListing(Base):
    __tablename__ = "job_listings"
    id: Mapped[uuid.UUID] = pk()
    company_id: Mapped[uuid.UUID | None] = fk("companies", nullable=True, ondelete="SET NULL")
    source_id: Mapped[uuid.UUID | None] = fk("job_sources", nullable=True, ondelete="SET NULL")
    title: Mapped[str] = mapped_column(String(250))
    description: Mapped[str] = mapped_column(Text)
    source_url: Mapped[str] = mapped_column(String(800), unique=True)
    location: Mapped[str | None] = mapped_column(String(150))
    deadline: Mapped[dt.date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default="unknown")  # active | expired | unknown
    first_seen: Mapped[dt.datetime] = now()
    last_checked: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True))


class JobRequirement(Base):
    __tablename__ = "job_requirements"
    id: Mapped[uuid.UUID] = pk()
    job_id: Mapped[uuid.UUID] = fk("job_listings")
    skill_id: Mapped[uuid.UUID | None] = fk("skills", nullable=True, ondelete="SET NULL")
    req_type: Mapped[str] = mapped_column(String(20))  # skill | experience | education | other
    mandatory: Mapped[bool] = mapped_column(Boolean, default=True)
    text: Mapped[str] = mapped_column(Text)


class JobSearchQuery(Base):
    __tablename__ = "job_search_queries"
    id: Mapped[uuid.UUID] = pk()
    user_id: Mapped[uuid.UUID] = fk("users")
    keywords: Mapped[str] = mapped_column(String(300))
    filters: Mapped[dict | None] = mapped_column(JSON)
    notify: Mapped[bool] = mapped_column(Boolean, default=False)


class MatchRun(Base):
    __tablename__ = "match_runs"
    id: Mapped[uuid.UUID] = pk()
    user_id: Mapped[uuid.UUID] = fk("users")
    cv_id: Mapped[uuid.UUID] = fk("cv_documents")
    job_id: Mapped[uuid.UUID] = fk("job_listings")
    suitability_score: Mapped[float] = mapped_column(Float)
    method_version: Mapped[str] = mapped_column(String(50))  # e.g. "hybrid-v0.1"
    created_at: Mapped[dt.datetime] = now()


class RequirementMatch(Base):
    __tablename__ = "requirement_matches"
    id: Mapped[uuid.UUID] = pk()
    run_id: Mapped[uuid.UUID] = fk("match_runs")
    requirement_id: Mapped[uuid.UUID] = fk("job_requirements")
    status: Mapped[str] = mapped_column(String(20))  # matched | partial | needs_review | not_demonstrated
    confidence: Mapped[float] = mapped_column(Float, default=0.0)


class MatchEvidence(Base):
    __tablename__ = "match_evidence"
    id: Mapped[uuid.UUID] = pk()
    match_id: Mapped[uuid.UUID] = fk("requirement_matches")
    cv_section_id: Mapped[uuid.UUID | None] = fk("parsed_cv_sections", nullable=True, ondelete="SET NULL")
    snippet: Mapped[str] = mapped_column(Text)
    method: Mapped[str] = mapped_column(String(20))


class SkillGap(Base):
    __tablename__ = "skill_gaps"
    id: Mapped[uuid.UUID] = pk()
    run_id: Mapped[uuid.UUID] = fk("match_runs")
    skill_id: Mapped[uuid.UUID | None] = fk("skills", nullable=True, ondelete="SET NULL")
    gap_type: Mapped[str] = mapped_column(String(20))  # not_demonstrated | partial
    priority: Mapped[str] = mapped_column(String(10), default="medium")


class Recommendation(Base):
    __tablename__ = "recommendations"
    id: Mapped[uuid.UUID] = pk()
    gap_id: Mapped[uuid.UUID] = fk("skill_gaps")
    action_type: Mapped[str] = mapped_column(String(30))  # learn | build_project | clarify_cv
    advice: Mapped[str] = mapped_column(Text)
    done: Mapped[bool] = mapped_column(Boolean, default=False)


class JobApplication(Base):
    """'Saved' is simply the first status; there is no separate SavedJob table."""
    __tablename__ = "job_applications"
    __table_args__ = (UniqueConstraint("user_id", "job_id"),)
    id: Mapped[uuid.UUID] = pk()
    user_id: Mapped[uuid.UUID] = fk("users")
    job_id: Mapped[uuid.UUID] = fk("job_listings")
    status: Mapped[str] = mapped_column(String(20), default="saved")
    applied_on: Mapped[dt.date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)
    reminder_at: Mapped[dt.date | None] = mapped_column(Date)


class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[uuid.UUID] = pk()
    user_id: Mapped[uuid.UUID] = fk("users")
    job_id: Mapped[uuid.UUID | None] = fk("job_listings", nullable=True, ondelete="SET NULL")
    type: Mapped[str] = mapped_column(String(30))
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
