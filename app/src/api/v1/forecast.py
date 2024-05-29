from typing import List

from fastapi import APIRouter, Depends, WebSocket

from auth.auth_bearer import JWTBearer, get_current_user_from_ws
from exceptions.base import ServiceException
from schemas import TrainTestDataSchema
from schemas.auth import AuthJWTSchema
from schemas.forecast import (
    ForecastProgressEnum,
    ResultForecastSchema,
    ResultWebSocketForecastDataSchema,
    ResultWebSocketForecastSchema,
    StatusForecastEnum,
)
from services.base import BaseForecastService
from services.forecast import get_forecast_service

router = APIRouter(
    tags=[
        "Forecast",
    ]
)


@router.websocket("/ws/train-test")
async def websocket_endpoint(
    websocket: WebSocket,
    auth_data: AuthJWTSchema = Depends(get_current_user_from_ws),
    service: BaseForecastService = Depends(get_forecast_service),
):
    await websocket.accept()

    async def set_progress(progress: ForecastProgressEnum):
        data = ResultWebSocketForecastSchema(
            status=StatusForecastEnum.process,
            progress=progress,
        )

        await websocket.send_text(data.model_dump_json())

    try:
        await set_progress(ForecastProgressEnum.start)
        body = await websocket.receive_json()
        data = TrainTestDataSchema(**body)

        result = await service.get_train_test_result(
            data, auth_data.user_id, set_progress
        )

        data = ResultWebSocketForecastSchema(
            status=result.status,
            progress=ForecastProgressEnum.finish,
            message=result.message,
            data=ResultWebSocketForecastDataSchema(
                train_metrics=result.train_metrics,
                test_metrics=result.test_metrics,
                test_ts=result.test_ts,
                train_ts=result.train_ts,
                exog_ts=result.exog_ts,
            ),
        )

        await websocket.send_text(data.model_dump_json())

    except ServiceException as e:
        data = ResultWebSocketForecastSchema(
            status=StatusForecastEnum.error, message=e.msg
        )

        await websocket.send_text(data.model_dump_json())

    finally:
        await websocket.close()


@router.post("/train-test", response_model=ResultForecastSchema)
async def train_test(
    data: TrainTestDataSchema,
    auth_data: AuthJWTSchema = Depends(JWTBearer()),
    service: BaseForecastService = Depends(get_forecast_service),
):
    result = await service.get_train_test_result(data, auth_data.user_id)

    return ResultForecastSchema(
        status=result.status,
        message=result.message,
        train_metrics=result.train_metrics,
        test_metrics=result.test_metrics,
        test_ts=result.test_ts,
        train_ts=result.test_ts,
        exog_ts=result.exog_ts,
    )


@router.get("/history", response_model=List[ResultForecastSchema])
async def get_list_history(
    auth_data: AuthJWTSchema = Depends(JWTBearer()),
    service: BaseForecastService = Depends(get_forecast_service),
):
    result = await service.get_users_history(user_id=auth_data.user_id)
    data = []
    async for obj in result:
        data.append(
            ResultForecastSchema(
                status=obj.status,
                message=obj.message,
                train_metrics=obj.train_metrics,
                test_metrics=obj.test_metrics,
                test_ts=obj.test_ts,
                train_ts=obj.test_ts,
                exog_ts=obj.exog_ts,
            )
        )
    return data
