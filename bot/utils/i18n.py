"""
================================================================================
SUPER GUARDIAN BOT - I18N MODULE
================================================================================
Module: bot.utils.i18n
================================================================================
"""

from __future__ import annotations

import os
import ujson as json
from typing import Any, Dict

_STRINGS: Dict[str, Dict[str, Any]] = {}
LOCALES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "locales")


def load_locales() -> None:
    if not os.path.exists(LOCALES_DIR):
        return
    for filename in os.listdir(LOCALES_DIR):
        if filename.endswith(".json"):
            lang_code = filename[:-5]
            file_path = os.path.join(LOCALES_DIR, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    _STRINGS[lang_code] = json.loads(f.read())
            except Exception:
                pass


def tr(lang: str, key: str, **kwargs: Any) -> str:
    lang = lang if lang in _STRINGS else "en"
    keys = key.split(".")
    data = _STRINGS.get(lang, {})

    for k in keys:
        if isinstance(data, dict):
            data = data.get(k, {})
        else:
            data = None
            break

    if not data or not isinstance(data, str):
        data = _STRINGS.get("en", {})
        for k in keys:
            if isinstance(data, dict):
                data = data.get(k, key)
            else:
                return key

    return data.format(**kwargs) if kwargs else data


load_locales()
