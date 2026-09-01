from aiogram import Router

from .help import router as help_router
from .start import router as start_router
from .nomer import router as nomerrouter
from .tolov import router as tolovrouter
from .menu import router as menuroputer
from .secret_key import router as secret_key
from .admin import router as adrouter
from .apilar import router as apilarrouter

router = Router()
router.include_router(start_router)
router.include_router(help_router)
router.include_router(tolovrouter)
router.include_router(nomerrouter)
router.include_router(menuroputer)
router.include_router(secret_key)
router.include_router(adrouter)
router.include_router(apilarrouter)
