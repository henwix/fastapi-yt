from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.utils.get_datetime_utc_now import get_datetime_utc_now


class IntIDMixin:
    id: Mapped[int] = mapped_column(primary_key=True)


class CreatedAtMixin:
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=get_datetime_utc_now,
        server_default=sa.func.now(),
    )


class UpdatedAtMixin:
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=get_datetime_utc_now,
        server_default=sa.func.now(),
        onupdate=get_datetime_utc_now,
        server_onupdate=sa.func.now(),
    )
