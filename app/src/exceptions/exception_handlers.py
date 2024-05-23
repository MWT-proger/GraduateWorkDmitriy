from fastapi import Request
from fastapi.responses import JSONResponse

from exceptions.user import ServiceException

async def service_exception_handler(request: Request, exc: ServiceException):
    return JSONResponse(
        status_code=400,
        content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
    )
