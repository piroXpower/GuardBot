"""
================================================================================
SUPER GUARDIAN BOT - MAIN EXECUTION ENTRYPOINT
================================================================================
Module: bot.__main__
Description:
    Runs the bot under uvloop, coordinates lifecycle startup/shutdown,
    and initializes worker pools.
================================================================================
"""

from __future__ import annotations

import asyncio
import logging
import uvloop
from pyrogram import idle

from bot import app
from bot.core.registry import registry
from bot.database.cache import cache_manager

logger = logging.getLogger("GuardianBot.Main")


async def start_system() -> None:
    """Bootstraps storage connections, loads commands, and connects MTProto client."""
    try:
        logger.info("Connecting distributed Redis caching layer...")
        await cache_manager.initialize()

        logger.info("Starting Telegram MTProto Gateway...")
        await app.start()

        bot_account = await app.get_me()
        logger.info(
            "System operational as @%s (User ID: %s) | Loaded %d dynamic commands.",
            bot_account.username,
            bot_account.id,
            registry.total_commands,
        )

        await idle()

    except asyncio.CancelledError:
        logger.warning("Event loop execution cancelled by system.")
    except Exception as fatal_err:
        logger.critical("Fatal runtime exception: %s", fatal_err, exc_info=True)
    finally:
        logger.info("Shutting down bot workers...")
        if app.is_initialized:
            await app.stop()
        await cache_manager.close()
        logger.info("Process terminated cleanly.")


if __name__ == "__main__":
    uvloop.install()
    try:
        asyncio.run(start_system())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Process manually exited.")
