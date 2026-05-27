from datetime import UTC, datetime


def get_datetime_utc_now() -> datetime:
    return datetime.now(tz=UTC)
