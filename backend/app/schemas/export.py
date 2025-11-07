from typing import List, Optional
from pydantic import BaseModel, Field


class HeaderOpts(BaseModel):
    enabled: bool = True
    name: Optional[str] = None
    contact: Optional[str] = None


class FontsOpt(BaseModel):
    en: List[str] = Field(default_factory=lambda: ["Inter", "Times New Roman", "Times", "Serif"])
    zh: List[str] = Field(default_factory=lambda: ["Noto Sans CJK", "PingFang SC", "SimSun", "Heiti SC", "Sans-Serif"])


class ExportOptions(BaseModel):
    page: str = "A4"
    margin_cm: float = 2.0
    line_height: float = 1.35
    header: HeaderOpts = HeaderOpts()
    fonts: FontsOpt = FontsOpt()


class ExportPDFRequest(BaseModel):
    genId: Optional[int] = None
    html: Optional[str] = None
    options: ExportOptions = ExportOptions()

