from dishka.integrations.taskiq import FromDishka, inject

from app.application.files_cleanup.usecases import CleanupUseCase
from app.infrastructure.taskiq.broker import get_broker

broker = get_broker()


@broker.task(task_name='files_cleanup')
@inject(patch_module=True)
async def files_cleanup(use_case: FromDishka[CleanupUseCase]) -> int:
    return await use_case.execute()
