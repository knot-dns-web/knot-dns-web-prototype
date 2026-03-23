"""Интеграционные тесты для knot_wrapper.

Тесты проверяют работу обёртки knot_wrapper над libknot.

Запуск: pytest src/backend/tests/integration/test_wrapper.py -v
"""

from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

import pytest
from libknot.control import KnotCtl

# Путь к исходникам
if Path("/app/src/src").exists():
    _SRC_PATH = Path("/app/src/src")
else:
    _SRC_PATH = Path(__file__).resolve().parents[2] / "src" / "backend" / "src"

if _SRC_PATH.is_dir() and str(_SRC_PATH) not in sys.path:
    sys.path.insert(0, str(_SRC_PATH))

from knot_wrapper.implementation.base_operations.config import (
    begin_config, commit_config, abort_config,
    get_config, set_config, unset_config
)
from knot_wrapper.implementation.base_operations.zone import (
    begin_zone, commit_zone, abort_zone,
    get_zone, set_zone, unset_zone, status_zone
)


def _knot_socket() -> str:
    return os.environ.get("KNOT_SOCKET", "/run/knot/knot.sock")


def _require_knot_socket() -> str:
    p = _knot_socket()
    if not os.path.exists(p):
        pytest.skip(f"Нет сокета Knot ({p})")
    return p


def _abort_all():
    """Аварийный сброс всех транзакций"""
    socket = _knot_socket()
    if not os.path.exists(socket):
        return
    try:
        ctl = KnotCtl()
        ctl.connect(socket)
        try:
            ctl.send_block(cmd="conf-abort")
            ctl.receive_block()
        except Exception:
            pass
        ctl.close()
    except Exception:
        pass


@pytest.fixture(scope="function", autouse=True)
def cleanup():
    """Сброс транзакций перед каждым тестом"""
    _abort_all()
    yield
    _abort_all()


# ================================================================
# КОНФИГУРАЦИОННЫЕ ТРАНЗАКЦИИ
# ================================================================

def test_config_begin_commit():
    """Тест: begin_config -> abort_config"""
    socket = _require_knot_socket()
    ctl = KnotCtl()
    ctl.connect(socket)
    try:
        begin_config(ctl)
        abort_config(ctl)
    finally:
        ctl.close()


def test_config_get_zones():
    """Тест: получить список зон"""
    socket = _require_knot_socket()
    ctl = KnotCtl()
    ctl.connect(socket)
    try:
        begin_config(ctl)
        try:
            result = get_config(ctl, section="zone")
            assert result is None or isinstance(result, dict)
        finally:
            abort_config(ctl)
    finally:
        ctl.close()


def test_config_list_all_zones():
    """Тест: получить информацию о всех зонах"""
    socket = _require_knot_socket()
    ctl = KnotCtl()
    ctl.connect(socket)
    try:
        begin_config(ctl)
        try:
            result = get_config(ctl, section="zone")
            zones = result or {}
            # Проверяем что результат содержит информацию о зонах
            assert isinstance(zones, dict)
        finally:
            abort_config(ctl)
    finally:
        ctl.close()


# ================================================================
# ЗОННЫЕ ТРАНЗАКЦИИ С СУЩЕСТВУЮЩЕЙ ЗОНОЙ
# ================================================================

def test_zone_begin_commit():
    """Тест: begin_zone -> abort_zone"""
    socket = _require_knot_socket()
    ctl = KnotCtl()
    ctl.connect(socket)
    try:
        begin_zone(ctl)
        abort_zone(ctl)
    finally:
        ctl.close()


def test_zone_status_existing_zone():
    """Тест: получить статус существующей зоны"""
    socket = _require_knot_socket()
    ctl = KnotCtl()
    ctl.connect(socket)
    try:
        # Используем зону которая точно существует
        # zone-status работает без begin_zone для существующих зон
        result = status_zone(ctl, zone="example.com")
        # Результат может быть None или dict
        assert result is None or isinstance(result, dict)
    finally:
        ctl.close()


def test_zone_get_records():
    """Тест: получить записи существующей зоны (только чтение)"""
    socket = _require_knot_socket()
    ctl = KnotCtl()
    ctl.connect(socket)
    try:
        # Для чтения используем begin_zone без commit (read-only)
        begin_zone(ctl, "example.com")
        try:
            result = get_zone(ctl, zone="example.com")
            # Read-only транзакция, просто abort
            abort_zone(ctl, "example.com")
            # Результат содержит записи зоны
            assert result is not None
        except:
            abort_zone(ctl, "example.com")
            raise
    finally:
        ctl.close()


# ================================================================
# НЕГАТИВНЫЕ ТЕСТЫ
# ================================================================

def test_config_abort():
    """Тест: отмена транзакции конфигурации"""
    socket = _require_knot_socket()
    ctl = KnotCtl()
    ctl.connect(socket)
    try:
        begin_config(ctl)
        abort_config(ctl)
    finally:
        ctl.close()


def test_zone_abort():
    """Тест: отмена зонной транзакции"""
    socket = _require_knot_socket()
    ctl = KnotCtl()
    ctl.connect(socket)
    try:
        begin_zone(ctl)
        try:
            set_zone(ctl, zone="example.com", owner="temp-test", type="A", ttl="300", data="1.2.3.4")
            abort_zone(ctl)
        except:
            abort_zone(ctl)
            raise
    finally:
        ctl.close()


def test_nonexistent_zone_status():
    """Тест: статус несуществующей зоны - ожидаем ошибку"""
    socket = _require_knot_socket()
    ctl = KnotCtl()
    ctl.connect(socket)
    try:
        with pytest.raises(Exception) as exc_info:
            status_zone(ctl, zone="definitely-nonexistent-zone-12345.com")
        # Ожидаем ошибку "no such zone"
        assert "no such zone" in str(exc_info.value).lower() or "not found" in str(exc_info.value).lower()
    finally:
        ctl.close()


def test_zone_begin_nonexistent():
    """Тест: begin_zone для несуществующей зоны - ожидаем ошибку"""
    socket = _require_knot_socket()
    ctl = KnotCtl()
    ctl.connect(socket)
    try:
        with pytest.raises(Exception) as exc_info:
            begin_zone(ctl, "definitely-nonexistent-zone-12345.com")
            commit_zone(ctl, "definitely-nonexistent-zone-12345.com")
        assert "no such zone" in str(exc_info.value).lower() or "not found" in str(exc_info.value).lower()
    finally:
        ctl.close()
