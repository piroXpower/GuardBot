"""
================================================================================
SUPER GUARDIAN BOT - INLINE KEYBOARDS
================================================================================
Module: bot.utils.keyboards
================================================================================
"""

from __future__ import annotations

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import BOT_USERNAME, CHANNEL_LINK, GITHUB_REPO, OWNER_USERNAME, SUPPORT_CHAT, SUPPORTED_LANGUAGES
from bot.utils.i18n import tr


def get_home_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"➕ {tr(lang, 'buttons.add_me')}", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")],
        [
            InlineKeyboardButton(f"📡 {tr(lang, 'buttons.source')}", callback_data="btn_source"),
            InlineKeyboardButton(f"💬 {tr(lang, 'buttons.support')}", url=SUPPORT_CHAT),
        ],
        [
            InlineKeyboardButton(f"📖 {tr(lang, 'buttons.help')}", callback_data="btn_help"),
            InlineKeyboardButton(f"👑 {tr(lang, 'buttons.owner')}", url=f"https://t.me/{OWNER_USERNAME}"),
        ],
        [InlineKeyboardButton(f"🌐 {tr(lang, 'buttons.language')}", callback_data="btn_lang_menu")],
    ])


def get_source_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💻 GitHub", url=GITHUB_REPO),
            InlineKeyboardButton("📢 Channel", url=CHANNEL_LINK),
        ],
        [InlineKeyboardButton(f"◀️ {tr(lang, 'buttons.back')}", callback_data="btn_home")],
    ])


def get_help_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"🛡️ {tr(lang, 'help_categories.protection')}", callback_data="help_prot"),
            InlineKeyboardButton(f"👤 {tr(lang, 'help_categories.members')}", callback_data="help_mem"),
        ],
        [
            InlineKeyboardButton(f"🔞 {tr(lang, 'help_categories.nsfw')}", callback_data="help_nsfw"),
            InlineKeyboardButton(f"🌊 {tr(lang, 'help_categories.flood')}", callback_data="help_flood"),
        ],
        [
            InlineKeyboardButton(f"🔗 {tr(lang, 'help_categories.link')}", callback_data="help_link"),
            InlineKeyboardButton(f"⚠️ {tr(lang, 'help_categories.warnings')}", callback_data="help_warn"),
        ],
        [
            InlineKeyboardButton(f"🔒 {tr(lang, 'help_categories.lockdown')}", callback_data="help_lock"),
            InlineKeyboardButton(f"📖 {tr(lang, 'help_categories.commands')}", callback_data="help_cmds"),
        ],
        [InlineKeyboardButton(f"◀️ {tr(lang, 'buttons.back')}", callback_data="btn_home")],
    ])


def get_back_to_help_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"◀️ {tr(lang, 'buttons.back')}", callback_data="btn_help")]
    ])


def get_lang_kb() -> InlineKeyboardMarkup:
    buttons = []
    items = list(SUPPORTED_LANGUAGES.items())
    for i in range(0, len(items), 2):
        row = [InlineKeyboardButton(items[i][1], callback_data=f"setlang_{items[i][0]}")]
        if i + 1 < len(items):
            row.append(InlineKeyboardButton(items[i + 1][1], callback_data=f"setlang_{items[i + 1][0]}"))
        buttons.append(row)
    buttons.append([InlineKeyboardButton("◀️ Back", callback_data="btn_home")])
    return InlineKeyboardMarkup(buttons)
                
