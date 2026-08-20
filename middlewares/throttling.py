import asyncio
import time
from collections import defaultdict
from typing import Any, Awaitable, Callable, Dict, Optional

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject


class ThrottlingMiddleware(BaseMiddleware):
    """Simple anti-flood middleware for aiogram 3."""

    def __init__(self, limit: float = 0.5, key_prefix: str = 'antiflood_'):
        self.rate_limit = limit
        self.prefix = key_prefix
        self._last_call: Dict[Any, float] = defaultdict(float)
        self._warned_until: Dict[Any, float] = defaultdict(float)
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)

        user = event.from_user
        key: Any = f"{self.prefix}{user.id}" if user else f"{self.prefix}anonymous"
        now = time.monotonic()
        delta = now - self._last_call[key]

        if delta < self.rate_limit:
            if now >= self._warned_until[key]:
                self._warned_until[key] = now + self.rate_limit
                await event.answer("Juda tez yozayapsiz. Iltimos, biroz kuting.")
            await asyncio.sleep(max(self.rate_limit - delta, 0))

        self._last_call[key] = time.monotonic()
        return await handler(event, data)
