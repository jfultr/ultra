from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def signup_and_login(email: str, password: str) -> str:
    res = client.post("/api/auth/signup", json={"email": email, "password": password})
    if not res.status_code == 409: 
        assert res.status_code == 200, res.text

    res = client.post("/api/auth/login", data={"username": email, "password": password})
    assert res.status_code == 200, res.text
    token = res.json()["access_token"]
    return token


def test_item_crud_flow(tmp_path):
    token = signup_and_login("user@example.com", "password123")
    headers = {"Authorization": f"Bearer {token}"}

    # Create
    res = client.post("/api/items/", json={"title": "A", "description": "B"}, headers=headers)
    assert res.status_code == 201, res.text
    item = res.json()
    item_id = item["id"]

    # List
    res = client.get("/api/items/", headers=headers)
    assert res.status_code == 200
    items = res.json()
    assert len(items) == 1

    # Get
    res = client.get(f"/api/items/{item_id}", headers=headers)
    assert res.status_code == 200
    assert res.json()["id"] == item_id

    # Update
    res = client.put(f"/api/items/{item_id}", json={"title": "X"}, headers=headers)
    assert res.status_code == 200
    assert res.json()["title"] == "X"

    # Delete
    res = client.delete(f"/api/items/{item_id}", headers=headers)
    assert res.status_code == 204

    # Not found after delete
    res = client.get(f"/api/items/{item_id}", headers=headers)
    assert res.status_code == 404


def test_create_new_project(tmp_path):
    pass

