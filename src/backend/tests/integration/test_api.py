import os
import sys
from pathlib import Path

# Определяем путь к исходникам
# В контейнере: /app/src/src -> knot_wrapper напрямую
# В репозитории: src/backend/src -> knot_wrapper внутри backend
_CONTAINER_SRC = Path("/app/src/src")
_REPO_BACKEND_SRC = Path(__file__).resolve().parents[2] / "src" / "backend" / "src"

if _CONTAINER_SRC.exists():
    _BACKEND_SRC = _CONTAINER_SRC
else:
    _BACKEND_SRC = _REPO_BACKEND_SRC

if _BACKEND_SRC.is_dir() and str(_BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(_BACKEND_SRC))

# Импорт app с автоопределением пути
try:
    from app.main import app
except ImportError:
    from src.app.main import app

from fastapi.testclient import TestClient

# Получаем путь к сокету из переменной окружения
KNOT_SOCKET = os.getenv("KNOT_SOCKET", "/run/knot/knot.sock")

HEADERS = {"X-User": "admin"}

# Создаем тестовый клиент
client = TestClient(app)


# ================================================================
# ТЕСТЫ ДЛЯ КОРНЕВОГО ЭНДПОИНТА (/)
# ================================================================

def test_root():
    response = client.get("/")
    
    if response.status_code != 200:
        print(f"\n[ОШИБКА ROOT]: {response.json()}\n")
        
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "Knot DNS API running"


# ================================================================
# ТЕСТЫ ДЛЯ АУТЕНТИФИКАЦИИ (/auth)
# ================================================================

def test_login_success():
    """Тест успешной аутентификации"""
    response = client.post("/auth/login", data={
        "username": "admin",
        "password": "admin"
    })
    
    if response.status_code != 200:
        print(f"\n[ОШИБКА ЛОГИНА]: {response.json()}\n")
        
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
    assert "detail" in response.json()


def test_login_nonexistent_user():
    """Тест аутентификации с несуществующим пользователем"""
    response = client.post("/auth/login", data={
        "username": "nonexistent_user",
        "password": "password"
    })
    
    assert response.status_code == 401
    assert "detail" in response.json()

# ================================================================
# ТЕСТЫ ДЛЯ ЗОН (/zones)
# ================================================================

def test_create_zone():
    response = client.post("/zones", json={"name": "example.com"}, headers=HEADERS)
    
    if response.status_code not in [200, 201]:
        print(f"\n[ОШИБКА СОЗДАНИЯ ЗОНЫ]: {response.json()}\n")
        
    assert response.status_code in [200, 201]


def test_get_zones():
    response = client.get("/zones", headers=HEADERS)
    
    if response.status_code != 200:
        print(f"\n[ОШИБКА ПОЛУЧЕНИЯ ЗОН]: {response.json()}\n")
        
    assert response.status_code == 200
    assert "zones" in response.json()


def test_delete_zone():
    # Создаем
    client.post("/zones", json={"name": "todelete.com"}, headers=HEADERS)
    # Удаляем
    response = client.delete("/zones/todelete.com", headers=HEADERS)
    
    if response.status_code != 200:
        print(f"\n[ОШИБКА УДАЛЕНИЯ ЗОНЫ]: {response.json()}\n")
        
    assert response.status_code == 200


# ================================================================
# ТЕСТЫ ДЛЯ ЗАПИСЕЙ (/records)
# ================================================================

def test_create_record():
    response = client.post("/records", json={
        "zone": "example.com",
        "owner": "example_user",
        "type": "A",
        "ttl": 3600,
        "data": "192.168.1.1"
    }, headers=HEADERS)
    
    if response.status_code not in [200, 201]:
        print(f"\n[ОШИБКА СОЗДАНИЯ ЗАПИСИ]: {response.json()}\n")
        
    assert response.status_code in [200, 201]


def test_get_records():
    response = client.get("/records", headers=HEADERS)
    
    if response.status_code != 200:
        print(f"\n[ОШИБКА ПОЛУЧЕНИЯ ЗАПИСЕЙ]: {response.json()}\n")
        
    assert response.status_code == 200
    assert "records" in response.json()


def test_delete_record():
    client.post("/records", json={
        "zone": "example.com",
        "owner": "example_user",
        "type": "A",
        "ttl": 3600,
        "data": "192.168.1.1"
    }, headers=HEADERS)
    
    response = client.delete("/records/example.com/example_user/A", headers=HEADERS)
    
    if response.status_code != 200:
        print(f"\n[ОШИБКА УДАЛЕНИЯ ЗАПИСИ]: {response.json()}\n")
        
    assert response.status_code == 200


# ================================================================
# ТЕСТЫ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ (/users)
# ================================================================

def test_create_user():
    response = client.post("/users", json={
        "username": "example_user",
        "password": "password",
        "role": "user",
        "email": "example@example.com"
    }, headers=HEADERS)
    
    if response.status_code not in [200, 201]:
        print(f"\n[ОШИБКА СОЗДАНИЯ ЮЗЕРА]: {response.json()}\n")
        
    assert response.status_code in [200, 201]


def test_get_users():
    response = client.get("/users", headers=HEADERS)
    
    if response.status_code != 200:
        print(f"\n[ОШИБКА ПОЛУЧЕНИЯ ЮЗЕРОВ]: {response.json()}\n")
        
    assert response.status_code == 200


def test_delete_user():
    client.post("/users", json={
        "username": "todelete_user",
        "password": "password",
        "role": "user",
        "email": "del@example.com"
    }, headers=HEADERS)
    
    response = client.delete("/users/todelete_user", headers=HEADERS)
    
    if response.status_code != 200:
        print(f"\n[ОШИБКА УДАЛЕНИЯ ЮЗЕРА]: {response.json()}\n")
        
    assert response.status_code == 200


def test_update_user():
    """Тест обновления пользователя"""
    # Сначала создаем пользователя
    client.post("/users", json={
        "username": "updatable_user",
        "password": "old_password",
        "role": "user",
        "email": "old@example.com"
    }, headers=HEADERS)
    
    # Обновляем
    response = client.put("/users/updatable_user", json={
        "password": "new_password",
        "role": "admin",
        "email": "new@example.com"
    }, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"\n[ОШИБКА ОБНОВЛЕНИЯ ЮЗЕРА]: {response.json()}\n")
        
    assert response.status_code == 200
    assert response.json()["username"] == "updatable_user"
    assert response.json()["role"] == "admin"


# ================================================================
# ТЕСТЫ ДЛЯ ОБНОВЛЕНИЯ ЗАПИСЕЙ (/records PUT)
# ================================================================

def test_update_record():
    """Тест обновления DNS записи"""
    # Сначала создаем запись
    client.post("/records", json={
        "zone": "example.com",
        "owner": "update_test",
        "type": "A",
        "ttl": 3600,
        "data": "192.168.1.1"
    }, headers=HEADERS)
    
    # Обновляем
    response = client.put("/records/example.com", json={
        "old_owner": "update_test",
        "old_type": "A",
        "old_data": "192.168.1.1",
        "owner": "update_test",
        "type": "A",
        "ttl": 7200,
        "data": "192.168.1.2"
    }, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"\n[ОШИБКА ОБНОВЛЕНИЯ ЗАПИСИ]: {response.json()}\n")
        
    assert response.status_code == 200


# ================================================================
# ТЕСТЫ ДЛЯ ЭКСПОРТА/ИМПОРТА ЗОН (/zones)
# ================================================================

def test_export_zone():
    """Тест экспорта зоны"""
    # Сначала создаем зону
    client.post("/zones", json={"name": "exporttest.com"}, headers=HEADERS)
    
    # Добавляем запись в зону
    client.post("/records", json={
        "zone": "exporttest.com",
        "owner": "@",
        "type": "A",
        "ttl": 3600,
        "data": "192.168.1.1"
    }, headers=HEADERS)
    
    # Экспортируем
    response = client.get("/zones/exporttest.com/export", headers=HEADERS)
    
    if response.status_code != 200:
        print(f"\n[ОШИБКА ЭКСПОРТА ЗОНЫ]: {response.json()}\n")
        
    assert response.status_code == 200
    assert response.text  # Проверяем, что есть контент


def test_import_zone():
    """Тест импорта зоны"""
    zone_content = """$ORIGIN importtest.com.
$TTL 3600
@  IN  SOA ns1.example.com. admin.example.com. 2023010101 3600 900 604800 86400
@  IN  NS  ns1.example.com.
ns1 IN  A   192.168.1.1
@  IN  A   192.168.1.2
"""
    
    response = client.post("/zones/import", json={
        "name": "importtest.com",
        "content": zone_content
    }, headers=HEADERS)
    
    if response.status_code not in [200, 201]:
        print(f"\n[ОШИБКА ИМПОРТА ЗОНЫ]: {response.json()}\n")
        
    assert response.status_code in [200, 201]


# ================================================================
# ТЕСТЫ ДЛЯ ЛОГОВ (/logs)
# ================================================================

def test_get_logs():
    """Тест получения логов"""
    response = client.get("/logs", headers=HEADERS)
    
    if response.status_code != 200:
        print(f"\n[ОШИБКА ПОЛУЧЕНИЯ ЛОГОВ]: {response.json()}\n")
        
    assert response.status_code == 200
    assert "logs" in response.json()


# ================================================================
# НЕГАТИВНЫЕ ТЕСТЫ
# ================================================================

def test_create_zone_duplicate():
    """Тест создания дубликата зоны"""
    # Создаем зону
    client.post("/zones", json={"name": "duplicate.com"}, headers=HEADERS)
    
    # Пытаемся создать снова
    response = client.post("/zones", json={"name": "duplicate.com"}, headers=HEADERS)
    
    assert response.status_code == 400


def test_delete_nonexistent_zone():
    """Тест удаления несуществующей зоны"""
    response = client.delete("/zones/nonexistent12345.com", headers=HEADERS)
    
    # Может вернуть 404 или 200 (если ignore_not_exists=True)
    assert response.status_code in [200, 404]


def test_delete_nonexistent_record():
    """Тест удаления несуществующей записи"""
    response = client.delete("/records/nonexistent.com/nonexistent/A", headers=HEADERS)
    
    # Ожидаем 404
    assert response.status_code == 404


def test_delete_nonexistent_user():
    """Тест удаления несуществующего пользователя"""
    response = client.delete("/users/nonexistent_user_12345", headers=HEADERS)
    
    # Ожидаем 404
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
    
    # Ожидаем ошибку
    assert response.status_code == 400


def test_update_nonexistent_record():
    """Тест обновления несуществующей записи"""
    response = client.put("/records/example.com", json={
        "old_owner": "nonexistent",
        "old_type": "A",
        "old_data": "192.168.1.1",
        "owner": "nonexistent",
        "type": "A",
        "ttl": 3600,
        "data": "192.168.1.2"
    }, headers=HEADERS)
    
    # Ожидаем ошибку
    assert response.status_code == 400


# ================================================================
# ТЕСТЫ РАЗЛИЧНЫХ ТИПОВ ЗАПИСЕЙ
# ================================================================

def test_create_aaaa_record():
    """Тест создания AAAA записи"""
    response = client.post("/records", json={
        "zone": "example.com",
        "owner": "test_aaaa",
        "type": "AAAA",
        "ttl": 3600,
        "data": "::1"
    }, headers=HEADERS)
    
    if response.status_code not in [200, 201]:
        print(f"\n[ОШИБКА СОЗДАНИЯ AAAA ЗАПИСИ]: {response.json()}\n")
        
    assert response.status_code in [200, 201]


def test_create_cname_record():
    """Тест создания CNAME записи"""
    response = client.post("/records", json={
        "zone": "example.com",
        "owner": "test_cname",
        "type": "CNAME",
        "ttl": 3600,
        "data": "example.com"
    }, headers=HEADERS)
    
    if response.status_code not in [200, 201]:
        print(f"\n[ОШИБКА СОЗДАНИЯ CNAME ЗАПИСИ]: {response.json()}\n")
        
    assert response.status_code in [200, 201]


def test_create_txt_record():
    """Тест создания TXT записи"""
    response = client.post("/records", json={
        "zone": "example.com",
        "owner": "test_txt",
        "type": "TXT",
        "ttl": 3600,
        "data": "v=spf1 mx -all"
    }, headers=HEADERS)
    
    if response.status_code not in [200, 201]:
        print(f"\n[ОШИБКА СОЗДАНИЯ TXT ЗАПИСИ]: {response.json()}\n")
        
    assert response.status_code in [200, 201]


def test_create_mx_record():
    """Тест создания MX записи"""
    response = client.post("/records", json={
        "zone": "example.com",
        "owner": "@",
        "type": "MX",
        "ttl": 3600,
        "data": "10 mail.example.com"
    }, headers=HEADERS)
    
    if response.status_code not in [200, 201]:
        print(f"\n[ОШИБКА СОЗДАНИЯ MX ЗАПИСИ]: {response.json()}\n")
        
    assert response.status_code in [200, 201]


def test_create_ns_record():
    """Тест создания NS записи"""
    response = client.post("/records", json={
        "zone": "example.com",
        "owner": "@",
        "type": "NS",
        "ttl": 3600,
        "data": "ns1.example.com"
    }, headers=HEADERS)
    
    if response.status_code not in [200, 201]:
        print(f"\n[ОШИБКА СОЗДАНИЯ NS ЗАПИСИ]: {response.json()}\n")
        
    assert response.status_code in [200, 201]


def test_create_soa_record():
    """Тест создания SOA записи"""
    response = client.post("/records", json={
        "zone": "example.com",
        "owner": "@",
        "type": "SOA",
        "ttl": 3600,
        "data": "ns1.example.com. admin.example.com. 2023010101 3600 900 604800 86400"
    }, headers=HEADERS)
    
    if response.status_code not in [200, 201]:
        print(f"\n[ОШИБКА СОЗДАНИЯ SOA ЗАПИСИ]: {response.json()}\n")
        
    assert response.status_code in [200, 201]


# ================================================================
# ТЕСТЫ БЕЗ АВТОРИЗАЦИИ (401)
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
