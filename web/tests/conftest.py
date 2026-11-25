"""Pytest path setup: web/ er root for `app`-pakken."""

from __future__ import annotations

import sys
from pathlib import Path

WEB_ROOT = Path(__file__).resolve().parents[1]
if str(WEB_ROOT) not in sys.path:
    sys.path.insert(0, str(WEB_ROOT))
