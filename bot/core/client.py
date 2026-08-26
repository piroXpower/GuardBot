"""
================================================================================
SUPER GUARDIAN BOT - CLIENT SUBSYSTEM
================================================================================
Module: bot.core.client
================================================================================
"""

from __future__ import annotations

import asyncio
import logging
import sys
import time
from typing import Any, List, Optional

from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.errors import (
    AuthKeyDuplicated,
    AuthKeyInvalid,
    FloodWait,
    NetworkMigrate,
    SessionRevoked,
    Unauthorized,
)
from pyrogram.types import BotCommand, User

from config import API_HASH, API_ID, BOT_TOKEN

logger = logging.getLogger("GuardianBot.Client")


class ClientHealthTracker:
    def __init__(self) -> None:
        self.boot_time: float = time.time()
        self.is_connected: bool = False
        self.total_updates_processed: int = 0
        self.last_heartbeat: float = time.time()

    def record_update(self) -> None:
        self.total_updates_processed += 1
        self.last_heartbeat = time.time()

    @property
    def uptime_seconds(self) -> float:
        return time.time() - self.boot_time


class GuardianClient(Client):
    def __init__(self) -> None:
        super().__init__(
            name="SuperGuardianBotInstance",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="bot/plugins"),
            workers=128,
            max_concurrent_transmissions=10,
            parse_mode=ParseMode.DEFAULT,
            sleep_threshold=60,
        )
        self.me: Optional[User] = None
        self.tracker: ClientHealthTracker = ClientHealthTracker()
        self._is_stopping: bool = False
        self._background_tasks: List[asyncio.Task[Any]] = []

    async def start(self) -> None:
        try:
            await super().start()
            self.me = await self.get_me()
            self.tracker.is_connected = True
            await self._setup_default_commands()
            self._background_tasks.append(asyncio.create_task(self._heartbeat_loop()))
        except (Unauthorized, AuthKeyInvalid, AuthKeyDuplicated, SessionRevoked) as auth_err:
            logger.critical("Authentication error: %s", auth_err)
            sys.exit(1)
        except NetworkMigrate:
            await asyncio.sleep(2)
            await self.start()
        except FloodWait as flood_err:
            await asyncio.sleep(flood_err.value + 1)
            await self.start()

    async def stop(self, *args: Any) -> None:
        if self._is_stopping:
            return
        self._is_stopping = True
        for task in self._background_tasks:
            if not task.done():
                task.cancel()
        self.tracker.is_connected = False
        await super().stop()

    async def _setup_default_commands(self) -> None:
        try:
            commands = [
                BotCommand("start", "Start the bot and view dashboard"),
                BotCommand("help", "Open full command and help list"),
                BotCommand("ping", "Check bot latency"),
                BotCommand("id", "Get chat and user IDs"),
            ]
            await self.set_bot_commands(commands)
        except Exception as e:
            logger.warning("Failed to register Telegram UI commands: %s", e)

    async def _heartbeat_loop(self) -> None:
        while not self._is_stopping:
            try:
                await asyncio.sleep(30)
                if self.is_connected:
                    self.tracker.last_heartbeat = time.time()
            except asyncio.CancelledError:
                break


client = GuardianClient()
        
