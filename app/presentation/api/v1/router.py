from fastapi import APIRouter

from app.presentation.api.v1.handlers.auth import router as auth_router
from app.presentation.api.v1.handlers.channels import router as channels_router

v1_router = APIRouter()
v1_router.include_router(router=channels_router)
v1_router.include_router(router=auth_router)
