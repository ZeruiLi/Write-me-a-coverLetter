from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    def __init__(self, code: str, http: int = 400, msg: str | None = None, detail: dict | None = None) -> None:
        self.code = code
        self.http = http
        self.msg = msg or code
        self.detail = detail or {}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError):  # type: ignore
        return JSONResponse(status_code=exc.http, content={"code": exc.code, "message": exc.msg, "detail": exc.detail})

    @app.exception_handler(Exception)
    async def unhandled_error(_: Request, exc: Exception):  # type: ignore
        return JSONResponse(status_code=500, content={"code": "internal_error", "message": str(exc)})

