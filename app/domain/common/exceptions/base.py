from dataclasses import dataclass


@dataclass
class AppError(Exception):
    message = 'Application error occured'
