from typing import TypeVar, Generic, Optional, Any, Dict
from fastapi import status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from starlette.responses import JSONResponse

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    data: Optional[T] = None
    status_code: int
    success: bool
    message: str
    total_pages: Optional[int] = None
    

    class Config:
        arbitrary_types_allowed = True


def success_response(data: Any = None, message: str = "Operation completed successfully",
                     status_code: int = status.HTTP_200_OK, total_pages: Optional[int] = None) -> Dict[str, Any]:
    return {
        "data": jsonable_encoder(data),
        "status_code": status_code,
        "success": True,
        "message": message,
        "total_pages": total_pages
    }


def error_response(message: str = "An error occurred", status_code: int = status.HTTP_400_BAD_REQUEST,
                   data: Any = None, total_pages: Optional[int] = None) -> Dict[str, Any]:
    return {
        "data": jsonable_encoder(data),
        "status_code": status_code,
        "success": False,
        "message": message,
        "total_pages": total_pages
    }


def create_response(data: Any = None, message: str = None, status_code: int = status.HTTP_200_OK,
                    success: bool = None, total_pages: Optional[int] = None) -> JSONResponse:
    if success is None:
        success = 200 <= status_code < 400

    if message is None:
        message = "Operation completed successfully" if success else "An error occurred"

    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder({
            "data": data,
            "status_code": status_code,
            "success": success,
            "message": message,
            "total_pages": total_pages
        })
    )
