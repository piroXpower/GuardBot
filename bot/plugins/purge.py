"""
================================================================================
SUPER GUARDIAN BOT - PURGE PLUGIN
================================================================================
Module: bot.plugins.purge
Description:
    High-speed batch message deletion for message sweep operations.
================================================================================
"""

from __future__ import annotations

from pyrogram import Client
from pyrogram.types import Message

from bot.core.decorators import require_admin
from bot.core.error_handler import auto_catch
from bot.core.registry import registry


@registry.register("purge", "Purge", admin_only=True)
@registry.register("spurge", "Purge", admin_only=True)
@require_admin(["can_delete_messages"])
@auto_catch
async def purge_cmd(client: Client, message: Message) -> None:
    if not message.reply_to_message:
        await message.reply_text("⚠️ Reply to a message to start purging from.")
        return
    msg_ids = list(range(message.reply_to_message.id, message.id + 1))
    for i in range(0, len(msg_ids), 100):
        await client.delete_messages(message.chat.id, msg_ids[i:i + 100])
    if message.command[0] != "spurge":
        ack = await client.send_message(message.chat.id, f"🧹 Purged {len(msg_ids)} messages.")
        await client.delete_messages(message.chat.id, [ack.id])
