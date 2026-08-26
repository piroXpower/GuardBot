"""
================================================================================
SUPER GUARDIAN BOT - ADMIN MANAGEMENT SUITE
================================================================================
Module: bot.plugins.admin
Description:
    Provides promotion, demotion, title modification, pin/unpin controls,
    and administrator permission management.
================================================================================
"""

from __future__ import annotations

import logging
from typing import Optional, Union

from pyrogram import Client
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import ChatAdministratorRights, Message, User

from bot.core.decorators import require_admin
from bot.core.error_handler import auto_catch
from bot.core.registry import registry

logger = logging.getLogger("GuardianBot.Admin")


def extract_target_user(message: Message) -> Optional[Union[User, int, str]]:
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user
    if len(message.command) > 1:
        target = message.command[1]
        return int(target) if target.isdigit() else target
    return None


@registry.register("promote", "Admin", admin_only=True, desc="Promotes a member to admin")
@registry.register("fullpromote", "Admin", admin_only=True, desc="Promotes a member with full permissions")
@require_admin(["can_promote_members"])
@auto_catch
async def promote_user(client: Client, message: Message) -> None:
    target = extract_target_user(message)
    if not target:
        await message.reply_text("⚠️ **Usage**: `/promote @user [custom title]` or reply to target.")
        return

    uid = target.id if isinstance(target, User) else target
    is_full = message.command[0] == "fullpromote"

    rights = ChatAdministratorRights(
        can_change_info=True,
        can_post_messages=True,
        can_edit_messages=True,
        can_delete_messages=True,
        can_restrict_members=True,
        can_invite_users=True,
        can_pin_messages=True,
        can_promote_members=is_full,
        can_manage_video_chats=True,
        is_anonymous=False,
    )

    await client.promote_chat_member(message.chat.id, uid, privileges=rights)
    title = message.command[2] if len(message.command) > 2 else "Admin"
    try:
        await client.set_administrator_title(message.chat.id, uid, title)
    except Exception:
        pass

    await message.reply_text(f"👑 **Promoted**: `{uid}` as **{title}**.")


@registry.register("demote", "Admin", admin_only=True, desc="Demotes an admin to a regular member")
@require_admin(["can_promote_members"])
@auto_catch
async def demote_user(client: Client, message: Message) -> None:
    target = extract_target_user(message)
    if not target:
        await message.reply_text("⚠️ **Usage**: `/demote @user` or reply to target.")
        return

    uid = target.id if isinstance(target, User) else target
    empty_rights = ChatAdministratorRights(
        can_change_info=False,
        can_post_messages=False,
        can_edit_messages=False,
        can_delete_messages=False,
        can_restrict_members=False,
        can_invite_users=False,
        can_pin_messages=False,
        can_promote_members=False,
        can_manage_video_chats=False,
        is_anonymous=False,
    )
    await client.promote_chat_member(message.chat.id, uid, privileges=empty_rights)
    await message.reply_text(f"📉 **Demoted**: `{uid}` to regular member.")


@registry.register("pin", "Admin", admin_only=True, desc="Pins a replied message")
@registry.register("unpin", "Admin", admin_only=True, desc="Unpins a replied message")
@registry.register("unpinall", "Admin", admin_only=True, desc="Unpins all messages in group")
@require_admin(["can_pin_messages"])
@auto_catch
async def pin_handlers(client: Client, message: Message) -> None:
    cmd = message.command[0]
    if cmd == "unpinall":
        await client.unpin_all_chat_messages(message.chat.id)
        await message.reply_text("📌 **All pinned messages removed.**")
        return

    if not message.reply_to_message:
        await message.reply_text("⚠️ **Reply to a message** to pin/unpin it.")
        return

    if cmd == "pin":
        disable_notify = "silent" in message.text.lower()
        await client.pin_chat_message(message.chat.id, message.reply_to_message.id, disable_notification=disable_notify)
        await message.reply_text("📌 **Message pinned.**")
    elif cmd == "unpin":
        await client.unpin_chat_message(message.chat.id, message.reply_to_message.id)
        await message.reply_text("📌 **Message unpinned.**")


@registry.register("settitle", "Admin", admin_only=True, desc="Sets custom title for an admin")
@require_admin(["can_promote_members"])
@auto_catch
async def set_title_handler(client: Client, message: Message) -> None:
    if not message.reply_to_message or len(message.command) < 2:
        await message.reply_text("⚠️ **Usage**: Reply to an admin with `/settitle <New Title>`")
        return

    title = " ".join(message.command[1:])
    target_id = message.reply_to_message.from_user.id
    await client.set_administrator_title(message.chat.id, target_id, title)
    await message.reply_text(f"🏷️ **Title Updated**: `{title}` for `{target_id}`.")
