"""
================================================================================
SUPER GUARDIAN BOT - APPLICATION ROOT INITIALIZER
================================================================================
Module: bot.__init__
Description:
    Core application package initialization. Instantiates client singletons
    and configures standard stream logging pipelines.
================================================================================
"""

from __future__ import annotations

import logging
import sys

from .core.client import GuardianClient, client
from .core.registry import registry

# Stream Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - [%(name)s] - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("GuardianBot")
app = client

__all__ = ["app", "registry", "logger", "GuardianClient"]
