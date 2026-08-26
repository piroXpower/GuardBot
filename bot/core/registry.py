"""
================================================================================
SUPER GUARDIAN BOT - COMMAND REGISTRY
================================================================================
Module: bot.core.registry
================================================================================
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine, Dict, List, Optional, Set

logger = logging.getLogger("GuardianBot.Registry")


@dataclass
class CommandMetadata:
    name: str
    category: str
    handler: Callable[..., Coroutine[Any, Any, Any]]
    permissions: List[str] = field(default_factory=list)
    description: str = ""
    admin_only: bool = False


class CommandRegistry:
    def __init__(self) -> None:
        self._commands: Dict[str, CommandMetadata] = {}
        self._categories: Dict[str, List[str]] = {}
        self._admin_commands: Set[str] = set()

    def register(
        self,
        command: str,
        category: str = "General",
        permissions: Optional[List[str]] = None,
        description: str = "",
        admin_only: bool = False,
    ) -> Callable[[Callable[..., Coroutine[Any, Any, Any]]], Callable[..., Coroutine[Any, Any, Any]]]:
        def decorator(func: Callable[..., Coroutine[Any, Any, Any]]) -> Callable[..., Coroutine[Any, Any, Any]]:
            clean_cmd = command.lower().strip().lstrip("/")
            meta = CommandMetadata(
                name=clean_cmd,
                category=category,
                handler=func,
                permissions=permissions or [],
                description=description,
                admin_only=admin_only,
            )

            self._commands[clean_cmd] = meta
            if admin_only or permissions:
                self._admin_commands.add(clean_cmd)

            if category not in self._categories:
                self._categories[category] = []
            if clean_cmd not in self._categories[category]:
                self._categories[category].append(clean_cmd)

            return func

        return decorator

    def get_command_metadata(self, command_name: str) -> Optional[CommandMetadata]:
        clean = command_name.lower().strip().lstrip("/")
        return self._commands.get(clean)

    async def dispatch(self, command_name: str, client: Any, update: Any, *args: Any, **kwargs: Any) -> Any:
        clean_cmd = command_name.lower().strip().lstrip("/")
        meta = self.get_command_metadata(clean_cmd)
        if meta:
            return await meta.handler(client, update, *args, **kwargs)
        return None

    @property
    def total_commands(self) -> int:
        return len(self._commands)


registry = CommandRegistry()
