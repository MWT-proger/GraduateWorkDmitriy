from fastapi import APIRouter, Depends

from auth.auth_bearer import JWTBearer, get_current_user_from_ws
from core.manager_ws import ManagerWebSocket, get_anomaly_manager_web_socket
from models.base import PydanticObjectId
from schemas.anomaly import (
    AnomalyProgressEnum,
    AnomalyTrainTestDataSchema,
    ResultAnomalyDataListSchema,
    ResultAnomalyListSchema,
    ResultAnomalySchema,
    ResultWebSocketAnomalyDataSchema,
    ResultWebSocketAnomalySchema,
)
from schemas.auth import AuthJWTSchema
from services.anomaly import get_anomaly_service
from services.base import BaseAnomalyService

router = APIRouter(
    tags=[
        "Anomaly",
    ]
)


@router.websocket("/ws/train-test")
async def websocket_endpoint(
    manager_ws: ManagerWebSocket = Depends(get_anomaly_manager_web_socket),
    auth_data: AuthJWTSchema = Depends(get_current_user_from_ws),
    service: BaseAnomalyService = Depends(get_anomaly_service),
):
    # await manager_ws.ws.accept()

    try:
        await manager_ws.set_progress(AnomalyProgressEnum.start)
        body = await manager_ws.ws.receive_json()
        data = AnomalyTrainTestDataSchema(**body)

        result = await service.get_train_test_result(
            data, auth_data.user_id, manager_ws.set_progress
        )

        data = ResultWebSocketAnomalySchema(
            status=result.status,
            progress=AnomalyProgressEnum.finish,
            message=result.message,
            data=ResultWebSocketAnomalyDataSchema(
                train_metrics=result.train_metrics,
                test_metrics=result.test_metrics,
                test_ts=result.test_ts,
                test_pred=result.test_pred,
                test_labels=result.test_labels,
            ),
        )

        await manager_ws.ws.send_text(data.model_dump_json())

    except Exception as e:
        await manager_ws.send_exception(e)

    finally:
        await manager_ws.close()


@router.post("", response_model=ResultWebSocketAnomalySchema)
async def train_test(
    data: AnomalyTrainTestDataSchema,
    auth_data: AuthJWTSchema = Depends(JWTBearer()),
    service: BaseAnomalyService = Depends(get_anomaly_service),
):

    async def set_progress(data: tuple):
        pass

    result = await service.get_train_test_result(
        data, auth_data.user_id, set_progress
    )

    data = ResultWebSocketAnomalySchema(
        status=result.status,
        progress=AnomalyProgressEnum.finish,
        message=result.message,
        data=ResultWebSocketAnomalyDataSchema(
            train_metrics=result.train_metrics,
            test_metrics=result.test_metrics,
            test_ts=result.test_ts,
            test_pred=result.test_pred,
            test_labels=result.test_labels,
        ),
    )
    return data


@router.get("", response_model=ResultAnomalyListSchema)
async def get_list_history(
    auth_data: AuthJWTSchema = Depends(JWTBearer()),
    service: BaseAnomalyService = Depends(get_anomaly_service),
):
    result = await service.get_users_history(user_id=auth_data.user_id)
    data = []
    async for obj in result:
        data.append(
            ResultAnomalyDataListSchema(
                id=obj.id,
                status=obj.status,
                message=obj.message,
                train_metrics=obj.train_metrics,
                test_metrics=obj.test_metrics,
            )
        )
    return ResultAnomalyListSchema(data=data)


@router.get("/{anomaly_id}", response_model=ResultAnomalySchema)
async def get_detail_history(
    anomaly_id: PydanticObjectId,
    auth_data: AuthJWTSchema = Depends(JWTBearer()),
    service: BaseAnomalyService = Depends(get_anomaly_service),
):
    obj = await service.get_users_history_by_id(
        user_id=auth_data.user_id, anomaly_id=anomaly_id
    )

    data = ResultAnomalySchema(
        id=obj.id,
        status=obj.status,
        message=obj.message,
        train_metrics=obj.train_metrics,
        test_metrics=obj.test_metrics,
        test_ts=obj.test_ts,
        test_pred=obj.test_pred,
        test_labels=obj.test_labels,
    )
    return data
