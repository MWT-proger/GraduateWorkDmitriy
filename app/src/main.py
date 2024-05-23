from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from motor.motor_asyncio import AsyncIOMotorClient

from api import v1 as api_v1
from core.config import settings
from db import mongodb
from exceptions.exception_handlers import service_exception_handler
from exceptions.user import ServiceException


@asynccontextmanager
async def lifespan(app: FastAPI):
    mongodb.mongodb = AsyncIOMotorClient(settings.MONGODB.DSN)
    yield
    await mongodb.mongodb.close()


app = FastAPI(
    lifespan=lifespan,
    title=settings.PROJECT_NAME,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)

app.include_router(api_v1.router, prefix="/api/v1")
app.exception_handler(ServiceException)(service_exception_handler)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
    )
