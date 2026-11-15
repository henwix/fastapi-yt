from dishka.integrations.taskiq import FromDishka, inject

from app.application.channels.dto import PurgeDeletedChannelsResult
from app.application.channels.usecases.channels import PurgeDeletedChannelsUseCase
from app.infrastructure.taskiq.broker import get_broker

broker = get_broker()


@broker.task(task_name='purge_deleted_channels_task', schedule=[{'cron': '*/5 * * * *'}])
@inject(patch_module=True)
async def purge_deleted_channels_task(use_case: FromDishka[PurgeDeletedChannelsUseCase]) -> PurgeDeletedChannelsResult:
    return await use_case.execute()
