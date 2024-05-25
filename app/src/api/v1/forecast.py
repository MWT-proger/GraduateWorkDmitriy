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
async def login(
    data: TrainTestDataSchema,
    auth_data: AuthJWTSchema = Depends(JWTBearer()),
    service: BaseForecastService = Depends(get_forecast_service),
):

    return await service.get_train_test_result(data, auth_data.user_id)
