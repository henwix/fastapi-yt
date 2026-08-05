from datetime import UTC, date, datetime


def get_current_utc_datetime() -> datetime:
    return datetime.now(tz=UTC)


def get_current_utc_date() -> date:
    return datetime.now(tz=UTC).date()
