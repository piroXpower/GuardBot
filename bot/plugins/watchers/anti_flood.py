"""
================================================================================
SUPER GUARDIAN BOT - ANTI-FLOOD WATCHER
================================================================================
Module: bot.plugins.watchers.anti_flood
Description:
    Sliding-window flood detection tracking user message velocity in memory.
================================================================================
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Dict, List

from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import Message

from bot.core.error_handler import watcher_guard

FLOOD_CACHE: Dict[int, List[float]] = defaultdict(list)
FLOOD_LIMIT = 5
FLOOD_WINDOW = 3


@Client.on_message(filters.group & ~filters.service, group=2)
@watcher_guard
async def anti_flood_watcher(_: Client, message: Message) -> None:
    if not message.from_user:
        return
    uid = message.from_user.id
    now = time.time()
    FLOOD_CACHE[uid] = [t for t in FLOOD_CACHE[uid] if now - t < FLOOD_WINDOW]
    FLOOD_CACHE[uid].append(now)

    if len(FLOOD_CACHE[uid]) > FLOOD_LIMIT:
        member = await message.chat.get_member(uid)
        if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return
        await message.delete()
