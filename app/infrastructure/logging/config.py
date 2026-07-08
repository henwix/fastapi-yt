import logging
from logging.config import dictConfig

from msgspec import json

from app.core.configs import settings
from app.utils.get_datetime_utc_now import get_datetime_utc_now


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            'timestamp': get_datetime_utc_now().isoformat(),
            'process': record.processName,
            'level': record.levelname,
            'module': record.name,
            'line': record.lineno,
            'message': record.getMessage(),
        }

        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)

        if hasattr(record, 'log_meta') and record.log_meta:
            log_record['log_meta'] = record.log_meta

        return json.encode(log_record).decode()


class StringFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record = [
            f'{get_datetime_utc_now().isoformat()} | ',
            f'{record.processName} | ',
            f'{record.levelname:<8} | ',
            f'{record.name}:{record.lineno} - ',
            record.getMessage(),
        ]

        if hasattr(record, 'log_meta') and record.log_meta:
            log_record.append(f'\nlog_meta:{json.encode(record.log_meta).decode()}')

        if record.exc_info:
            log_record.append(self.formatException(record.exc_info))

        return ''.join(log_record)


log_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': JSONFormatter,
        },
        'string': {
            '()': StringFormatter,
        },
    },
    'handlers': {
        'logger_console': {
            'level': settings.logging_level,
            'class': 'logging.StreamHandler',
            'formatter': 'string' if settings.debug else 'json',
        },
    },
    'loggers': {
        'app': {
            'level': 'DEBUG',
            'handlers': ['logger_console'],
            'propagate': False,
        },
    },
}


def configure_logging():
    dictConfig(config=log_config)
