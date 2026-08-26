"""
================================================================================
SUPER GUARDIAN BOT - WORKER BOOTSTRAPPER (WITHOUT REDIS)
================================================================================
Module: bot.__main__
================================================================================
"""

from __future__ import annotations

import asyncio
import logging
import signal
import sys
import uvloop
from pyrogram import idle

from bot import (
    __version__,
    app,
    cache_manager,
    logger,
    registry,
    telemetry,
)

main_logger = logging.getLogger("GuardianBot.Main")


class GuardianBootstrapper:
    def __init__(self) -> None:
        self.is_running: bool = False
        self._shutdown_event: Optional[asyncio.Event] = None

    async def shutdown(self, signal_name: str) -> None:
        if not self.is_running:
            return

        main_logger.warning("Received shutdown signal: %s. Performing final backup...", signal_name)
        self.is_running = False

        # Perform a final backup on shutdown before closing
        if app.is_initialized:
            try:
                await cache_manager.backup_to_channel(app)
            except Exception as e:
                main_logger.error("Final backup failed: %s", e)

            try:
                await app.stop()
                main_logger.info("Telegram MTProto gateway disconnected.")
            except Exception as e:
                main_logger.error("Error disconnecting Telegram client: %s", e)

        await cache_manager.close()

        if self._shutdown_event:
            self._shutdown_event.set()

    async def run(self) -> None:
        self.is_running = True
        self._shutdown_event = asyncio.Event()

        main_logger.info("Connecting to Telegram MTProto Gateway...")
        await app.start()

        # Load database from Telegram Channel & start auto-sync
        await cache_manager.load_from_channel(app)
        cache_manager.start_auto_backup_loop(app)

        bot_account = await app.get_me()
        main_logger.info("=" * 60)
        main_logger.info("SUPER GUARDIAN BOT OPERATIONAL (NO REDIS)")
        main_logger.info("Identity : @%s (ID: %s)", bot_account.username, bot_account.id)
        main_logger.info("Commands : %d registered", registry.total_commands)
        main_logger.info("Storage  : In-Memory + Channel Backup Sync")
        main_logger.info("=" * 60)

        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(
                    sig,
                    lambda s=sig: asyncio.create_task(self.shutdown(s.name))
                )
            except NotImplementedError:
                pass

        try:
            await idle()
        finally:
            await self.shutdown("IDLE_EXIT")


def main() -> None:
    uvloop.install()
    bootstrapper = GuardianBootstrapper()
    try:
        asyncio.run(bootstrapper.run())
    except (KeyboardInterrupt, SystemExit):
        main_logger.info("Process stopped.")
    except Exception as fatal_error:
        main_logger.critical("Fatal boot failure: %s", fatal_error, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
    
