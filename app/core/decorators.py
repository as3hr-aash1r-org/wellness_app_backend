from functools import wraps
from typing import Callable
from fastapi import HTTPException
from starlette.responses import JSONResponse
from app.schemas.api_response import create_response


def standardize_response(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)

            if isinstance(result, JSONResponse):
                return result

            if isinstance(result, dict) and all(key in result for key in ["data", "status_code", "success", "message"]):
                return JSONResponse(
                    status_code=result["status_code"],
                    content=result
                )

            return create_response(
                data=result,
                message="Operation completed successfully",
                status_code=200
            )
        except HTTPException as e:
            return create_response(
                message=e.detail,
                status_code=e.status_code,
                success=False
            )
        except Exception as e:
            return create_response(
                message=str(e),
                status_code=500,
                success=False
            )

    return wrapper
