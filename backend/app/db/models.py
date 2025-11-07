from datetime import datetime
from sqlalchemy import Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .engine import Base


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    file_name: Mapped[str] = mapped_column(String, nullable=False)
    sha256: Mapped[str] = mapped_column(String, nullable=False, index=True)
    mime: Mapped[str] = mapped_column(String, nullable=False)
    lang: Mapped[str] = mapped_column(String, nullable=True)
    tags: Mapped[dict] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    snapshots: Mapped[list["ResumeSnapshot"]] = relationship(back_populates="resume", cascade="all, delete-orphan")


class ResumeSnapshot(Base):
    __tablename__ = "resume_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id", ondelete="CASCADE"))
    data: Mapped[dict] = mapped_column(JSON)
    lang: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    resume: Mapped[Resume] = relationship(back_populates="snapshots")


class Generation(Base):
    __tablename__ = "generations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True)
    job_hash: Mapped[str] = mapped_column(String, index=True)
    type: Mapped[str] = mapped_column(String)  # 'short' | 'letter'
    provider: Mapped[str] = mapped_column(String)
    model: Mapped[str] = mapped_column(String)
    temperature: Mapped[float] = mapped_column()
    top_p: Mapped[float] = mapped_column()
    seed: Mapped[int] = mapped_column(default=0)
    params: Mapped[dict] = mapped_column(JSON)
    prompt: Mapped[str] = mapped_column(String)
    timings: Mapped[dict] = mapped_column(JSON)
    tokens: Mapped[dict] = mapped_column(JSON, default=dict)
    output_path: Mapped[str] = mapped_column(String, nullable=True)
    output_summary: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

