from fastapi import WebSocket
from pydantic import ValidationError

from exceptions.base import ServiceException
from schemas.forecast import (
    ForecastProgressEnum,
    ResultWebSocketForecastSchema,
    StatusForecastEnum,
)


class ManagerWebSocket:
    curent_progres: ForecastProgressEnum = ForecastProgressEnum.start
    code: int = 1000

    def __init__(self, ws: WebSocket) -> None:
        self.ws = ws

    async def set_progress(self, progress: ForecastProgressEnum):
        data = ResultWebSocketForecastSchema(
            status=StatusForecastEnum.process,
            progress=progress,
        )
        self.curent_progres = progress

        await self.ws.send_text(data.model_dump_json())

    async def send_exception(self, exc: Exception):
        if isinstance(exc, ServiceException):

            data = ResultWebSocketForecastSchema(
                status=StatusForecastEnum.error,
                progress=self.curent_progres,
                detail=[{"msg": exc.msg}],
            )
            await self.ws.send_text(data.model_dump_json())
            self.code = 4000

        elif isinstance(exc, ValidationError):
            data = ResultWebSocketForecastSchema(
                status=StatusForecastEnum.error,
                progress=self.curent_progres,
                detail=exc.errors(),
            )
            await self.ws.send_text(data.model_dump_json())
            self.code = 4000

        else:
            data = ResultWebSocketForecastSchema(
                status=StatusForecastEnum.error,
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


async def get_manager_web_socket(websocket: WebSocket):
    obj = ManagerWebSocket(websocket)
    return obj
