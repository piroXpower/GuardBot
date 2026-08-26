"""
================================================================================
SUPER GUARDIAN BOT - WARNS PLUGIN
================================================================================
Module: bot.plugins.warns
Description:
    Issues warning strikes to users with automated escalation upon reaching limits.
================================================================================
"""

from __future__ import annotations

from pyrogram import Client
from pyrogram.types import Message

from bot.core.decorators import require_admin
from bot.core.error_handler import auto_catch
from bot.core.registry import registry
from bot.database.cache import cache_manager


@registry.register("warn", "Warns", admin_only=True)
@require_admin(["can_restrict_members"])
@auto_catch
async def warn_user(_: Client, message: Message) -> None:
    if not message.reply_to_message or not message.reply_to_message.from_user:
        await message.reply_text("⚠️ Reply to a message to warn the user.")
        return
    target = message.reply_to_message.from_user
    chat_id = message.chat.id
    current_warns = await cache_manager.add_chat_warning(chat_id, target.id)
    if current_warns >= 3:
        await message.chat.ban_member(target.id)
        await cache_manager.reset_chat_warnings(chat_id, target.id)
        await message.reply_text(f"🔨 {target.mention} exceeded strike limit (3/3) and was banned.")
    else:
        await message.reply_text(f"⚠️ {target.mention} warned: `{current_warns}/3` strikes.")


@registry.register("unwarn", "Warns", admin_only=True)
@require_admin(["can_restrict_members"])
@auto_catch
async def unwarn_user(_: Client, message: Message) -> None:
    if not message.reply_to_message or not message.reply_to_message.from_user:
        await message.reply_text("⚠️ Reply to a message to reset strikes.")
        return
    target = message.reply_to_message.from_user
    await cache_manager.reset_chat_warnings(message.chat.id, target.id)
    await message.reply_text(f"✅ Reset warning strikes for {target.mention}.")
