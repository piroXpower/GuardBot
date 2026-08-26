"""
================================================================================
SUPER GUARDIAN BOT - LANGUAGE SETTINGS PLUGIN
================================================================================
Module: bot.plugins.language
Description:
    Provides interactive language selection menus and persists user preferences.
================================================================================
"""

from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message

from bot.core.error_handler import auto_catch
from bot.database.cache import set_user_language
from bot.utils.i18n import tr
from bot.utils.keyboards import get_home_kb, get_lang_kb


@Client.on_message(filters.command(["language", "lang", "setlang"]))
@auto_catch
async def handle_lang_cmd(_: Client, message: Message) -> None:
    await message.reply_text(
        text="🌐 **Select your preferred language / अपनी भाषा चुनें:**",
        reply_markup=get_lang_kb(),
    )


@Client.on_callback_query(filters.regex("^btn_lang_menu$"))
@auto_catch
async def handle_lang_menu(_: Client, query: CallbackQuery) -> None:
    await query.message.edit_text(
        text="🌐 **Select your preferred language / अपनी भाषा चुनें:**",
        reply_markup=get_lang_kb(),
    )


@Client.on_callback_query(filters.regex(r"^setlang_([a-z]{2})$"))
@auto_catch
async def handle_set_lang(_: Client, query: CallbackQuery) -> None:
    lang_code = query.data.split("_")[1]
    await set_user_language(query.from_user.id, lang_code)
    await query.answer(tr(lang_code, "lang_selected"), show_alert=True)
    await query.message.edit_text(
        text=tr(lang_code, "home_text"),
        reply_markup=get_home_kb(lang_code),
        disable_web_page_preview=True,
    )
