"""
================================================================================
SUPER GUARDIAN BOT - BAD WORDS WATCHER
================================================================================
Module: bot.plugins.watchers.bad_words
Description:
    Filter that removes toxic phrases, abusive terms, and crypto scams.
================================================================================
"""

from __future__ import annotations

import re
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import Message

from bot.core.error_handler import watcher_guard

FILTER_REGEX = re.compile(r"\b(scamlink|freecrypto|toxicabuse)\b", re.IGNORECASE)


@Client.on_message(filters.group & ~filters.service, group=3)
@watcher_guard
async def bad_words_filter(_: Client, message: Message) -> None:
    text = message.text or message.caption
    if not text or not message.from_user:
        return
    if FILTER_REGEX.search(text):
        member = await message.chat.get_member(message.from_user.id)
        if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return
        await message.delete()
