from dishka.integrations.taskiq import setup_dishka
from taskiq import AsyncBroker

from app.infrastructure.di.container import get_container
from app.infrastructure.taskiq.broker import get_broker


def setup_broker() -> AsyncBroker:
    container = get_container()
    broker = get_broker()
    setup_dishka(container=container, broker=broker)

    return broker


broker = setup_broker()
