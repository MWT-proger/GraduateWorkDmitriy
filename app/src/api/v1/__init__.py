from fastapi import APIRouter

from . import anomaly, auth, dataset, forecast, user

router = APIRouter(prefix="")
router.include_router(user.router, prefix="/users")
router.include_router(auth.router, prefix="/auth")
router.include_router(forecast.router, prefix="/forecasts")
router.include_router(anomaly.router, prefix="/anomalies")
router.include_router(dataset.router, prefix="/datasets")
