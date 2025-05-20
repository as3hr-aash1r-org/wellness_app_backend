from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.schemas.api_response import create_response
from app.api.v1.routes import auth, user, chat
from app.database.base import Base
from app.database.session import engine

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Health & Wellness App API",
 version="1.0.0",
 docs_url="/api/docs",
 openapi_url="/api/openapi.json"
 )

app.include_router(auth.router, prefix="/api")
app.include_router(user.router, prefix="/api")
app.include_router(chat.router, prefix="/api")

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return create_response(
        message=str(exc.detail),
        status_code=exc.status_code,
        success=False
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    error_messages = []

    for error in errors:
        location = "->".join(str(loc) for loc in error["loc"])
        error_messages.append(f"{location}: {error['msg']}")

    return create_response(
        message="Validation error",
        data={"details": error_messages},
        status_code=422,
        success=False
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return create_response(
        message="Internal server error",
        status_code=500,
        success=False
    )
