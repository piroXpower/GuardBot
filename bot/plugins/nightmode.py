"""
================================================================================
SUPER GUARDIAN BOT - NIGHT MODE AUTOMATION
================================================================================
Module: bot.plugins.nightmode
Description:
    Provides automated UTC schedule-based chat lockdowns during overnight hours.
================================================================================
"""

from __future__ import annotations

import logging
from pyrogram import Client
from pyrogram.types import Message

from bot.core.decorators import require_admin
from bot.core.error_handler import auto_catch
from bot.core.registry import registry
from bot.database.cache import cache_manager

logger = logging.getLogger("GuardianBot.NightMode")


@registry.register("nightmode", "NightMode", admin_only=True, desc="Configure scheduled night mode")
@require_admin(["can_change_info"])
@auto_catch
async def nightmode_cmd(_: Client, message: Message) -> None:
    chat_id = message.chat.id
    if len(message.command) < 2:
        status = await cache_manager.get_chat_setting(chat_id, "nightmode", default="off")
        start_h = await cache_manager.get_chat_setting(chat_id, "night_start", "0")
        end_h = await cache_manager.get_chat_setting(chat_id, "night_end", "6")
        await message.reply_text(
            f"🌙 **Night Mode Status**: `{status.upper()}`\n"
            f"• **Schedule**: `{int(start_h):02d}:00 UTC` to `{int(end_h):02d}:00 UTC`\n\n"
            f"Usage:\n"
            f"• `/nightmode on`\n"
            f"• `/nightmode off`\n"
            f"• `/nightmode set <start_0_23> <end_0_23>`"
        )
        return

    sub = message.command[1].lower()
    if sub in ["on", "enable"]:
        await cache_manager.set_chat_setting(chat_id, "nightmode", "on")
        await message.reply_text("🌙 **Night Mode Enabled**.")
    elif sub in ["off", "disable"]:
        await cache_manager.set_chat_setting(chat_id, "nightmode", "off")
        await message.reply_text("☀️ **Night Mode Disabled**.")
    elif sub == "set" and len(message.command) >= 4:
        s_str, e_str = message.command[2], message.command[3]
        if s_str.isdigit() and e_str.isdigit():
            s, e = int(s_str), int(e_str)
            if 0 <= s <= 23 and 0 <= e <= 23:
                await cache_manager.set_chat_setting(chat_id, "night_start", str(s))
                await cache_manager.set_chat_setting(chat_id, "night_end", str(e))
                await message.reply_text(f"⚙️ **Schedule Set**: `{s:02d}:00 UTC` to `{e:02d}:00 UTC`.")
                return
        await message.reply_text("❌ Provide valid hours between 0 and 23.")
