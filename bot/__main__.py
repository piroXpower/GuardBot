"""
================================================================================
SUPER GUARDIAN BOT - DISTRIBUTED ASYNC WORKER BOOTSTRAPPER
================================================================================
Module: bot.__main__
Description:
    Worker thread orchestrator. Replaces the default asyncio loop with uvloop,
    binds POSIX signal traps, initializes the Redis cache pool, verifies MTProto
    authentication, and drives non-blocking update ingestion.
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
    """Manages the startup, health checks, and shutdown lifecycle."""
    def __init__(self) -> None:
        self.is_running: bool = False
        self._shutdown_event: Optional[asyncio.Event] = None

    async def shutdown(self, signal_name: str) -> None:
        if not self.is_running:
            return

        main_logger.warning("Received shutdown signal: %s. Cleaning up...", signal_name)
        self.is_running = False

        if app.is_initialized:
            try:
                await app.stop()
                main_logger.info("Telegram MTProto gateway disconnected.")
            except Exception as e:
                main_logger.error("Error disconnecting Telegram client: %s", e)

        try:
            await cache_manager.close()
            main_logger.info("Redis cache pool closed.")
        except Exception as e:
            main_logger.error("Error closing Redis pool: %s", e)

        if self._shutdown_event:
            self._shutdown_event.set()

    async def run(self) -> None:
        self.is_running = True
        self._shutdown_event = asyncio.Event()

        main_logger.info("Initializing distributed Redis cache pool...")
        await cache_manager.initialize()

        main_logger.info("Connecting to Telegram MTProto Gateway...")
        await app.start()

        bot_account = await app.get_me()
        main_logger.info("=" * 60)
        main_logger.info("SUPER GUARDIAN BOT OPERATIONAL")
        main_logger.info("Identity : @%s (ID: %s)", bot_account.username, bot_account.id)
        main_logger.info("Commands : %d registered", registry.total_commands)
        main_logger.info("Version  : %s", __version__)
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
            
