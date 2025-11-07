from contextlib import contextmanager
from typing import Iterator
from .engine import SessionLocal


@contextmanager
def get_session() -> Iterator:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

