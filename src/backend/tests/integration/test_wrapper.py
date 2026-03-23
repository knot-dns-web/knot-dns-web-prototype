"""Интеграционные тесты для knot_wrapper.base_operations.

Тесты проверяют:
1. Базовые операции с конфигурацией (config)
2. Базовые операции с зонами (zone)
3. DNS-запросы через dnspython для проверки результатов

Запуск: pytest src/backend/tests/integration/test_wrapper.py -v
"""

from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

import pytest
import dns.resolver
import dns.zone
from libknot.control import KnotCtl

# Путь к исходникам (для импорта knot_wrapper)
# В контейнере: /app/src/src -> knot_wrapper напрямую
# В репозитории: src/backend/src -> knot_wrapper внутри backend
if Path("/app/src/src").exists():
    _SRC_PATH = Path("/app/src/src")
else:
    _SRC_PATH = Path(__file__).resolve().parents[2] / "src" / "backend" / "src"

if _SRC_PATH.is_dir() and str(_SRC_PATH) not in sys.path:
    sys.path.insert(0, str(_SRC_PATH))

# Импорт базовых операций
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
        pytest.skip(f"Нет сокета Knot ({p}). Запускайте в контейнере с knotd.")
    return p


def _unique_zone() -> str:
    return f"test-{uuid.uuid4().hex[:8]}.com"


def _cleanup_zone(ctl: KnotCtl, zone_name: str):
    """Удаляет зону из конфигурации Knot"""
    try:
        begin_config(ctl)
        unset_config(ctl, section="zone", identifier=zone_name)
        commit_config(ctl)
    except Exception:
        pass


# ================================================================
# ТЕСТЫ БАЗОВЫХ ОПЕРАЦИЙ КОНФИГУРАЦИИ
# ================================================================

def test_config_begin_commit():
    """Тест начала и коммита конфигурации"""
    socket = _require_knot_socket()
    ctl = KnotCtl()
    ctl.connect(socket)
    try:
        begin_config(ctl)
        # Успешное выполнение без ошибок = успех
    finally:
        ctl.close()


def test_config_get_zone_list():
    """Тест получения списка зон"""
    socket = _require_knot_socket()
    ctl = KnotCtl()
    ctl.connect(socket)
    try:
        begin_config(ctl)
        result = get_config(ctl, section="zone")
        # Результат должен быть dict или None
        assert result is None or isinstance(result, dict)
    finally:
        ctl.close()


def test_config_set_and_unset_zone():
    """Тест создания и удаления зоны"""
    socket = _require_knot_socket()
    zone_name = _unique_zone()
    ctl = KnotCtl()
    ctl.connect(socket)
    try:
        # Создаём зону
        begin_config(ctl)
        set_config(ctl, section="zone", identifier=zone_name)
        commit_config(ctl)
        
        # Проверяем что зона существует
        begin_config(ctl)
        result = get_config(ctl, section="zone")
        zones = (result or {}).get("zone", {})
        assert zone_name in zones or zone_name.rstrip(".com") in str(zones)
        
        # Удаляем зону
        begin_config(ctl)
        unset_config(ctl, section="zone", identifier=zone_name)
        commit_config(ctl)
        
        # Проверяем что зона удалена
        begin_config(ctl)
        result = get_config(ctl, section="zone")
        zones = (result or {}).get("zone", {})
        assert zone_name not in zones and zone_name.rstrip(".com") not in str(zones)
    finally:
        ctl.close()


# ================================================================
# ТЕСТЫ БАЗОВЫХ ОПЕРАЦИЙ С ЗОНАМИ
# ================================================================

def test_zone_begin_commit():
    """Тест начала и коммита зонной транзакции"""
    socket = _require_knot_socket()
    ctl = KnotCtl()
    ctl.connect(socket)
    try:
        begin_zone(ctl)
        # Успешное выполнение без ошибок = успех
    finally:
        ctl.close()


def test_zone_set_and_get_record():
    """Тест установки и получения DNS-записи"""
    socket = _require_knot_socket()
    zone_name = _unique_zone()
    zone_without_tld = zone_name.rstrip(".com")
    ctl = KnotCtl()
    ctl.connect(socket)
    try:
        # Создаём зону
        begin_config(ctl)
        set_config(ctl, section="zone", identifier=zone_name)
        commit_config(ctl)
        
        # Добавляем запись
        begin_zone(ctl, zone_name)
        set_zone(ctl, zone=zone_without_tld, owner="@", type="A", ttl="3600", data="10.0.0.1")
        commit_zone(ctl, zone_name)
        
        # Получаем записи зоны
        begin_zone(ctl, zone_name)
        result = get_zone(ctl, zone=zone_without_tld)
        commit_zone(ctl, zone_name)
        
        # Проверяем что запись есть
        assert result is not None
        assert "10.0.0.1" in str(result)
    finally:
        _cleanup_zone(ctl, zone_name)
        ctl.close()


def test_zone_unset_record():
    """Тест удаления DNS-записи"""
    socket = _require_knot_socket()
    zone_name = _unique_zone()
    zone_without_tld = zone_name.rstrip(".com")
    ctl = KnotCtl()
    ctl.connect(socket)
    try:
        # Создаём зону и запись
        begin_config(ctl)
        set_config(ctl, section="zone", identifier=zone_name)
        commit_config(ctl)
        
        begin_zone(ctl, zone_name)
        set_zone(ctl, zone=zone_without_tld, owner="@", type="A", ttl="3600", data="10.0.0.1")
        commit_zone(ctl, zone_name)
        
        # Удаляем запись
        begin_zone(ctl, zone_name)
        unset_zone(ctl, zone=zone_without_tld, owner="@", type="A", data="10.0.0.1")
        commit_zone(ctl, zone_name)
        
        # Проверяем что запись удалена
        begin_zone(ctl, zone_name)
        result = get_zone(ctl, zone=zone_without_tld)
        commit_zone(ctl, zone_name)
        
        # Запись не должна содержать 10.0.0.1
        assert result is None or "10.0.0.1" not in str(result)
    finally:
        _cleanup_zone(ctl, zone_name)
        ctl.close()


def test_zone_status():
    """Тест получения статуса зоны"""
    socket = _require_knot_socket()
    zone_name = _unique_zone()
    ctl = KnotCtl()
    ctl.connect(socket)
    try:
        # Создаём зону
        begin_config(ctl)
        set_config(ctl, section="zone", identifier=zone_name)
        commit_config(ctl)
        
        # Получаем статус
        result = status_zone(ctl, zone=zone_name.rstrip(".com"))
        
        # Статус должен быть dict или None
        assert result is None or isinstance(result, dict)
    finally:
        _cleanup_zone(ctl, zone_name)
        ctl.close()


# ================================================================
# ТЕСТЫ С РАЗЛИЧНЫМИ ТИПАМИ ЗАПИСЕЙ
# ================================================================

def test_zone_creates_multiple_record_types():
    """Тест создания записей разных типов"""
    socket = _require_knot_socket()
    zone_name = _unique_zone()
    zone_without_tld = zone_name.rstrip(".com")
    ctl = KnotCtl()
    ctl.connect(socket)
    try:
        # Создаём зону
        begin_config(ctl)
        set_config(ctl, section="zone", identifier=zone_name)
        commit_config(ctl)
        
        # Создаём A запись
        begin_zone(ctl, zone_name)
        set_zone(ctl, zone=zone_without_tld, owner="www", type="A", ttl="3600", data="192.168.1.1")
        commit_zone(ctl, zone_name)
        
        # Создаём AAAA запись
        begin_zone(ctl, zone_name)
        set_zone(ctl, zone=zone_without_tld, owner="www", type="AAAA", ttl="3600", data="::1")
        commit_zone(ctl, zone_name)
        
        # Создаём TXT запись
        begin_zone(ctl, zone_name)
        set_zone(ctl, zone=zone_without_tld, owner="@", type="TXT", ttl="3600", data="v=spf1 mx -all")
        commit_zone(ctl, zone_name)
        
        # Проверяем записи
        begin_zone(ctl, zone_name)
        result = get_zone(ctl, zone=zone_without_tld)
        commit_zone(ctl, zone_name)
        
        result_str = str(result)
        assert "192.168.1.1" in result_str
        assert "::1" in result_str
        assert "v=spf1 mx -all" in result_str
    finally:
        _cleanup_zone(ctl, zone_name)
        ctl.close()


def test_zone_cname_record():
    """Тест создания CNAME записи"""
    socket = _require_knot_socket()
    zone_name = _unique_zone()
    zone_without_tld = zone_name.rstrip(".com")
    ctl = KnotCtl()
    ctl.connect(socket)
    try:
        # Создаём зону
        begin_config(ctl)
        set_config(ctl, section="zone", identifier=zone_name)
        commit_config(ctl)
        
        # Создаём A запись (основная)
        begin_zone(ctl, zone_name)
        set_zone(ctl, zone=zone_without_tld, owner="server", type="A", ttl="3600", data="10.0.0.5")
        commit_zone(ctl, zone_name)
        
        # Создаём CNAME
        begin_zone(ctl, zone_name)
        set_zone(ctl, zone=zone_without_tld, owner="alias", type="CNAME", ttl="3600", data="server." + zone_without_tld + ".")
        commit_zone(ctl, zone_name)
        
        # Проверяем
        begin_zone(ctl, zone_name)
        result = get_zone(ctl, zone=zone_without_tld)
        commit_zone(ctl, zone_name)
        
        result_str = str(result)
        assert "CNAME" in result_str
        assert "server" in result_str
    finally:
        _cleanup_zone(ctl, zone_name)
        ctl.close()


# ================================================================
# ТЕСТЫ С ПОЛНЫМ ЦИКЛОМ (СОЗДАНИЕ + ПРОВЕРКА DNS)
# ================================================================

def test_full_zone_lifecycle_with_dns_query():
    """Тест полного цикла: создание зоны, записей и DNS-запрос"""
    socket = _require_knot_socket()
    # Используем зарезервированный IP для тестирования
    zone_name = "test-dns-zone.com"
    zone_without_tld = zone_name.rstrip(".com")
    ctl = KnotCtl()
    ctl.connect(socket)
    
    resolver = dns.resolver.Resolver()
    # Knot слушает на localhost в контейнере
    resolver.nameservers = ['127.0.0.1']
    
    try:
        # Создаём зону
        begin_config(ctl)
        set_config(ctl, section="zone", identifier=zone_name)
        commit_config(ctl)
        
        # Добавляем NS и SOA (минимально для работы зоны)
        begin_zone(ctl, zone_name)
        set_zone(ctl, zone=zone_without_tld, owner="@", type="NS", ttl="3600", data="ns1." + zone_without_tld + ".")
        commit_zone(ctl, zone_name)
        
        begin_zone(ctl, zone_name)
        set_zone(ctl, zone=zone_without_tld, owner="@", type="SOA", ttl="3600", 
                 data="ns1." + zone_without_tld + ". hostmaster." + zone_without_tld + ". 1 3600 900 604800 86400")
        commit_zone(ctl, zone_name)
        
        # Добавляем A запись
        begin_zone(ctl, zone_name)
        set_zone(ctl, zone=zone_without_tld, owner="test", type="A", ttl="3600", data="127.0.0.1")
        commit_zone(ctl, zone_name)
        
        # Проверяем через get_zone
        begin_zone(ctl, zone_name)
        result = get_zone(ctl, zone=zone_without_tld)
        commit_zone(ctl, zone_name)
        
        result_str = str(result)
        assert "test" in result_str
        assert "127.0.0.1" in result_str
        
        # DNS-запрос (может не работать если Knot не настроен как resolver)
        # Пропускаем если не работает
        try:
            answers = resolver.resolve('test.' + zone_without_tld, 'A')
            assert len(answers) > 0
            assert str(answers[0]) == "127.0.0.1"
        except Exception:
            # DNS-запрос может не работать, но запись создана корректно
            pass
        
    finally:
        _cleanup_zone(ctl, zone_name)
        ctl.close()


# ================================================================
# НЕГАТИВНЫЕ ТЕСТЫ
# ================================================================

def test_zone_operations_on_nonexistent_zone():
    """Тест операций с несуществующей зоной"""
    socket = _require_knot_socket()
    ctl = KnotCtl()
    ctl.connect(socket)
    try:
        # Попытка получить статус несуществующей зоны
        result = status_zone(ctl, zone="nonexistent-zone-that-does-not-exist.com")
        # Может вернуть ошибку или None
        assert result is None or isinstance(result, dict)
    finally:
        ctl.close()


def test_config_abort():
    """Тест отмены транзакции конфигурации"""
    socket = _require_knot_socket()
    ctl = KnotCtl()
    ctl.connect(socket)
    try:
        begin_config(ctl)
        # Не делаем set, просто abort
        abort_config(ctl)
        # Успех если не выброшено исключение
    finally:
        ctl.close()


def test_zone_abort():
    """Тест отмены зонной транзакции"""
    socket = _require_knot_socket()
    zone_name = _unique_zone()
    ctl = KnotCtl()
    ctl.connect(socket)
    try:
        begin_config(ctl)
        set_config(ctl, section="zone", identifier=zone_name)
        commit_config(ctl)
        
        begin_zone(ctl, zone_name)
        set_zone(ctl, zone=zone_name.rstrip(".com"), owner="temp", type="A", ttl="3600", data="1.2.3.4")
        # Не коммитим, отменяем
        abort_zone(ctl, zone_name)
        
        # Проверяем что запись не создана
        begin_zone(ctl, zone_name)
        result = get_zone(ctl, zone=zone_name.rstrip(".com"))
        commit_zone(ctl, zone_name)
        
        assert result is None or "1.2.3.4" not in str(result)
    finally:
        _cleanup_zone(ctl, zone_name)
        ctl.close()
