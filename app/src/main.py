from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from motor.motor_asyncio import AsyncIOMotorClient

from core.config import settings
from db import mongodb

@asynccontextmanager
async def lifespan(app: FastAPI):
    mongodb.mongodb = AsyncIOMotorClient(settings.MONGODB.DSN)
    yield
    await mongodb.mongodb.close()

app = FastAPI(
    lifespan=lifespan,
    title=settings.PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)
print(settings.MONGODB.DSN)
if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=settings.PORT,
    )
