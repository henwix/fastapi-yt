from dataclasses import dataclass


@dataclass
class AppException(Exception):
    message = 'Application exception occured'
