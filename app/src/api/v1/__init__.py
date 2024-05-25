from fastapi import APIRouter

from . import auth, forecast, user

router = APIRouter(prefix="")
router.include_router(user.router, prefix="/user")
router.include_router(auth.router, prefix="/auth")
router.include_router(forecast.router, prefix="/forecast")
