"""
================================================================================
SUPER GUARDIAN BOT - REDIS CACHE
================================================================================
Module: bot.database.cache
================================================================================
"""

from __future__ import annotations

import logging
from typing import Optional
import redis.asyncio as aioredis
from redis.asyncio.connection import ConnectionPool

from config import REDIS_URL

logger = logging.getLogger("GuardianBot.Cache")


class DistributedCacheManager:
    def __init__(self, connection_url: str) -> None:
        self.url: str = connection_url
        self.pool: Optional[ConnectionPool] = None
        self.client: Optional[aioredis.Redis] = None
        self._is_connected: bool = False

    async def initialize(self) -> None:
        if self._is_connected:
            return
        try:
            self.pool = ConnectionPool.from_url(
                self.url,
                max_connections=250,
                decode_responses=True,
                socket_timeout=5.0,
                socket_connect_timeout=5.0,
            )
            self.client = aioredis.Redis(connection_pool=self.pool)
            await self.client.ping()
            self._is_connected = True
        except Exception as exc:
            logger.critical("Failed to connect to Redis cache: %s", exc)
            self._is_connected = False

    async def close(self) -> None:
        if not self._is_connected or not self.client:
            return
        await self.client.aclose()
        if self.pool:
            await self.pool.disconnect()
        self._is_connected = False

    async def check_flood_rate_limit(self, chat_id: int, user_id: int, limit: int = 5, window: int = 3) -> bool:
        if not self._is_connected or not self.client:
            return False
        key = f"flood:{chat_id}:{user_id}"
        try:
            async with self.client.pipeline(transaction=True) as pipe:
                pipe.incr(key)
                pipe.expire(key, window)
                res = await pipe.execute()
            return res[0] > limit
        except Exception:
            return False

    async def set_user_language(self, user_id: int, lang_code: str) -> bool:
        if not self._is_connected or not self.client:
            return False
        try:
            await self.client.set(f"user_lang:{user_id}", lang_code)
            return True
        except Exception:
            return False

    async def get_user_language(self, user_id: int) -> str:
        if not self._is_connected or not self.client:
            return "en"
        try:
            lang = await self.client.get(f"user_lang:{user_id}")
            return lang if lang else "en"
        except Exception:
            return "en"

    async def get_chat_setting(self, chat_id: int, setting_name: str, default: str = "off") -> str:
        if not self._is_connected or not self.client:
            return default
        try:
            val = await self.client.hget(f"chat_cfg:{chat_id}", setting_name)
            return val if val is not None else default
        except Exception:
            return default

    async def set_chat_setting(self, chat_id: int, setting_name: str, value: str) -> bool:
        if not self._is_connected or not self.client:
            return False
        try:
            await self.client.hset(f"chat_cfg:{chat_id}", setting_name, value)
            return True
        except Exception:
            return False

    async def add_chat_warning(self, chat_id: int, user_id: int) -> int:
        if not self._is_connected or not self.client:
            return 1
        try:
            return await self.client.incr(f"warns:{chat_id}:{user_id}")
        except Exception:
            return 1

    async def reset_chat_warnings(self, chat_id: int, user_id: int) -> bool:
        if not self._is_connected or not self.client:
            return False
        try:
            await self.client.delete(f"warns:{chat_id}:{user_id}")
            return True
        except Exception:
            return False


cache_manager = DistributedCacheManager(REDIS_URL)

async def check_flood_rate_limit(chat_id: int, user_id: int, limit: int = 5, window: int = 3) -> bool:
    return await cache_manager.check_flood_rate_limit(chat_id, user_id, limit, window)

async def set_user_language(user_id: int, lang_code: str) -> bool:
    return await cache_manager.set_user_language(user_id, lang_code)

async def get_user_language(user_id: int) -> str:
    return await cache_manager.get_user_language(user_id)
        
