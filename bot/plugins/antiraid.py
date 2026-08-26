"""
================================================================================
SUPER GUARDIAN BOT - ANTI-RAID & MASS JOIN MITIGATION
================================================================================
Module: bot.plugins.antiraid
Description:
    Monitors join velocities to detect coordinated token attacks, clone raids,
    and automatic bot additions.
================================================================================
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from typing import Dict, List, Set

from pyrogram import Client, filters
from pyrogram.types import ChatPermissions, Message, User

from bot.core.decorators import require_admin
from bot.core.error_handler import auto_catch, watcher_guard
from bot.core.registry import registry
from bot.database.cache import cache_manager

logger = logging.getLogger("GuardianBot.AntiRaid")

JOIN_TIMESTAMPS: Dict[int, List[float]] = defaultdict(list)
AUTO_LOCKDOWN_CHATS: Set[int] = set()

DEFAULT_THRESHOLD = 8
DEFAULT_WINDOW = 5


@Client.on_message(filters.group & filters.new_chat_members, group=10)
@watcher_guard
async def new_member_raid_watcher(client: Client, message: Message) -> None:
    chat_id = message.chat.id
    setting = await cache_manager.get_chat_setting(chat_id, "antiraid", default="on")
    if setting == "off":
        return

    now = time.time()
    valid_stamps = [t for t in JOIN_TIMESTAMPS[chat_id] if now - t < DEFAULT_WINDOW]
    valid_stamps.append(now)
    JOIN_TIMESTAMPS[chat_id] = valid_stamps

    limit = int(await cache_manager.get_chat_setting(chat_id, "raid_limit", str(DEFAULT_THRESHOLD)))

    if len(valid_stamps) >= limit and chat_id not in AUTO_LOCKDOWN_CHATS:
        AUTO_LOCKDOWN_CHATS.add(chat_id)
        restricted = ChatPermissions(
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_other_messages=False,
            can_send_polls=False,
            can_add_web_page_previews=False,
            can_invite_users=False,
            can_pin_messages=False,
        )
        await client.set_chat_permissions(chat_id, restricted)
        await client.send_message(
            chat_id,
            "🚨 **AUTOMATIC RAID LOCKDOWN TRIGGERED** 🚨\n\n"
            "⚠️ High-velocity join spike detected. Messaging permissions locked.\n"
            "💡 Use `/unlockdown` or `/antiraid off` to restore access."
        )

    for member in message.new_chat_members:
        if member.is_bot:
            antibot = await cache_manager.get_chat_setting(chat_id, "antibot", default="off")
            if antibot == "on":
                try:
                    await message.chat.ban_member(member.id)
                except Exception:
                    pass


@registry.register("antiraid", "Security", admin_only=True, desc="Configure anti-raid defenses")
@require_admin(["can_restrict_members", "can_change_info"])
@auto_catch
async def antiraid_command(_: Client, message: Message) -> None:
    chat_id = message.chat.id
    if len(message.command) < 2:
        current = await cache_manager.get_chat_setting(chat_id, "antiraid", default="on")
        limit = await cache_manager.get_chat_setting(chat_id, "raid_limit", str(DEFAULT_THRESHOLD))
        await message.reply_text(
            f"🛡️ **Anti-Raid Status**: `{current.upper()}`\n"
            f"• **Threshold**: `{limit} users / {DEFAULT_WINDOW}s`\n"
            f"• **Active Lockdown**: `{'YES 🔒' if chat_id in AUTO_LOCKDOWN_CHATS else 'NO 🔓'}`\n\n"
            f"Usage: `/antiraid on`, `/antiraid off`, `/antiraid limit 10`"
        )
        return

    sub = message.command[1].lower()
    if sub in ["on", "enable"]:
        await cache_manager.set_chat_setting(chat_id, "antiraid", "on")
        await message.reply_text("✅ **Anti-Raid Enabled**.")
    elif sub in ["off", "disable"]:
        await cache_manager.set_chat_setting(chat_id, "antiraid", "off")
        AUTO_LOCKDOWN_CHATS.discard(chat_id)
        await message.reply_text("⚠️ **Anti-Raid Disabled**.")
    elif sub == "limit" and len(message.command) > 2:
        new_lim = message.command[2]
        if new_lim.isdigit() and int(new_lim) >= 3:
            await cache_manager.set_chat_setting(chat_id, "raid_limit", new_lim)
            await message.reply_text(f"⚙️ **Threshold Updated**: `{new_lim}` joins / `{DEFAULT_WINDOW}`s.")
        else:
            await message.reply_text("❌ Threshold must be an integer $\\ge 3$.")


@registry.register("antibot", "Security", admin_only=True, desc="Toggle anti-bot join security")
@require_admin(["can_restrict_members"])
@auto_catch
async def antibot_command(_: Client, message: Message) -> None:
    if len(message.command) < 2:
        current = await cache_manager.get_chat_setting(message.chat.id, "antibot", default="off")
        await message.reply_text(f"🤖 **Anti-Bot Status**: `{current.upper()}`\nUsage: `/antibot on` or `/antibot off`")
        return

    mode = message.command[1].lower()
    if mode in ["on", "enable"]:
        await cache_manager.set_chat_setting(message.chat.id, "antibot", "on")
        await message.reply_text("🛡️ **Anti-Bot Enabled**: Unauthorized bots will be banned on arrival.")
    elif mode in ["off", "disable"]:
        await cache_manager.set_chat_setting(message.chat.id, "antibot", "off")
        await message.reply_text("🔓 **Anti-Bot Disabled**.")
