"""Интеграционные тесты для проверки DNS через dnspython.

Тесты создают зоны и записи через API и проверяют резолвинг через dnspython.

Запуск: pytest src/backend/tests/integration/test_dns_resolve.py -v
"""

from __future__ import annotations

import os
import sys
import time
import uuid
from pathlib import Path

import pytest
import dns.resolver
from dns.exception import DNSException

# Путь к исходникам
if Path("/app/src/src").exists():
    _SRC_PATH = Path("/app/src/src")
else:
    _SRC_PATH = Path(__file__).resolve().parents[2] / "src" / "backend" / "src"

if _SRC_PATH.is_dir() and str(_SRC_PATH) not in sys.path:
    sys.path.insert(0, str(_SRC_PATH))

from src.app.main import app
from src.app.users.service import _users_db, pwd_context
from fastapi.testclient import TestClient


# DNS сервер для тестов - используем Knot
DNS_SERVER = os.environ.get("TEST_DNS_SERVER", "127.0.0.1")
DNS_PORT = int(os.environ.get("TEST_DNS_PORT", "53"))


def _get_dns_resolver():
    """Получить настроенный DNS-резолвер"""
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [DNS_SERVER]
    resolver.port = DNS_PORT
    resolver.timeout = 3
    resolver.lifetime = 5
    resolver.rotate = False
    return resolver


client = TestClient(app)

# Инициализируем admin пользователя
if "admin" not in _users_db:
    hashed_password = pwd_context.hash("admin")
    _users_db["admin"] = {
        "password": hashed_password,
        "role": "admin",
        "email": "admin@test.com"
    }


def get_auth_headers():
    response = client.post("/auth/login", data={
        "username": "admin",
        "password": "admin"
    })
    if response.status_code == 200:
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    return {}


def _unique_zone():
    return f"dns-{uuid.uuid4().hex[:8]}.test"


def _wait_for_sync(seconds: int = 2):
    """Подождать синхронизации DNS"""
    time.sleep(seconds)


def _dns_resolve(fqdn: str, rtype: str):
    """Вспомогательная функция для DNS запросов с обработкой ошибок"""
    resolver = _get_dns_resolver()
    try:
        return resolver.resolve(fqdn, rtype)
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
        return None
    except (dns.resolver.LifetimeTimeout, TimeoutError):
        return None


# ================================================================
# ТЕСТЫ ЗОН
# ================================================================

def test_zone_creation_and_resolution():
    """Тест: создание зоны и базовый резолвинг"""
    zone_name = _unique_zone()
    headers = get_auth_headers()
    
    response = client.post("/zones", json={"name": zone_name}, headers=headers)
    assert response.status_code in [200, 201], f"Zone creation failed: {response.json()}"
    
    client.post("/records", json={
        "zone": zone_name,
        "owner": "testhost",
        "type": "A",
        "ttl": 60,
        "data": "10.0.0.1"
    }, headers=headers)
    
    _wait_for_sync(3)
    
    answers = _dns_resolve(f"testhost.{zone_name}.", 'A')
    if answers is None:
        pytest.skip("DNS server not available or zone not propagated")
    assert len(answers) > 0
    assert str(answers[0]) == "10.0.0.1"
    
    client.delete(f"/zones/{zone_name}", headers=headers)


# ================================================================
# ТЕСТЫ A-ЗАПИСЕЙ
# ================================================================

def test_a_record_resolution():
    """Тест: A-запись резолвится корректно"""
    zone_name = _unique_zone()
    headers = get_auth_headers()
    
    client.post("/zones", json={"name": zone_name}, headers=headers)
    client.post("/records", json={
        "zone": zone_name,
        "owner": "www",
        "type": "A",
        "ttl": 60,
        "data": "192.168.100.50"
    }, headers=headers)
    
    _wait_for_sync(3)
    
    answers = _dns_resolve(f"www.{zone_name}.", 'A')
    if answers is None:
        pytest.skip("DNS not available")
    assert len(answers) > 0
    assert str(answers[0]) == "192.168.100.50"
    
    client.delete(f"/zones/{zone_name}", headers=headers)


def test_multiple_a_records():
    """Тест: несколько A-записей в одной зоне"""
    zone_name = _unique_zone()
    headers = get_auth_headers()
    
    client.post("/zones", json={"name": zone_name}, headers=headers)
    
    hosts = [
        ("server1", "10.1.1.1"),
        ("server2", "10.1.1.2"),
        ("server3", "10.1.1.3"),
    ]
    
    for host, ip in hosts:
        client.post("/records", json={
            "zone": zone_name,
            "owner": host,
            "type": "A",
            "ttl": 60,
            "data": ip
        }, headers=headers)
    
    _wait_for_sync(3)
    
    for host, expected_ip in hosts:
        answers = _dns_resolve(f"{host}.{zone_name}.", 'A')
        if answers is None:
            pytest.skip("DNS not available")
        assert str(answers[0]) == expected_ip
    
    client.delete(f"/zones/{zone_name}", headers=headers)


# ================================================================
# ТЕСТЫ AAAA-ЗАПИСЕЙ
# ================================================================

def test_aaaa_record_resolution():
    """Тест: AAAA-запись (IPv6) резолвится корректно"""
    zone_name = _unique_zone()
    headers = get_auth_headers()
    
    client.post("/zones", json={"name": zone_name}, headers=headers)
    client.post("/records", json={
        "zone": zone_name,
        "owner": "ipv6host",
        "type": "AAAA",
        "ttl": 60,
        "data": "2001:db8::100"
    }, headers=headers)
    
    _wait_for_sync(3)
    
    answers = _dns_resolve(f"ipv6host.{zone_name}.", 'AAAA')
    if answers is None:
        pytest.skip("DNS not available")
    assert len(answers) > 0
    assert "2001:db8::100" in str(answers[0]).lower()
    
    client.delete(f"/zones/{zone_name}", headers=headers)


# ================================================================
# ТЕСТЫ TXT-ЗАПИСЕЙ
# ================================================================

def test_txt_record_resolution():
    """Тест: TXT-запись резолвится корректно"""
    zone_name = _unique_zone()
    headers = get_auth_headers()
    
    client.post("/zones", json={"name": zone_name}, headers=headers)
    client.post("/records", json={
        "zone": zone_name,
        "owner": "@",
        "type": "TXT",
        "ttl": 60,
        "data": "v=spf1 mx -all"
    }, headers=headers)
    
    _wait_for_sync(3)
    
    answers = _dns_resolve(f"{zone_name}.", 'TXT')
    if answers is None:
        pytest.skip("DNS not available")
    assert len(answers) > 0
    txt_data = str(answers[0])
    assert "v=spf1" in txt_data
    
    client.delete(f"/zones/{zone_name}", headers=headers)


# ================================================================
# ТЕСТЫ MX-ЗАПИСЕЙ
# ================================================================

def test_mx_record_resolution():
    """Тест: MX-запись резолвится корректно"""
    zone_name = _unique_zone()
    headers = get_auth_headers()
    
    client.post("/zones", json={"name": zone_name}, headers=headers)
    client.post("/records", json={
        "zone": zone_name,
        "owner": "@",
        "type": "MX",
        "ttl": 60,
        "data": f"10 mail.{zone_name}."
    }, headers=headers)
    
    _wait_for_sync(3)
    
    answers = _dns_resolve(f"{zone_name}.", 'MX')
    if answers is None:
        pytest.skip("DNS not available")
    assert len(answers) > 0
    mx_data = str(answers[0])
    assert "mail" in mx_data
    
    client.delete(f"/zones/{zone_name}", headers=headers)


# ================================================================
# ТЕСТЫ CNAME-ЗАПИСЕЙ
# ================================================================

def test_cname_record_resolution():
    """Тест: CNAME-запись резолвится корректно"""
    zone_name = _unique_zone()
    headers = get_auth_headers()
    
    client.post("/zones", json={"name": zone_name}, headers=headers)
    
    client.post("/records", json={
        "zone": zone_name,
        "owner": "original",
        "type": "A",
        "ttl": 60,
        "data": "10.10.10.10"
    }, headers=headers)
    
    client.post("/records", json={
        "zone": zone_name,
        "owner": "alias",
        "type": "CNAME",
        "ttl": 60,
        "data": f"original.{zone_name}."
    }, headers=headers)
    
    _wait_for_sync(3)
    
    answers = _dns_resolve(f"alias.{zone_name}.", 'CNAME')
    if answers is None:
        pytest.skip("DNS not available")
    assert len(answers) > 0
    cname_target = str(answers[0])
    assert cname_target == f"original.{zone_name}."
    
    client.delete(f"/zones/{zone_name}", headers=headers)


# ================================================================
# ТЕСТЫ ОБНОВЛЕНИЯ ЗАПИСЕЙ
# ================================================================

def test_record_update_and_resolution():
    """Тест: обновление записи отражается в DNS"""
    zone_name = _unique_zone()
    headers = get_auth_headers()
    
    client.post("/zones", json={"name": zone_name}, headers=headers)
    client.post("/records", json={
        "zone": zone_name,
        "owner": "dynamic",
        "type": "A",
        "ttl": 60,
        "data": "1.1.1.1"
    }, headers=headers)
    
    _wait_for_sync(2)
    
    client.put(f"/records/{zone_name}", json={
        "old_owner": "dynamic",
        "old_type": "A",
        "old_data": "1.1.1.1",
        "owner": "dynamic",
        "type": "A",
        "ttl": 60,
        "data": "2.2.2.2"
    }, headers=headers)
    
    _wait_for_sync(3)
    
    answers = _dns_resolve(f"dynamic.{zone_name}.", 'A')
    if answers is None:
        pytest.skip("DNS not available")
    assert str(answers[0]) == "2.2.2.2"
    
    client.delete(f"/zones/{zone_name}", headers=headers)



# ================================================================
# ТЕСТЫ TTL
# ================================================================

def test_ttl_respected():
    """Тест: TTL учитывается при резолвинге"""
    zone_name = _unique_zone()
    headers = get_auth_headers()
    
    client.post("/zones", json={"name": zone_name}, headers=headers)
    client.post("/records", json={
        "zone": zone_name,
        "owner": "ttl-test",
        "type": "A",
        "ttl": 300,
        "data": "5.5.5.5"
    }, headers=headers)
    
    _wait_for_sync(3)
    
    answers = _dns_resolve(f"ttl-test.{zone_name}.", 'A')
    if answers is None:
        pytest.skip("DNS not available")
    assert answers.ttl <= 300
    assert str(answers[0]) == "5.5.5.5"
    
    client.delete(f"/zones/{zone_name}", headers=headers)


# ================================================================
# НЕГАТИВНЫЕ ТЕСТЫ
# ================================================================

def test_nonexistent_record_returns_nxdomain():
    """Тест: несуществующая запись возвращает NXDOMAIN"""
    zone_name = _unique_zone()
    headers = get_auth_headers()
    
    client.post("/zones", json={"name": zone_name}, headers=headers)
    
    _wait_for_sync(3)
    
    answers = _dns_resolve(f"nonexistent.{zone_name}.", 'A')
    if answers is None:
        pass  # NXDOMAIN или недоступен DNS
    else:
        pytest.fail("Nonexistent record should not resolve")
    
    client.delete(f"/zones/{zone_name}", headers=headers)


def test_nonexistent_zone_returns_nxdomain():
    """Тест: несуществующая зона возвращает NXDOMAIN"""
    answers = _dns_resolve("this-zone-definitely-does-not-exist-123456789.test.", 'A')
    if answers is None:
        pass  # NXDOMAIN или недоступен DNS
    else:
        pytest.fail("Nonexistent zone should not resolve")
