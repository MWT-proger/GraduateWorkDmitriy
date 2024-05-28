from typing import List

from fastapi import APIRouter, Depends

from auth.auth_bearer import JWTBearer
from schemas import TrainTestDataSchema
from schemas.auth import AuthJWTSchema
from schemas.forecast import ResultForecastSchema
from services.base import BaseForecastService
from services.forecast import get_forecast_service

router = APIRouter(
    tags=[
        "Forecast",
    ]
)


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
