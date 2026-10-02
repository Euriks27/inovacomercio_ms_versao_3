# -*- coding: utf-8 -*-
"""Ponto de entrada do backend Flask — funciona de qualquer CWD."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app import app  # noqa: E402
from backend.core.config import settings  # noqa: E402

if __name__ == "__main__":
    app.run(host=settings.APP_HOST, port=settings.APP_PORT, debug=settings.APP_DEBUG)
