"""
================================================================================
SUPER GUARDIAN BOT - START PLUGIN
================================================================================
Module: bot.plugins.start
Description:
    Renders the primary home screen and interactive navigation dashboard.
================================================================================
"""

from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message

from bot.core.error_handler import auto_catch
from bot.database.cache import get_user_language
from bot.utils.i18n import tr
from bot.utils.keyboards import get_home_kb


@Client.on_message(filters.command("start") & filters.private)
@auto_catch
async def handle_start(_: Client, message: Message) -> None:
    lang = await get_user_language(message.from_user.id)
    await message.reply_text(
        text=tr(lang, "home_text"),
        reply_markup=get_home_kb(lang),
        disable_web_page_preview=True,
    )


@Client.on_callback_query(filters.regex("^btn_home$"))
@auto_catch
async def handle_home_cb(_: Client, query: CallbackQuery) -> None:
    lang = await get_user_language(query.from_user.id)
    await query.message.edit_text(
        text=tr(lang, "home_text"),
        reply_markup=get_home_kb(lang),
        disable_web_page_preview=True,
    )
