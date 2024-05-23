import logging

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from core import config
from core.logger import LOGGING

app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=config.PORT,
    )
