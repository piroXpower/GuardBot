"""
================================================================================
SUPER GUARDIAN BOT - GLOBAL CONFIGURATION
================================================================================
"""

from __future__ import annotations

import os

API_ID: int = int(os.getenv("API_ID", "12345678"))
API_HASH: str = os.getenv("API_HASH", "your_api_hash_here")
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "your_bot_token_here")
BOT_USERNAME: str = os.getenv("BOT_USERNAME", "SuperGuardiansBot")
OWNER_USERNAME: str = os.getenv("OWNER_USERNAME", "YourTelegramHandle")
SUPPORT_CHAT: str = os.getenv("SUPPORT_CHAT", "https://t.me/YourSupportGroup")
GITHUB_REPO: str = os.getenv("GITHUB_REPO", "https://github.com/your-repo")
CHANNEL_LINK: str = os.getenv("CHANNEL_LINK", "https://t.me/YourChannel")
REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

SUPPORTED_LANGUAGES: dict[str, str] = {
    "en": "🇺🇸 English",
    "hi": "🇮🇳 हिन्दी",
    "es": "🇪🇸 Español",
    "ru": "🇷🇺 Русский",
    "ar": "🇸🇦 العربية",
    "id": "🇮🇩 Bahasa Indonesia",
    "pt": "🇧🇷 Português",
    "fr": "🇫🇷 Français",
    "de": "🇩🇪 Deutsch",
    "it": "🇮🇹 Italiano",
    "tr": "🇹🇷 Türkçe",
    "ja": "🇯🇵 日本語",
}
