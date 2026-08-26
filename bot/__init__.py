"""
================================================================================
SUPER GUARDIAN BOT - APPLICATION ROOT & TELEMETRY REGISTRY
================================================================================
Package: bot
Description:
    Core initialization module for the Super Guardian Bot enterprise cluster.
    Provides standard ANSI logging formatting, initializes MTProto client instances,
    exposes the central command registry, and mounts distributed caching singletons.
================================================================================
"""

from __future__ import annotations

import logging
import platform
import sys
import time
from typing import Any, Dict, Final, List, Optional, Set, Tuple, Union

from .core.client import GuardianClient, client
from .core.registry import CommandMetadata, CommandRegistry, registry
from .database.cache import DistributedCacheManager, cache_manager

# Configure ANSI logging format
LOG_FORMAT: Final[str] = "%(asctime)s - [%(levelname)s] - [%(name)s:%(lineno)d] - %(message)s"
LOG_DATE_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"


class ColoredConsoleFormatter(logging.Formatter):
    GREY: str = "\x1b[38;20m"
    GREEN: str = "\x1b[32;20m"
    YELLOW: str = "\x1b[33;20m"
    RED: str = "\x1b[31;20m"
    BOLD_RED: str = "\x1b[31;1m"
    RESET: str = "\x1b[0m"

    FORMATS: Dict[int, str] = {
        logging.DEBUG: GREY + LOG_FORMAT + RESET,
        logging.INFO: GREEN + LOG_FORMAT + RESET,
        logging.WARNING: YELLOW + LOG_FORMAT + RESET,
        logging.ERROR: RED + LOG_FORMAT + RESET,
        logging.CRITICAL: BOLD_RED + LOG_FORMAT + RESET,
    }

    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.FORMATS.get(record.levelno, LOG_FORMAT)
        formatter = logging.Formatter(log_fmt, datefmt=LOG_DATE_FORMAT)
        return formatter.format(record)


root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(ColoredConsoleFormatter())
root_logger.addHandler(console_handler)

logger: logging.Logger = logging.getLogger("GuardianBot")
app: GuardianClient = client

__version__: Final[str] = "3.5.0-enterprise"
__author__: Final[str] = "Super Guardian Core Architecture Team"
__status__: Final[str] = "Production Cluster"


class SystemTelemetryMatrix:
    """In-memory telemetry and runtime metric tracking registry."""
    def __init__(self) -> None:
        self.boot_time: float = time.time()
        self.node_id: str = f"node-{platform.node()}"
        self.metric_registry: Dict[str, int] = {
            "updates_routed": 0,
            "commands_executed": 0,
            "security_blocks": 0,
            "rate_limits_hit": 0,
        }

    def record_event(self, node_key: str, amount: int = 1) -> None:
        self.metric_registry[node_key] = self.metric_registry.get(node_key, 0) + amount

    @property
    def uptime(self) -> float:
        return time.time() - self.boot_time


telemetry: SystemTelemetryMatrix = SystemTelemetryMatrix()

__all__: Tuple[str, ...] = (
    "__version__",
    "__author__",
    "__status__",
    "logger",
    "app",
    "client",
    "registry",
    "cache_manager",
    "telemetry",
    "SystemTelemetryMatrix",
    "GuardianClient",
    "CommandRegistry",
    "DistributedCacheManager",
)

logger.info("Core application initialized. Ready for worker boot sequence.")
