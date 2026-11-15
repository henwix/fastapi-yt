from dishka.integrations.taskiq import FromDishka, inject

from app.application.videos.dto import CreateVideoCleanupsResult
from app.application.videos.usecases import CreateVideoCleanupsUseCase
from app.infrastructure.taskiq.broker import get_broker

broker = get_broker()


@broker.task(task_name='create_video_cleanups_task', schedule=[{'cron': '*/5 * * * *'}])
@inject(patch_module=True)
async def create_video_cleanups_task(use_case: FromDishka[CreateVideoCleanupsUseCase]) -> CreateVideoCleanupsResult:
    return await use_case.execute()
