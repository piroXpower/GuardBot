"""
================================================================================
SUPER GUARDIAN BOT - SETTINGS & UTILITY PLUGIN
================================================================================
Module: bot.plugins.settings
Description:
    Latency benchmarks, user info lookups, and diagnostic information cards.
================================================================================
"""

from __future__ import annotations

import time
from pyrogram import Client
from pyrogram.types import Message

from bot.core.error_handler import auto_catch
from bot.core.registry import registry


@registry.register("ping", "Utility")
@auto_catch
async def ping_cmd(_: Client, message: Message) -> None:
    start = time.time()
    msg = await message.reply_text("⚡ Ping...")
    latency = (time.time() - start) * 1000
    await msg.edit_text(f"⚡ **Pong!** `{latency:.2f}ms`")


@registry.register("id", "Utility")
@auto_catch
async def id_cmd(_: Client, message: Message) -> None:
    user = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    uid = user.id if user else "Unknown"
    await message.reply_text(f"💬 **Chat ID**: `{message.chat.id}`\n👤 **User ID**: `{uid}`")
