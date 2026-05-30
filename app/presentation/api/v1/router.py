from fastapi import APIRouter

from app.presentation.api.v1.handlers.channels import router

v1_router = APIRouter()
v1_router.include_router(router=router)
