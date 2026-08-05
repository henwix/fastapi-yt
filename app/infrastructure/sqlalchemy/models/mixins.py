from datetime import datetime
from uuid import UUID, uuid7

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.utils.datetime import get_current_utc_datetime


class UUIDIdMixin:
    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid7,
    )


class CreatedAtMixin:
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=get_current_utc_datetime,
        server_default=sa.func.now(),
    )


class UpdatedAtMixin:
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=get_current_utc_datetime,
        server_default=sa.func.now(),
        onupdate=get_current_utc_datetime,
        server_onupdate=sa.func.now(),
    )
