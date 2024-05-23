from fastapi import APIRouter

from . import user, auth


router = APIRouter(prefix="")
router.include_router(user.router, prefix="/user")
router.include_router(auth.router, prefix="/auth")
