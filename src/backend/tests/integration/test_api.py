import os
import sys
from pathlib import Path

# Определяем путь к исходникам
_CONTAINER_SRC = Path("/app/src/src")
_REPO_BACKEND_SRC = Path(__file__).resolve().parents[2] / "src" / "backend" / "src"

if _CONTAINER_SRC.exists():
    _BACKEND_SRC = _CONTAINER_SRC
else:
    _BACKEND_SRC = _REPO_BACKEND_SRC

if _BACKEND_SRC.is_dir() and str(_BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(_BACKEND_SRC))

# Импорт app
try:
    from src.app.main import app
    from src.app.users.service import UserService, _users_db, pwd_context
except ImportError:
    from ...src.app.main import app
    from ...src.app.users.service import UserService, _users_db, pwd_context

from fastapi.testclient import TestClient
import pytest
import uuid

# Создаем тестовый клиент
client = TestClient(app)

# Инициализируем admin пользователя
def setup_test_user():
    if "admin" not in _users_db:
        hashed_password = pwd_context.hash("admin")
        _users_db["admin"] = {
            "password": hashed_password,
            "role": "admin",
            "email": "admin@test.com"
        }

setup_test_user()

# Функция для получения headers
def get_auth_headers():
    response = client.post("/auth/login", data={
        "username": "admin",
        "password": "admin"
    })
    if response.status_code == 200:
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    return {}

HEADERS = get_auth_headers()


# ================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ================================================================

def cleanup_zone(zone_name: str):
    """Удаляет зону после теста"""
    client.delete(f"/zones/{zone_name}", headers=HEADERS)


# ================================================================
# ТЕСТЫ АУТЕНТИФИКАЦИИ (не зависят от зон)
# ================================================================

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "Knot DNS API running"


def test_login_success():
    """Тест успешной аутентификации"""
    response = client.post("/auth/login", data={
        "username": "admin",
        "password": "admin"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_invalid_credentials():
    """Тест аутентификации с неверными данными"""
    response = client.post("/auth/login", data={
        "username": "admin",
        "password": "wrong_password"
    })
    assert response.status_code == 401


def test_login_nonexistent_user():
    """Тест аутентификации с несуществующим пользователем"""
    response = client.post("/auth/login", data={
        "username": "nonexistent_user",
        "password": "password"
    })
    assert response.status_code == 401


# ================================================================
# ТЕСТЫ ЗОН (каждый тест создаёт и удаляет свою зону)
# ================================================================

def test_create_zone():
    """Тест создания зоны"""
    zone_name = f"create-test-{uuid.uuid4().hex[:8]}.com"
    response = client.post("/zones", json={"name": zone_name}, headers=HEADERS)
    try:
        assert response.status_code in [200, 201]
    finally:
        cleanup_zone(zone_name)


def test_get_zones():
    """Тест получения списка зон"""
    response = client.get("/zones", headers=HEADERS)
    assert response.status_code == 200
    assert "zones" in response.json()


def test_delete_zone():
    """Тест удаления зоны"""
    zone_name = f"delete-test-{uuid.uuid4().hex[:8]}.com"
    client.post("/zones", json={"name": zone_name}, headers=HEADERS)
    response = client.delete(f"/zones/{zone_name}", headers=HEADERS)
    assert response.status_code == 200


def test_export_zone():
    """Тест экспорта зоны"""
    zone_name = f"export-test-{uuid.uuid4().hex[:8]}.com"
    client.post("/zones", json={"name": zone_name}, headers=HEADERS)
    client.post("/records", json={
        "zone": zone_name,
        "owner": "@",
        "type": "A",
        "ttl": 3600,
        "data": "192.168.1.1"
    }, headers=HEADERS)
    try:
        response = client.get(f"/zones/{zone_name}/export", headers=HEADERS)
        assert response.status_code == 200
        assert response.text
    finally:
        cleanup_zone(zone_name)


def test_import_zone():
    """Тест импорта зоны"""
    zone_name = f"import-test-{uuid.uuid4().hex[:8]}.com"
    zone_content = f"""$ORIGIN {zone_name}.
$TTL 3600
@  IN  SOA ns1.example.com. admin.example.com. 2023010101 3600 900 604800 86400
@  IN  NS  ns1.example.com.
ns1 IN  A   192.168.1.1
@  IN  A   192.168.1.2
"""
    response = client.post("/zones/import", json={
        "name": zone_name,
        "content": zone_content
    }, headers=HEADERS)
    try:
        assert response.status_code in [200, 201]
    finally:
        cleanup_zone(zone_name)


def test_create_zone_duplicate():
    """Тест создания дубликата зоны"""
    zone_name = f"dup-test-{uuid.uuid4().hex[:8]}.com"
    client.post("/zones", json={"name": zone_name}, headers=HEADERS)
    try:
        response = client.post("/zones", json={"name": zone_name}, headers=HEADERS)
        assert response.status_code == 400
    finally:
        cleanup_zone(zone_name)


def test_delete_nonexistent_zone():
    """Тест удаления несуществующей зоны"""
    response = client.delete("/zones/nonexistent12345.com", headers=HEADERS)
    assert response.status_code in [200, 404]


# ================================================================
# ТЕСТЫ ЗАПИСЕЙ (каждый тест создаёт свою зону и запись)
# ================================================================

def test_create_record():
    """Тест создания DNS записи"""
    zone_name = f"rec-create-{uuid.uuid4().hex[:8]}.com"
    client.post("/zones", json={"name": zone_name}, headers=HEADERS)
    try:
        response = client.post("/records", json={
            "zone": zone_name,
            "owner": "test-owner",
            "type": "A",
            "ttl": 3600,
            "data": "192.168.1.1"
        }, headers=HEADERS)
        assert response.status_code in [200, 201]
    finally:
        cleanup_zone(zone_name)


def test_get_records():
    """Тест получения записей"""
    zone_name = f"rec-get-{uuid.uuid4().hex[:8]}.com"
    client.post("/zones", json={"name": zone_name}, headers=HEADERS)
    client.post("/records", json={
        "zone": zone_name,
        "owner": "test",
        "type": "A",
        "ttl": 3600,
        "data": "192.168.1.1"
    }, headers=HEADERS)
    try:
        response = client.get("/records", headers=HEADERS)
        assert response.status_code == 200
        assert "records" in response.json()
    finally:
        cleanup_zone(zone_name)


def test_delete_record():
    """Тест удаления DNS записи"""
    zone_name = f"rec-del-{uuid.uuid4().hex[:8]}.com"
    client.post("/zones", json={"name": zone_name}, headers=HEADERS)
    client.post("/records", json={
        "zone": zone_name,
        "owner": "to-delete",
        "type": "A",
        "ttl": 3600,
        "data": "192.168.1.1"
    }, headers=HEADERS)
    try:
        response = client.delete(f"/records/{zone_name}/to-delete/A/192.168.1.1", headers=HEADERS)
        assert response.status_code == 200
    finally:
        cleanup_zone(zone_name)


def test_update_record():
    """Тест обновления DNS записи"""
    zone_name = f"rec-upd-{uuid.uuid4().hex[:8]}.com"
    client.post("/zones", json={"name": zone_name}, headers=HEADERS)
    client.post("/records", json={
        "zone": zone_name,
        "owner": "update-owner",
        "type": "A",
        "ttl": 3600,
        "data": "192.168.1.1"
    }, headers=HEADERS)
    try:
        response = client.put(f"/records/{zone_name}", json={
            "old_owner": "update-owner",
            "old_type": "A",
            "old_data": "192.168.1.1",
            "owner": "update-owner",
            "type": "A",
            "ttl": 7200,
            "data": "192.168.1.2"
        }, headers=HEADERS)
        assert response.status_code == 200
    finally:
        cleanup_zone(zone_name)


def test_create_aaaa_record():
    """Тест создания AAAA записи"""
    zone_name = f"aaaa-test-{uuid.uuid4().hex[:8]}.com"
    client.post("/zones", json={"name": zone_name}, headers=HEADERS)
    try:
        response = client.post("/records", json={
            "zone": zone_name,
            "owner": "test_aaaa",
            "type": "AAAA",
            "ttl": 3600,
            "data": "::1"
        }, headers=HEADERS)
        assert response.status_code in [200, 201]
    finally:
        cleanup_zone(zone_name)


def test_create_cname_record():
    """Тест создания CNAME записи"""
    zone_name = f"cname-test-{uuid.uuid4().hex[:8]}.com"
    client.post("/zones", json={"name": zone_name}, headers=HEADERS)
    try:
        response = client.post("/records", json={
            "zone": zone_name,
            "owner": "test_cname",
            "type": "CNAME",
            "ttl": 3600,
            "data": f"test.{zone_name}"
        }, headers=HEADERS)
        assert response.status_code in [200, 201]
    finally:
        cleanup_zone(zone_name)


def test_create_txt_record():
    """Тест создания TXT записи"""
    zone_name = f"txt-test-{uuid.uuid4().hex[:8]}.com"
    client.post("/zones", json={"name": zone_name}, headers=HEADERS)
    try:
        response = client.post("/records", json={
            "zone": zone_name,
            "owner": "test_txt",
            "type": "TXT",
            "ttl": 3600,
            "data": "v=spf1 mx -all"
        }, headers=HEADERS)
        assert response.status_code in [200, 201]
    finally:
        cleanup_zone(zone_name)


def test_create_mx_record():
    """Тест создания MX записи"""
    zone_name = f"mx-test-{uuid.uuid4().hex[:8]}.com"
    client.post("/zones", json={"name": zone_name}, headers=HEADERS)
    try:
        response = client.post("/records", json={
            "zone": zone_name,
            "owner": "@",
            "type": "MX",
            "ttl": 3600,
            "data": f"10 mail.{zone_name}"
        }, headers=HEADERS)
        assert response.status_code in [200, 201]
    finally:
        cleanup_zone(zone_name)


def test_create_ns_record():
    """Тест создания NS записи"""
    zone_name = f"ns-test-{uuid.uuid4().hex[:8]}.com"
    client.post("/zones", json={"name": zone_name}, headers=HEADERS)
    try:
        response = client.post("/records", json={
            "zone": zone_name,
            "owner": "@",
            "type": "NS",
            "ttl": 3600,
            "data": f"ns1.{zone_name}"
        }, headers=HEADERS)
        assert response.status_code in [200, 201]
    finally:
        cleanup_zone(zone_name)


def test_delete_nonexistent_record():
    """Тест удаления несуществующей записи"""
    response = client.delete("/records/nonexistent.com/nonexistent/A", headers=HEADERS)
    assert response.status_code == 404


def test_create_record_nonexistent_zone():
    """Тест создания записи в несуществующей зоне"""
    response = client.post("/records", json={
        "zone": "nonexistent_zone_12345.com",
        "owner": "test",
        "type": "A",
        "ttl": 3600,
        "data": "192.168.1.1"
    }, headers=HEADERS)
    assert response.status_code == 400


def test_update_nonexistent_record():
    """Тест обновления несуществующей записи"""
    zone_name = f"nonex-{uuid.uuid4().hex[:8]}.com"
    response = client.put(f"/records/{zone_name}", json={
        "old_owner": "nonexistent",
        "old_type": "A",
        "old_data": "192.168.1.1",
        "owner": "nonexistent",
        "type": "A",
        "ttl": 3600,
        "data": "192.168.1.2"
    }, headers=HEADERS)
    assert response.status_code == 400


# ================================================================
# ТЕСТЫ ПОЛЬЗОВАТЕЛЕЙ
# ================================================================

def test_create_user():
    """Тест создания пользователя"""
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    response = client.post("/users", json={
        "username": username,
        "password": "password",
        "role": "user",
        "email": f"{username}@example.com"
    }, headers=HEADERS)
    try:
        assert response.status_code in [200, 201]
    finally:
        client.delete(f"/users/{username}", headers=HEADERS)


def test_get_users():
    """Тест получения списка пользователей"""
    response = client.get("/users", headers=HEADERS)
    assert response.status_code == 200


def test_delete_user():
    """Тест удаления пользователя"""
    username = f"deluser_{uuid.uuid4().hex[:8]}"
    client.post("/users", json={
        "username": username,
        "password": "password",
        "role": "user",
        "email": f"{username}@example.com"
    }, headers=HEADERS)
    response = client.delete(f"/users/{username}", headers=HEADERS)
    assert response.status_code == 200


def test_update_user():
    """Тест обновления пользователя"""
    username = f"upduser_{uuid.uuid4().hex[:8]}"
    client.post("/users", json={
        "username": username,
        "password": "old_password",
        "role": "user",
        "email": f"{username}@example.com"
    }, headers=HEADERS)
    try:
        response = client.put(f"/users/{username}", json={
            "password": "new_password",
            "role": "admin",
            "email": f"new_{username}@example.com"
        }, headers=HEADERS)
        assert response.status_code == 200
        assert response.json()["username"] == username
        assert response.json()["role"] == "admin"
    finally:
        client.delete(f"/users/{username}", headers=HEADERS)


def test_delete_nonexistent_user():
    """Тест удаления несуществующего пользователя"""
    response = client.delete("/users/nonexistent_user_12345", headers=HEADERS)
    assert response.status_code == 404


# ================================================================
# ТЕСТЫ ЛОГОВ
# ================================================================

def test_get_logs():
    """Тест получения логов"""
    response = client.get("/logs", headers=HEADERS)
    assert response.status_code == 200
    assert "logs" in response.json()


# ================================================================
# ТЕСТЫ БЕЗ АВТОРИЗАЦИИ
# ================================================================

def test_zones_without_auth():
    """Тест доступа к зонам без авторизации"""
    response = client.get("/zones")
    assert response.status_code == 401


def test_records_without_auth():
    """Тест доступа к записям без авторизации"""
    response = client.get("/records")
    assert response.status_code == 401


def test_logs_without_auth():
    """Тест доступа к логам без авторизации"""
    response = client.get("/logs")
    assert response.status_code == 401


def test_create_zone_without_auth():
    """Тест создания зоны без авторизации"""
    response = client.post("/zones", json={"name": "test.com"})
    assert response.status_code == 401
