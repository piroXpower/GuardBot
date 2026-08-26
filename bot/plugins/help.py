"""
================================================================================
SUPER GUARDIAN BOT - HELP PLUGIN
================================================================================
Module: bot.plugins.help
Description:
    Renders the interactive category-based help menu matching the UI layout.
================================================================================
"""

from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message

from bot.core.error_handler import auto_catch
from bot.database.cache import get_user_language
from bot.utils.i18n import tr
from bot.utils.keyboards import get_back_to_help_kb, get_help_kb


@Client.on_message(filters.command("help"))
@auto_catch
async def handle_help_cmd(_: Client, message: Message) -> None:
    lang = await get_user_language(message.from_user.id)
    await message.reply_text(
        text=tr(lang, "help_main_text"),
        reply_markup=get_help_kb(lang),
        disable_web_page_preview=True,
    )


@Client.on_callback_query(filters.regex("^btn_help$"))
@auto_catch
async def handle_help_main(_: Client, query: CallbackQuery) -> None:
    lang = await get_user_language(query.from_user.id)
    await query.message.edit_text(
        text=tr(lang, "help_main_text"),
        reply_markup=get_help_kb(lang),
        disable_web_page_preview=True,
    )


@Client.on_callback_query(filters.regex(r"^help_(prot|mem|nsfw|flood|link|warn|lock|cmds)$"))
@auto_catch
async def handle_help_sub(_: Client, query: CallbackQuery) -> None:
    category = query.data.split("_")[1]
    lang = await get_user_language(query.from_user.id)
    await query.message.edit_text(
        text=tr(lang, f"help_details.{category}"),
        reply_markup=get_back_to_help_kb(lang),
        disable_web_page_preview=True,
    )
