from __future__ import annotations

from pathlib import Path
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from ..core.config import settings
from ..db import models
from ..db.session import get_session
from ..schemas.export import ExportPDFRequest
from ..services.render import html_to_pdf


router = APIRouter(prefix="/api/exports", tags=["exports"])


@router.post("/letter/pdf")
def export_letter_pdf(req: ExportPDFRequest, db: Session = Depends(get_session)):
    html = req.html
    gen = None
    if req.genId is not None:
        gen = db.get(models.Generation, req.genId)
        if gen and (not html):
            # load from file if exists; else from output_summary/params not appropriate
            html = gen.output_path and Path(gen.output_path).exists() and Path(gen.output_path).read_text(encoding="utf-8") or html
    if not html:
        from ..core.errors import AppError
        raise AppError("no_html", 400, "No HTML provided and genId not found")

    pdf_bytes = html_to_pdf(html, req.options.model_dump())
    # Save under storage/exports/{genId}
    if gen:
        out_dir = settings.storage_exports / str(gen.id)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "letter.pdf"
        out_path.write_bytes(pdf_bytes)
        gen.output_path = str(out_path)
    return Response(content=pdf_bytes, media_type="application/pdf")

