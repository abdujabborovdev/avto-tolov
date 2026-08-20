from aiogram import Dispatcher

from .errors import router as errors_router
from .users import router as users_router
from .groups import router as groups_router
from .channels import router as channels_router


def setup(dp: Dispatcher):
    dp.include_router(errors_router)
    dp.include_router(users_router)
    dp.include_router(groups_router)
    dp.include_router(channels_router)
