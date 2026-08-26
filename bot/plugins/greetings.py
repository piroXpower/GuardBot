"""
================================================================================
SUPER GUARDIAN BOT - GREETINGS & VERIFICATION CAPTCHA
================================================================================
Module: bot.plugins.greetings
Description:
    Handles dynamic group greetings, service message deletions, and math captchas
    for new members.
================================================================================
"""

from __future__ import annotations

import asyncio
import logging
import random
import time
from typing import Any, Dict, List, Tuple

from pyrogram import Client, filters
from pyrogram.types import (
    CallbackQuery,
    ChatPermissions,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from bot.core.decorators import require_admin
from bot.core.error_handler import auto_catch, watcher_guard
from bot.core.registry import registry
from bot.database.cache import cache_manager

logger = logging.getLogger("GuardianBot.Greetings")

PENDING_CAPTCHAS: Dict[Tuple[int, int], Dict[str, Any]] = {}
DEFAULT_WELCOME = "👋 Welcome to **{chat_title}**, {user_mention}!"


def create_math_challenge() -> Tuple[str, int, List[int]]:
    a = random.randint(2, 10)
    b = random.randint(1, 9)
    answer = a + b
    options = {answer}
    while len(options) < 4:
        options.add(random.randint(3, 19))
    opt_list = list(options)
    random.shuffle(opt_list)
    return f"`{a} + {b} = ?`", answer, opt_list


@Client.on_message(filters.group & filters.new_chat_members, group=5)
@watcher_guard
async def greetings_watcher(client: Client, message: Message) -> None:
    chat_id = message.chat.id
    captcha_on = (await cache_manager.get_chat_setting(chat_id, "captcha", default="off")) == "on"

    for member in message.new_chat_members:
        if member.is_bot:
            continue

        if captcha_on:
            try:
                await message.chat.restrict_member(member.id, ChatPermissions(can_send_messages=False))
            except Exception:
                pass

            prompt, answer, options = create_math_challenge()
            buttons = [
                [
                    InlineKeyboardButton(str(options[0]), callback_data=f"cpt_{chat_id}_{member.id}_{options[0]}"),
                    InlineKeyboardButton(str(options[1]), callback_data=f"cpt_{chat_id}_{member.id}_{options[1]}"),
                ],
                [
                    InlineKeyboardButton(str(options[2]), callback_data=f"cpt_{chat_id}_{member.id}_{options[2]}"),
                    InlineKeyboardButton(str(options[3]), callback_data=f"cpt_{chat_id}_{member.id}_{options[3]}"),
                ]
            ]
            msg = await client.send_message(
                chat_id,
                f"🛡️ Welcome {member.mention}! Solve the captcha within 120s to speak:\n👉 {prompt}",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            PENDING_CAPTCHAS[(chat_id, member.id)] = {"ans": answer, "msg_id": msg.id}
        else:
            tmpl = await cache_manager.get_chat_setting(chat_id, "welcome_msg", DEFAULT_WELCOME)
            text = tmpl.format(
                chat_title=message.chat.title,
                user_mention=member.mention,
                user_id=member.id,
                user_first=member.first_name,
            )
            await client.send_message(chat_id, text, disable_web_page_preview=True)


@Client.on_callback_query(filters.regex(r"^cpt_(-?\d+)_(\d+)_(\d+)$"))
@auto_catch
async def captcha_callback(client: Client, query: CallbackQuery) -> None:
    parts = query.data.split("_")
    chat_id = int(parts[1])
    user_id = int(parts[2])
    selected = int(parts[3])

    if query.from_user.id != user_id:
        await query.answer("⛔ Not your challenge.", show_alert=True)
        return

    key = (chat_id, user_id)
    record = PENDING_CAPTCHAS.get(key)
    if not record:
        await query.answer("⚠️ Expired.", show_alert=True)
        try:
            await query.message.delete()
        except Exception:
            pass
        return

    if selected == record["ans"]:
        del PENDING_CAPTCHAS[key]
        await client.set_chat_permissions(
            chat_id,
            ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
            )
        )
        await query.answer("✅ Verification complete!", show_alert=False)
        await query.message.edit_text(f"✅ {query.from_user.mention} is now verified.")
    else:
        del PENDING_CAPTCHAS[key]
        await query.answer("❌ Incorrect answer.", show_alert=True)
        try:
            await query.message.delete()
            await client.ban_chat_member(chat_id, user_id)
            await client.unban_chat_member(chat_id, user_id)
        except Exception:
            pass


@registry.register("welcome", "Greetings", admin_only=True, desc="Configure welcome messages")
@require_admin(["can_change_info"])
@auto_catch
async def welcome_config(_: Client, message: Message) -> None:
    chat_id = message.chat.id
    if len(message.command) < 2:
        status = await cache_manager.get_chat_setting(chat_id, "welcome", default="on")
        tmpl = await cache_manager.get_chat_setting(chat_id, "welcome_msg", DEFAULT_WELCOME)
        await message.reply_text(
            f"👋 **Welcome Setting**: `{status.upper()}`\n\n"
            f"**Template**:\n{tmpl}\n\n"
            f"Usage: `/welcome on`, `/welcome off`, `/welcome set <text>`, `/welcome reset`"
        )
        return

    sub = message.command[1].lower()
    if sub == "on":
        await cache_manager.set_chat_setting(chat_id, "welcome", "on")
        await message.reply_text("✅ Welcome messages enabled.")
    elif sub == "off":
        await cache_manager.set_chat_setting(chat_id, "welcome", "off")
        await message.reply_text("❌ Welcome messages disabled.")
    elif sub == "reset":
        await cache_manager.set_chat_setting(chat_id, "welcome_msg", DEFAULT_WELCOME)
        await message.reply_text("🔄 Welcome template reset.")
    elif sub == "set" and len(message.command) > 2:
        new_tmpl = message.text.split(None, 2)[2]
        await cache_manager.set_chat_setting(chat_id, "welcome_msg", new_tmpl)
        await message.reply_text("✅ Custom welcome message saved.")


@registry.register("captcha", "Greetings", admin_only=True, desc="Configure entry captcha")
@require_admin(["can_restrict_members"])
@auto_catch
async def captcha_config(_: Client, message: Message) -> None:
    if len(message.command) < 2:
        status = await cache_manager.get_chat_setting(message.chat.id, "captcha", default="off")
        await message.reply_text(f"🛡️ **Captcha Status**: `{status.upper()}`\nUsage: `/captcha on` or `/captcha off`")
        return

    mode = message.command[1].lower()
    if mode in ["on", "enable"]:
        await cache_manager.set_chat_setting(message.chat.id, "captcha", "on")
        await message.reply_text("🔒 Captcha challenge enabled.")
    elif mode in ["off", "disable"]:
        await cache_manager.set_chat_setting(message.chat.id, "captcha", "off")
        await message.reply_text("🔓 Captcha challenge disabled.")
