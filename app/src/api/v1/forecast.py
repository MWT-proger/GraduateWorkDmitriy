from typing import List

from fastapi import APIRouter, Depends

from auth.auth_bearer import JWTBearer, get_current_user_from_ws
from core.manager_ws import ManagerWebSocket, get_manager_web_socket
from schemas import TrainTestDataSchema
from schemas.auth import AuthJWTSchema
from schemas.forecast import (
    ForecastProgressEnum,
    ResultForecastSchema,
    ResultWebSocketForecastDataSchema,
    ResultWebSocketForecastSchema,
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
    manager_ws: ManagerWebSocket = Depends(get_manager_web_socket),
    auth_data: AuthJWTSchema = Depends(get_current_user_from_ws),
    service: BaseForecastService = Depends(get_forecast_service),
):
    # await manager_ws.ws.accept()

    try:
        await manager_ws.set_progress(ForecastProgressEnum.start)
        body = await manager_ws.ws.receive_json()
        data = TrainTestDataSchema(**body)

        result = await service.get_train_test_result(
            data, auth_data.user_id, manager_ws.set_progress
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

        await manager_ws.ws.send_text(data.model_dump_json())

    except Exception as e:
        await manager_ws.send_exception(e)

    finally:
        await manager_ws.close()


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
