"""
================================================================================
SUPER GUARDIAN BOT - PERMISSIONS & LOCKS PLUGIN
================================================================================
Module: bot.plugins.locks
Description:
    Granular permission toggles for text, media, stickers, polls, and emergency lockdowns.
================================================================================
"""

from __future__ import annotations

from pyrogram import Client
from pyrogram.types import ChatPermissions, Message

from bot.core.decorators import require_admin
from bot.core.error_handler import auto_catch
from bot.core.registry import registry

LOCK_TYPES = {
    "msg": "can_send_messages",
    "media": "can_send_media_messages",
    "stickers": "can_send_other_messages",
    "polls": "can_send_polls",
    "webprev": "can_add_web_page_previews",
    "invite": "can_invite_users",
    "pin": "can_pin_messages",
}


@registry.register("lock", "Locks", admin_only=True)
@registry.register("unlock", "Locks", admin_only=True)
@require_admin(["can_change_info"])
@auto_catch
async def lock_toggle(client: Client, message: Message) -> None:
    if len(message.command) < 2:
        await message.reply_text(f"⚠️ **Usage**: `/{message.command[0]} <type>`\nTypes: `{', '.join(LOCK_TYPES.keys())}`")
        return
    target_type = message.command[1].lower()
    if target_type not in LOCK_TYPES:
        await message.reply_text("❌ Invalid lock type.")
        return

    is_lock = message.command[0] == "lock"
    perm_attr = LOCK_TYPES[target_type]
    chat = await client.get_chat(message.chat.id)
    perms = chat.permissions or ChatPermissions()
    perm_dict = {k: getattr(perms, k, True) for k in LOCK_TYPES.values()}
    perm_dict[perm_attr] = not is_lock

    await client.set_chat_permissions(message.chat.id, ChatPermissions(**perm_dict))
    await message.reply_text(f"🔒 **{target_type}** is now **{'Locked' if is_lock else 'Unlocked'}**.")


@registry.register("lockdown", "Locks", admin_only=True)
@registry.register("unlockdown", "Locks", admin_only=True)
@require_admin(["can_change_info"])
@auto_catch
async def lockdown_toggle(client: Client, message: Message) -> None:
    is_lock = message.command[0] == "lockdown"
    all_perms = ChatPermissions(
        can_send_messages=not is_lock,
        can_send_media_messages=not is_lock,
        can_send_other_messages=not is_lock,
        can_send_polls=not is_lock,
        can_add_web_page_previews=not is_lock,
        can_invite_users=not is_lock,
        can_pin_messages=not is_lock,
    )
    await client.set_chat_permissions(message.chat.id, all_perms)
    await message.reply_text("🚨 **LOCKDOWN ACTIVE**" if is_lock else "🔓 **LOCKDOWN LIFTED**")
