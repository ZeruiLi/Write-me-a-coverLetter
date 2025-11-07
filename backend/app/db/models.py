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


# v1.1 LLM-first extraction tables
class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    kind: Mapped[str] = mapped_column(String)  # 'resume' | 'jd'


class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))
    file_sha256: Mapped[str] = mapped_column(String)
    mime: Mapped[str] = mapped_column(String)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AnchorText(Base):
    __tablename__ = "anchor_texts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    doc_version_id: Mapped[int] = mapped_column(ForeignKey("document_versions.id", ondelete="CASCADE"))
    anchor_sha256: Mapped[str] = mapped_column(String, unique=True)
    text: Mapped[str] = mapped_column()


class ExtractionRun(Base):
    __tablename__ = "extraction_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    doc_version_id: Mapped[int] = mapped_column(ForeignKey("document_versions.id", ondelete="CASCADE"))
    kind: Mapped[str] = mapped_column(String)  # 'resume' | 'jd'
    prompt_version: Mapped[str] = mapped_column(String)
    model: Mapped[str] = mapped_column(String)
    params_json: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ResumeObject(Base):
    __tablename__ = "resume_objects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    doc_version_id: Mapped[int] = mapped_column(ForeignKey("document_versions.id", ondelete="CASCADE"))
    extract_version: Mapped[str] = mapped_column(String)
    prompt_version: Mapped[str] = mapped_column(String)
    model: Mapped[str] = mapped_column(String)
    json: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class JDObject(Base):
    __tablename__ = "jd_objects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    doc_version_id: Mapped[int] = mapped_column(ForeignKey("document_versions.id", ondelete="CASCADE"))
    extract_version: Mapped[str] = mapped_column(String)
    prompt_version: Mapped[str] = mapped_column(String)
    model: Mapped[str] = mapped_column(String)
    json: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class GenerationRun(Base):
    __tablename__ = "generation_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    resume_obj_id: Mapped[int] = mapped_column(ForeignKey("resume_objects.id", ondelete="SET NULL"), nullable=True)
    jd_obj_id: Mapped[int] = mapped_column(ForeignKey("jd_objects.id", ondelete="SET NULL"), nullable=True)
    plan_json_sha: Mapped[str] = mapped_column(String)
    html_sha: Mapped[str] = mapped_column(String)
    model: Mapped[str] = mapped_column(String)
    params_json: Mapped[dict] = mapped_column(JSON, default=dict)
    timings_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
