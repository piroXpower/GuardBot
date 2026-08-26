"""
================================================================================
SUPER GUARDIAN BOT - ERROR HANDLER
================================================================================
Module: bot.core.error_handler
================================================================================
"""

from __future__ import annotations

import asyncio
import functools
import logging
from typing import Any, Callable, Coroutine, Optional, TypeVar, cast

from pyrogram.errors import (
    ChatAdminRequired,
    FloodWait,
    MessageCantBeDeleted,
    MessageDeleteForbidden,
    MessageNotModified,
    RPCError,
    SlowmodeWait,
    UserAdminInvalid,
)
from pyrogram.types import CallbackQuery, Message

logger = logging.getLogger("GuardianBot.ErrorHandler")
F = TypeVar("F", bound=Callable[..., Coroutine[Any, Any, Any]])


class SecurityError(Exception):
    pass


class DatabaseTimeoutError(Exception):
    pass


def auto_catch(func: F) -> F:
    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        target: Optional[Any] = None
        for arg in args:
            if isinstance(arg, (Message, CallbackQuery)):
                target = arg
                break

        try:
            return await func(*args, **kwargs)

        except FloodWait as flood:
            wait_time = int(flood.value) + 1
            await asyncio.sleep(wait_time)
            try:
                return await func(*args, **kwargs)
            except Exception:
                return None

        except SlowmodeWait as slowmode:
            if isinstance(target, Message):
                await target.reply_text(f"⏳ Chat is in slowmode. Please wait `{slowmode.value}` seconds.")
            return None

        except (ChatAdminRequired, UserAdminInvalid):
            if isinstance(target, Message):
                await target.reply_text("⛔ **Error**: I lack the administrator permissions required for this action.")
            elif isinstance(target, CallbackQuery):
                await target.answer("⛔ Error: Missing administrator permissions.", show_alert=True)
            return None

        except MessageNotModified:
            if isinstance(target, CallbackQuery):
                await target.answer("Menu is up to date.")
            return None

        except (MessageCantBeDeleted, MessageDeleteForbidden):
            return None

        except RPCError as rpc:
            logger.error("RPC error in %s: %s", func.__name__, rpc)
            return None

        except Exception as exc:
            logger.critical("Unhandled error in %s: %s", func.__name__, exc, exc_info=True)
            return None

    return cast(F, wrapper)


def watcher_guard(func: F) -> F:
    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except (MessageCantBeDeleted, MessageDeleteForbidden):
            pass
        except FloodWait as flood:
            await asyncio.sleep(flood.value + 1)
        except Exception as exc:
            logger.debug("Watcher ignored error in %s: %s", func.__name__, exc)
        return None

    return cast(F, wrapper)
