"""Гарантирует импорт `app` и `knot_wrapper` при запуске pytest из корня репозитория или из `/app/src` в контейнере."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from beartype import beartype
from beartype.claw import beartype_packages

_REPO_ROOT = Path(__file__).resolve().parents[2]  # .../knot-dns-web-prototype

# Определяем путь к исходникам
# В контейнере: /app/src/src -> knot_wrapper напрямую
# В репозитории: src/backend/src -> knot_wrapper внутри backend
_CONTAINER_SRC = Path("/app/src/src")
_REPO_BACKEND_SRC = _REPO_ROOT / "src" / "backend" / "src"

if _CONTAINER_SRC.exists():
    _BACKEND_SRC = _CONTAINER_SRC
else:
    _BACKEND_SRC = _REPO_BACKEND_SRC

if _BACKEND_SRC.is_dir():
    p = str(_BACKEND_SRC)
    if p not in sys.path:
        sys.path.insert(0, p)

# Имена тестовых зон для очистки перед каждым тестом
_KNOT_TEST_ZONE_NAMES = ("example.com", "todelete.com")


def _cleanup_knot_test_zones() -> None:
    socket_path = os.environ.get("KNOT_SOCKET", "/run/knot/knot.sock")
    if not os.path.exists(socket_path):
        return
    try:
        from libknot.control import KnotCtl
        # Импорт в зависимости от структуры
        try:
            from knot_wrapper.implementation.synchronous import get_knot_config_transaction
        except ImportError:
            from src.knot_wrapper.implementation.synchronous import get_knot_config_transaction
    except Exception:
        return

    for name in _KNOT_TEST_ZONE_NAMES:
        ctl = KnotCtl()
        try:
            ctl.connect(socket_path)
            with get_knot_config_transaction(ctl) as tx:
                tx.unset("zone", name)
                tx.commit()
        except Exception:
            pass
        finally:
            try:
                ctl.close()
            except Exception:
                pass


def pytest_sessionstart(session):
    """Инициализация сессии pytest с beartype"""
    try:
        import knot_wrapper.implementation.synchronous
    except ImportError:
        import src.knot_wrapper.implementation.synchronous
    beartype_packages(['src.app'])


def pytest_pyfunc_call(pyfuncitem):
    """Очистка тестовых зон и применение beartype к каждому тесту"""
    _cleanup_knot_test_zones()
    pyfuncitem.obj = beartype(pyfuncitem.obj)
    return None
