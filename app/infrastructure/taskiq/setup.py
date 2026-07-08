from logging import getLogger

from dishka.integrations.taskiq import setup_dishka
from taskiq import AsyncBroker, TaskiqEvents, TaskiqState

from app.infrastructure.di.container import get_container
from app.infrastructure.logging.config import configure_logging
from app.infrastructure.taskiq.broker import get_broker

logger = getLogger(__name__)


def setup_broker() -> AsyncBroker:
    container = get_container()
    broker = get_broker()
    setup_dishka(container=container, broker=broker)

    return broker


broker = setup_broker()


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def on_worker_startup(_: TaskiqState) -> None:
    configure_logging()
    logger.info('Worker startup complete')
