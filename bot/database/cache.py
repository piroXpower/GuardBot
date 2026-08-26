"""
================================================================================
SUPER GUARDIAN BOT - HYBRID IN-MEMORY & TELEGRAM CHANNEL STORAGE
================================================================================
Module: bot.database.cache
Description:
    Zero-Redis storage layer. Provides sub-millisecond in-memory dictionary
    lookups for rate-limiting, warnings, and chat configs, combined with an
    automated asynchronous JSON backup loop to a private Telegram channel.
================================================================================
"""

from __future__ import annotations

import asyncio
import io
import logging
import os
import time
from typing import Any, Dict, List, Optional

import ujson as json
from pyrogram import Client

from config import LOG_CHANNEL_ID

logger = logging.getLogger("GuardianBot.ChannelDB")

BACKUP_INTERVAL_SECONDS: int = 300  # Syncs JSON to channel every 5 minutes


class HybridChannelStorage:
    """In-memory state engine backed up asynchronously to a private Telegram channel."""

    def __init__(self) -> None:
        self.chat_configs: Dict[str, Dict[str, str]] = {}
        self.user_languages: Dict[str, str] = {}
        self.warnings: Dict[str, int] = {}
        self.rate_limits: Dict[str, List[float]] = {}
        self.is_loaded: bool = False
        self._lock = asyncio.Lock()
        self._backup_task: Optional[asyncio.Task] = None

    # --------------------------------------------------------------------------
    # Fast In-Memory Operations
    # --------------------------------------------------------------------------

    async def initialize(self) -> None:
        """Compatibility hook for bootstrapper."""
        logger.info("In-memory database cache initialized.")

    async def close(self) -> None:
        """Stops background tasks and cancels backup loop."""
        if self._backup_task and not self._backup_task.done():
            self._backup_task.cancel()
        logger.info("Storage engine closed cleanly.")

    async def check_flood_rate_limit(self, chat_id: int, user_id: int, limit: int = 5, window: int = 3) -> bool:
        """Sliding-window atomic rate limiter via in-memory timestamps."""
        key = f"{chat_id}:{user_id}"
        now = time.time()
        stamps = self.rate_limits.get(key, [])
        stamps = [t for t in stamps if now - t < window]
        stamps.append(now)
        self.rate_limits[key] = stamps
        return len(stamps) > limit

    async def get_chat_setting(self, chat_id: int, setting: str, default: str = "off") -> str:
        return self.chat_configs.get(str(chat_id), {}).get(setting, default)

    async def set_chat_setting(self, chat_id: int, setting: str, value: str) -> None:
        cid = str(chat_id)
        if cid not in self.chat_configs:
            self.chat_configs[cid] = {}
        self.chat_configs[cid][setting] = value

    async def add_chat_warning(self, chat_id: int, user_id: int) -> int:
        key = f"{chat_id}:{user_id}"
        self.warnings[key] = self.warnings.get(key, 0) + 1
        return self.warnings[key]

    async def reset_chat_warnings(self, chat_id: int, user_id: int) -> None:
        self.warnings.pop(f"{chat_id}:{user_id}", None)

    async def get_user_language(self, user_id: int) -> str:
        return self.user_languages.get(str(user_id), "en")

    async def set_user_language(self, user_id: int, lang: str) -> None:
        self.user_languages[str(user_id)] = lang

    # --------------------------------------------------------------------------
    # Telegram Channel Synchronization
    # --------------------------------------------------------------------------

    async def load_from_channel(self, client: Client) -> None:
        """Downloads the latest database JSON document from the storage channel upon startup."""
        try:
            logger.info("Fetching latest database snapshot from channel %s...", LOG_CHANNEL_ID)
            async for message in client.get_chat_history(LOG_CHANNEL_ID, limit=15):
                if message.document and message.document.file_name == "guardian_db.json":
                    file_bytes = await client.download_media(message, in_memory=True)
                    data = json.loads(file_bytes.getvalue().decode("utf-8"))
                    self.chat_configs = data.get("chat_configs", {})
                    self.user_languages = data.get("user_languages", {})
                    self.warnings = data.get("warnings", {})
                    self.is_loaded = True
                    logger.info("Database loaded successfully from Telegram channel (%d chats).", len(self.chat_configs))
                    return
            logger.warning("No previous database backup found. Initializing clean storage.")
            self.is_loaded = True
        except Exception as e:
            logger.error("Failed to load database from channel: %s", e)
            self.is_loaded = True

    async def backup_to_channel(self, client: Client) -> None:
        """Dumps in-memory state to a JSON file and uploads it to the private channel."""
        async with self._lock:
            try:
                payload = {
                    "chat_configs": self.chat_configs,
                    "user_languages": self.user_languages,
                    "warnings": self.warnings,
                    "timestamp": time.time(),
                }
                raw_data = json.dumps(payload, indent=2).encode("utf-8")
                doc = io.BytesIO(raw_data)
                doc.name = "guardian_db.json"

                await client.send_document(
                    chat_id=LOG_CHANNEL_ID,
                    document=doc,
                    caption=(
                        f"📦 **Database Auto-Backup**\n"
                        f"🕒 `{time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}`\n"
                        f"👥 Active Chats: `{len(self.chat_configs)}`\n"
                        f"🌐 Users Cached: `{len(self.user_languages)}`"
                    ),
                )
                logger.info("Database successfully backed up to Telegram channel.")
            except Exception as e:
                logger.error("Failed to upload backup to Telegram channel: %s", e)

    def start_auto_backup_loop(self, client: Client) -> None:
        """Spawns the background synchronization task."""
        self._backup_task = asyncio.create_task(self._auto_backup_worker(client))

    async def _auto_backup_worker(self, client: Client) -> None:
        while True:
            try:
                await asyncio.sleep(BACKUP_INTERVAL_SECONDS)
                await self.backup_to_channel(client)
            except asyncio.CancelledError:
                break
            except Exception as loop_err:
                logger.error("Auto backup worker error: %s", loop_err)


# Global storage instance
cache_manager = HybridChannelStorage()

async def check_flood_rate_limit(chat_id: int, user_id: int, limit: int = 5, window: int = 3) -> bool:
    return await cache_manager.check_flood_rate_limit(chat_id, user_id, limit, window)

async def set_user_language(user_id: int, lang_code: str) -> None:
    await cache_manager.set_user_language(user_id, lang_code)

async def get_user_language(user_id: int) -> str:
    return await cache_manager.get_user_language(user_id)
