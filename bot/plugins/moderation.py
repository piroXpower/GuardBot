"""
================================================================================
SUPER GUARDIAN BOT - MODERATION PLUGIN
================================================================================
Module: bot.plugins.moderation
Description:
    Core moderation actions: bans, silent bans, temp bans, mutes, kicks, and unbans.
================================================================================
"""

from __future__ import annotations

from pyrogram import Client
from pyrogram.types import ChatPermissions, Message, User

from bot.core.decorators import require_admin
from bot.core.error_handler import auto_catch
from bot.core.registry import registry
from bot.utils.time_parser import parse_time


def extract_user(message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user
    if len(message.command) > 1:
        target = message.command[1]
        return int(target) if target.isdigit() else target
    return None


@registry.register("ban", "Moderation", admin_only=True)
@registry.register("sban", "Moderation", admin_only=True)
@require_admin(["can_restrict_members"])
@auto_catch
async def ban_cmd(_: Client, message: Message) -> None:
    target = extract_user(message)
    if not target:
        await message.reply_text("⚠️ **Usage**: `/ban @user` or reply to target.")
        return
    uid = target.id if isinstance(target, User) else target
    await message.chat.ban_member(uid)
    if message.command[0] == "sban" and message.reply_to_message:
        await message.reply_to_message.delete()
        await message.delete()
    else:
        await message.reply_text(f"🔨 **Banned**: `{uid}`")


@registry.register("tban", "Moderation", admin_only=True)
@require_admin(["can_restrict_members"])
@auto_catch
async def tban_cmd(_: Client, message: Message) -> None:
    if len(message.command) < 2 and not message.reply_to_message:
        await message.reply_text("⚠️ **Usage**: `/tban @user 2h` or reply with `/tban 2h`.")
        return
    dur_str = message.command[1] if message.reply_to_message else message.command[2]
    until = parse_time(dur_str)
    if not until:
        await message.reply_text("❌ Invalid format: Use `10m`, `2h`, `7d`.")
        return
    target = extract_user(message)
    uid = target.id if isinstance(target, User) else target
    await message.chat.ban_member(uid, until_date=until)
    await message.reply_text(f"⏳ **Banned for {dur_str}**: `{uid}`")


@registry.register("unban", "Moderation", admin_only=True)
@require_admin(["can_restrict_members"])
@auto_catch
async def unban_cmd(_: Client, message: Message) -> None:
    target = extract_user(message)
    if not target:
        await message.reply_text("⚠️ **Usage**: `/unban @user` or reply to target.")
        return
    uid = target.id if isinstance(target, User) else target
    await message.chat.unban_member(uid)
    await message.reply_text(f"✅ **Unbanned**: `{uid}`")


@registry.register("mute", "Moderation", admin_only=True)
@registry.register("unmute", "Moderation", admin_only=True)
@require_admin(["can_restrict_members"])
@auto_catch
async def mute_cmd(_: Client, message: Message) -> None:
    target = extract_user(message)
    if not target:
        await message.reply_text("⚠️ **Usage**: `/mute` or `/unmute`.")
        return
    uid = target.id if isinstance(target, User) else target
    if message.command[0] == "unmute":
        await message.chat.restrict_member(uid, ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True))
        await message.reply_text(f"🔊 **Unmuted**: `{uid}`")
    else:
        await message.chat.restrict_member(uid, ChatPermissions(can_send_messages=False))
        await message.reply_text(f"🔇 **Muted**: `{uid}`")


@registry.register("kick", "Moderation", admin_only=True)
@require_admin(["can_restrict_members"])
@auto_catch
async def kick_cmd(_: Client, message: Message) -> None:
    target = extract_user(message)
    if not target:
        await message.reply_text("⚠️ **Usage**: `/kick @user` or reply to target.")
        return
    uid = target.id if isinstance(target, User) else target
    await message.chat.ban_member(uid)
    await message.chat.unban_member(uid)
    await message.reply_text(f"👞 **Kicked**: `{uid}`")
