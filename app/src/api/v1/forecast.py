from fastapi import APIRouter, Depends

from auth.auth_bearer import JWTBearer, get_current_user_from_ws
from core.manager_ws import ManagerWebSocket, get_forecast_manager_web_socket
from models.base import PydanticObjectId
from schemas import TrainTestDataSchema
from schemas.auth import AuthJWTSchema
from schemas.forecast import (
    ForecastProgressEnum,
    ResultForecastDataListSchema,
    ResultForecastListSchema,
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
    manager_ws: ManagerWebSocket = Depends(get_forecast_manager_web_socket),
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
                params=result.params,
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


@router.post("", response_model=ResultWebSocketForecastSchema)
async def train_test(
    data: TrainTestDataSchema,
    auth_data: AuthJWTSchema = Depends(JWTBearer()),
    service: BaseForecastService = Depends(get_forecast_service),
):

    async def set_progress(data: tuple):
        pass

    result = await service.get_train_test_result(
        data, auth_data.user_id, set_progress
    )

    data = ResultWebSocketForecastSchema(
        status=result.status,
        progress=ForecastProgressEnum.finish,
        message=result.message,
        data=ResultWebSocketForecastDataSchema(
            params=result.params,
            train_metrics=result.train_metrics,
            test_metrics=result.test_metrics,
            test_ts=result.test_ts,
            train_ts=result.train_ts,
            exog_ts=result.exog_ts,
        ),
    )
    return data


@router.get("", response_model=ResultForecastListSchema)
async def get_list_history(
    auth_data: AuthJWTSchema = Depends(JWTBearer()),
    service: BaseForecastService = Depends(get_forecast_service),
):
    result = await service.get_users_history(user_id=auth_data.user_id)
    data = []
    async for obj in result:
        data.append(
            ResultForecastDataListSchema(
                id=obj.id,
                status=obj.status,
                message=obj.message,
                params=obj.params,
                train_metrics=obj.train_metrics,
                test_metrics=obj.test_metrics,
            )
        )
    return ResultForecastListSchema(data=data)


@router.get("/{forecast_id}", response_model=ResultForecastSchema)
async def get_detail_history(
    forecast_id: PydanticObjectId,
    auth_data: AuthJWTSchema = Depends(JWTBearer()),
    service: BaseForecastService = Depends(get_forecast_service),
):
    obj = await service.get_users_history_by_id(
        user_id=auth_data.user_id, forecast_id=forecast_id
    )

    data = ResultForecastSchema(
        id=obj.id,
        status=obj.status,
        message=obj.message,
        params=obj.params,
        train_metrics=obj.train_metrics,
        test_metrics=obj.test_metrics,
        test_ts=obj.test_ts,
        train_ts=obj.train_ts,
        exog_ts=obj.exog_ts,
    )
    return data
