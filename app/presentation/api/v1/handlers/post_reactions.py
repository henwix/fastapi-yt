from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

router = APIRouter(
    prefix='/posts/{post_id}/reactions',
    tags=['Post Reactions'],
    route_class=DishkaRoute,
)
