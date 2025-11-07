import os
from dotenv import load_dotenv
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./storage/app.db")
    model_provider: str = os.getenv("MODEL_PROVIDER", "gemini")
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    ocr_enabled: bool = os.getenv("OCR_ENABLED", "true").lower() == "true"
    pdf_renderer: str = os.getenv("PDF_RENDERER", "chromium")
    default_output_lang: str = os.getenv("DEFAULT_OUTPUT_LANG", "auto")
    api_port: int = int(os.getenv("API_PORT", "8000"))

    storage_root: Path = Path("storage")
    storage_resumes: Path = Path("storage/resumes")
    storage_exports: Path = Path("storage/exports")
    storage_audit: Path = Path("storage/audit")


load_dotenv()
settings = Settings()


def ensure_storage_dirs() -> None:
    settings.storage_resumes.mkdir(parents=True, exist_ok=True)
    settings.storage_exports.mkdir(parents=True, exist_ok=True)
    settings.storage_audit.mkdir(parents=True, exist_ok=True)
