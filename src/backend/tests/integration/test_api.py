import os
import pytest
from fastapi.testclient import TestClient
from src.src.app.main import app

# Импортируем реализации для Knot
from src.src.knot_wrapper.implementation.synchronous import *
from src.src.knot_wrapper.transaction import set_knot_connection_path # пути такие, из-за того, что запуск будет в контейнере, а там другой путь к сокету

# Читаем путь к сокету из переменной окружения Docker (по умолчанию /run/knot/knot.sock)
knot_socket = os.getenv("KNOT_SOCKET", "/run/knot/knot.sock")
set_knot_connection_path(knot_socket)

HEADERS = {"X-User": "admin"}

client = TestClient(app)

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