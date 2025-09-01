from fastapi.testclient import TestClient
from conftest import signup_and_login


def test_item_crud_flow(client: TestClient):
    token = signup_and_login(client, "user@example.com", "password123")
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
