from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db.session import get_session
from ..services.audit import get_audit
from ..schemas.audit import AuditResponse


router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/{genId}", response_model=AuditResponse)
def audit_detail(genId: int, db: Session = Depends(get_session)):
    data = get_audit(db, genId)
    if not data:
        from ..core.errors import AppError
        raise AppError("gen_not_found", 404)
    return AuditResponse(**data)

