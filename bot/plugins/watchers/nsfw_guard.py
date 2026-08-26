"""
================================================================================
SUPER GUARDIAN BOT - NSFW GUARD WATCHER
================================================================================
Module: bot.plugins.watchers.nsfw_guard
Description:
    Media ingestion hook for processing images, stickers, videos, and animations.
================================================================================
"""

from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import Message

from bot.core.error_handler import watcher_guard
from bot.database.cache import cache_manager


@Client.on_message(filters.group & (filters.photo | filters.video | filters.animation), group=4)
@watcher_guard
async def nsfw_classifier_watcher(_: Client, message: Message) -> None:
    if not message.from_user:
        return
    setting = await cache_manager.get_chat_setting(message.chat.id, "nsfw", default="off")
    if setting == "off":
        return
    member = await message.chat.get_member(message.from_user.id)
    if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        return
