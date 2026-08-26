"""
================================================================================
SUPER GUARDIAN BOT - CORE SUBSYSTEM
================================================================================
Module: bot.core.__init__
================================================================================
"""

from __future__ import annotations

from .client import GuardianClient, client
from .decorators import rate_limit, require_admin, require_owner
from .error_handler import DatabaseTimeoutError, SecurityError, auto_catch, watcher_guard
from .registry import CommandMetadata, CommandRegistry, registry

__all__ = [
    "GuardianClient",
    "client",
    "require_admin",
    "require_owner",
    "rate_limit",
    "auto_catch",
    "watcher_guard",
    "SecurityError",
    "DatabaseTimeoutError",
    "CommandMetadata",
    "CommandRegistry",
    "registry",
]
