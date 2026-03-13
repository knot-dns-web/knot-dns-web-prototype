from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_create_zone():

    response = client.post(
        "/zones",
        json={"name": "example.com"}
    )

    assert response.status_code == 200

def test_list_zones():

    response = client.get("/zones")

    assert response.status_code == 200

# pytest src\backend\src\app\test_zones.py -v