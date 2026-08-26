"""
================================================================================
SUPER GUARDIAN BOT - TIME PARSER
================================================================================
Module: bot.utils.time_parser
================================================================================
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Optional

TIME_PATTERN = re.compile(r"^(\d+)([smhdwy])$", re.IGNORECASE)
UNIT_MULTIPLIERS = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800, "y": 31536000}


def time_to_seconds(duration_str: str) -> Optional[int]:
    if not duration_str:
        return None
    match = TIME_PATTERN.match(duration_str.strip().lower())
    if not match:
        return None
    value, unit = int(match.group(1)), match.group(2)
    return value * UNIT_MULTIPLIERS.get(unit, 0)


def parse_time(duration_str: str) -> Optional[datetime]:
    seconds = time_to_seconds(duration_str)
    if not seconds:
        return None
    return datetime.utcnow() + timedelta(seconds=seconds)


def format_duration(seconds: int) -> str:
    if seconds <= 0:
        return "0s"
    parts = []
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, secs = divmod(rem, 60)
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")
    return " ".join(parts)
