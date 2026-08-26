"""
================================================================================
SUPER GUARDIAN BOT - RBAC DECORATORS
================================================================================
Module: bot.core.decorators
================================================================================
"""

from __future__ import annotations

import functools
import logging
from typing import Any, Callable, Coroutine, List, Optional, TypeVar, cast

from pyrogram import Client
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import CallbackQuery, Message

from bot.core.error_handler import auto_catch
from bot.database.cache import cache_manager
from config import OWNER_USERNAME

logger = logging.getLogger("GuardianBot.Decorators")
F = TypeVar("F", bound=Callable[..., Coroutine[Any, Any, Any]])


def require_admin(permissions: Optional[List[str]] = None) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        @functools.wraps(func)
        @auto_catch
        async def wrapper(client: Client, update: Message | CallbackQuery, *args: Any, **kwargs: Any) -> Any:
            chat = update.chat if isinstance(update, Message) else update.message.chat
            user = update.from_user

            if not user:
                return None

            if isinstance(update, Message) and update.sender_chat and update.sender_chat.id == chat.id:
                return await func(client, update, *args, **kwargs)

            try:
                member = await chat.get_member(user.id)
            except Exception:
                return None

            if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                if isinstance(update, Message):
                    await update.reply_text("⛔ **Access Denied**: Administrator privileges required.")
                elif isinstance(update, CallbackQuery):
                    await update.answer("⛔ Access Denied: Admin privileges required.", show_alert=True)
                return None

            return await func(client, update, *args, **kwargs)

        return cast(F, wrapper)
    return decorator


def require_owner(func: F) -> F:
    @functools.wraps(func)
    @auto_catch
    async def wrapper(client: Client, update: Message | CallbackQuery, *args: Any, **kwargs: Any) -> Any:
        user = update.from_user
        if not user:
            return None

        clean_owner = OWNER_USERNAME.lstrip("@").lower()
        if (user.username or "").lower() != clean_owner:
            if isinstance(update, Message):
                await update.reply_text("⛔ **Restricted**: Reserved for bot owner.")
            elif isinstance(update, CallbackQuery):
                await update.answer("⛔ Access Denied: Owner exclusive.", show_alert=True)
            return None

        return await func(client, update, *args, **kwargs)

    return cast(F, wrapper)


def rate_limit(seconds: int = 2) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        @functools.wraps(func)
        @auto_catch
        async def wrapper(client: Client, update: Message | CallbackQuery, *args: Any, **kwargs: Any) -> Any:
            user = update.from_user
            if not user:
                return None

            chat_id = update.chat.id if isinstance(update, Message) else update.message.chat.id
            is_limited = await cache_manager.check_flood_rate_limit(chat_id, user.id, limit=1, window=seconds)

            if is_limited:
                if isinstance(update, CallbackQuery):
                    await update.answer("⏳ Rate limited, please wait...", show_alert=False)
                return None

            return await func(client, update, *args, **kwargs)

        return cast(F, wrapper)
    return decorator
        
