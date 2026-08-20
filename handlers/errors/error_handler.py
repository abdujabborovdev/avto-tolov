import logging

from aiogram import Router
from aiogram.types import ErrorEvent
from aiogram.exceptions import (
    TelegramUnauthorizedError,
    TelegramBadRequest,
    TelegramAPIError,
    TelegramRetryAfter,
)

router = Router()


@router.error()
async def errors_handler(event: ErrorEvent):
    exception = event.exception
    update = event.update

    if isinstance(exception, TelegramUnauthorizedError):
        logging.exception(f'Unauthorized: {exception}')
        return True

    if isinstance(exception, TelegramRetryAfter):
        logging.exception(f'RetryAfter: {exception} | Update: {update}')
        return True

    if isinstance(exception, TelegramBadRequest):
        logging.exception(f'TelegramBadRequest: {exception} | Update: {update}')
        return True

    if isinstance(exception, TelegramAPIError):
        logging.exception(f'TelegramAPIError: {exception} | Update: {update}')
        return True

    logging.exception(f'Update: {update} | {exception}')
    return True
