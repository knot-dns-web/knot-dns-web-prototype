"""Гарантирует импорт `app` и `knot_wrapper` при запуске pytest из корня репозитория или из `/app/src` в контейнере."""

from __future__ import annotations

import sys
from pathlib import Path

_backend_src = Path(__file__).resolve().parents[1] / "src"
if _backend_src.is_dir():
    p = str(_backend_src)
    if p not in sys.path:
        sys.path.insert(0, p)
