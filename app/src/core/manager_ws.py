from enum import Enum

from fastapi import WebSocket
from pydantic import BaseModel, ValidationError

from exceptions.base import ServiceException
from models.anomaly import StatusAnomalyEnum
from schemas.anomaly import AnomalyProgressEnum, ResultWebSocketAnomalySchema
from schemas.forecast import (
    ForecastProgressEnum,
    ResultWebSocketForecastSchema,
    StatusForecastEnum,
)


class ManagerWebSocket:
    curent_progres: Enum
    code: int = 1000
    result_schema: BaseModel
    status_emum: Enum

    def __init__(self, ws: WebSocket) -> None:
        self.ws = ws

    async def set_progress(self, progress: Enum):
        data = self.result_schema(
            status=self.status_emum.process,
            progress=progress,
        )
        self.curent_progres = progress

        await self.ws.send_text(data.model_dump_json())

    async def send_exception(self, exc: Exception):
        if isinstance(exc, ServiceException):

            data = self.result_schema(
                status=self.status_emum.error,
                progress=self.curent_progres,
                detail=[{"msg": exc.msg}],
            )
            await self.ws.send_text(data.model_dump_json())
            self.code = 4000

        elif isinstance(exc, ValidationError):
            data = self.result_schema(
                status=self.status_emum.error,
                progress=self.curent_progres,
                detail=exc.errors(),
            )
            await self.ws.send_text(data.model_dump_json())
            self.code = 4000

        else:
            data = self.result_schema(
                status=self.status_emum.error,
                progress=self.curent_progres,
                detail=[
                    {
                        "msg": "Произошла не предвиденная ошибка. Попробуйте позжею."
                    }
                ],
            )
            await self.ws.send_text(data.model_dump_json())
            self.code = 4005

    async def close(self, code: int = None):
        await self.ws.close(code=self.code if not code else code)


class ForecastManagerWebSocket(ManagerWebSocket):
    curent_progres: ForecastProgressEnum = ForecastProgressEnum.start
    code: int = 1000
    result_schema = ResultWebSocketForecastSchema
    status_emum = StatusForecastEnum


class AnomalyManagerWebSocket(ManagerWebSocket):
    curent_progres: AnomalyProgressEnum = AnomalyProgressEnum.start
    code: int = 1000
    result_schema = ResultWebSocketAnomalySchema
    status_emum = StatusAnomalyEnum


async def get_forecast_manager_web_socket(websocket: WebSocket):
    obj = ForecastManagerWebSocket(websocket)
    return obj


async def get_anomaly_manager_web_socket(websocket: WebSocket):
    obj = AnomalyManagerWebSocket(websocket)
    return obj
