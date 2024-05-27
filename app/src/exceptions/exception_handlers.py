from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

from exceptions.user import ServiceException


async def service_exception_handler(request: Request, exc: ServiceException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": [{"msg": exc.msg}]},
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": [{"msg": exc.detail}]},
    )


async def error_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": [{"msg": "Внутренняя ошибка сервера"}]},
    )
