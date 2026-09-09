from dishka.integrations.taskiq import FromDishka, inject

from app.application.videos.use_cases.delete_not_completed_videos import DeleteNotCompletedVideosUseCase
from app.infrastructure.taskiq.broker import get_broker

broker = get_broker()


@broker.task(task_name='delete_not_completed_videos', schedule=[{'cron': '0 * * * *'}])
@inject(patch_module=True)
async def delete_not_completed_videos(use_case: FromDishka[DeleteNotCompletedVideosUseCase]) -> int:
    return await use_case.execute()
