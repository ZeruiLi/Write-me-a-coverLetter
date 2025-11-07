from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings, ensure_storage_dirs
from .core.errors import register_exception_handlers
from .db.engine import create_all
from .routers import resumes, jobs, generate, exports, audit
from .routers import extract_llm, letter2


def create_app() -> FastAPI:
    app = FastAPI(title="Write me a Cover Letter API")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    app.include_router(resumes.router, prefix="/api")
    app.include_router(jobs.router, prefix="/api")
    app.include_router(generate.router, prefix="/api")
    app.include_router(extract_llm.router, prefix="/api")
    app.include_router(letter2.router, prefix="/api")
    app.include_router(exports.router)
    app.include_router(audit.router, prefix="/api")

    @app.get("/healthz")
    def healthz():
        return {"ok": True}

    @app.on_event("startup")
    def on_startup():
        ensure_storage_dirs()
        create_all()

    return app


app = create_app()
