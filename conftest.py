from __future__ import annotations

import os
import sys
from pathlib import Path

from beartype import beartype
from beartype.claw import beartype_packages

packages_with_strong_typing = [
    'src.app'
]

_REPO_ROOT = Path(__file__).resolve().parent

# Определяем путь к исходникам
# В контейнере: /app/src/src -> knot_wrapper напрямую
# В репозитории: src/backend/src -> knot_wrapper внутри backend
_CONTAINER_SRC = Path("/app/src/src")
_REPO_BACKEND_SRC = _REPO_ROOT / "src" / "backend" / "src"

if _CONTAINER_SRC.exists():
    _BACKEND_SRC = _CONTAINER_SRC
else:
    _BACKEND_SRC = _REPO_BACKEND_SRC


def _ensure_backend_src_on_path() -> None:
    if _BACKEND_SRC.is_dir():
        p = str(_BACKEND_SRC)
        if p not in sys.path:
            sys.path.insert(0, p)


def pytest_sessionstart(session):
    _ensure_backend_src_on_path()
    beartype_packages(packages_with_strong_typing)


def pytest_pyfunc_call(pyfuncitem):
    pyfuncitem.obj = beartype(pyfuncitem.obj)
    return None
