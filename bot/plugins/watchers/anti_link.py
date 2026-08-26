"""
================================================================================
SUPER GUARDIAN BOT - ANTI-LINK WATCHER
================================================================================
Module: bot.plugins.watchers.anti_link
Description:
    Intercepts and purges unauthorized external links and Telegram invite URLs.
================================================================================
"""

from __future__ import annotations

import re
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import Message

from bot.core.error_handler import watcher_guard
from bot.database.cache import cache_manager

LINK_REGEX = re.compile(r"(https?://|t\.me/|telegram\.me/)", re.IGNORECASE)


@Client.on_message(filters.group & ~filters.service, group=1)
@watcher_guard
async def anti_link_watcher(_: Client, message: Message) -> None:
    if not message.from_user:
        return
    setting = await cache_manager.get_chat_setting(message.chat.id, "antilink", default="on")
    if setting == "off":
        return

    text = message.text or message.caption
    if text and LINK_REGEX.search(text):
        member = await message.chat.get_member(message.from_user.id)
        if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return
        await message.delete()
