from fastapi.testclient import TestClient
from conftest import signup_and_login


def test_project_crud_flow(client: TestClient):
    token = signup_and_login(client, "user@example.com", "password123")
    headers = {"Authorization": f"Bearer {token}"}

    # Create
    res = client.post("/api/projects/", json={"title": "A", "description": "B"}, headers=headers)
    assert res.status_code == 201, res.text
    project = res.json()
    project_id = project["id"]

    # List
    res = client.get("/api/projects/", headers=headers)
    assert res.status_code == 200
    projects = res.json()
    assert len(projects) == 1

    # Get
    res = client.get(f"/api/projects/{project_id}", headers=headers)
    assert res.status_code == 200
    assert res.json()["id"] == project_id

    # Update
    res = client.put(f"/api/projects/{project_id}", json={"title": "X"}, headers=headers)
    assert res.status_code == 200
    assert res.json()["title"] == "X"

    # Delete
    res = client.delete(f"/api/projects/{project_id}", headers=headers)
    assert res.status_code == 204

    # Not found after delete
    res = client.get(f"/api/projects/{project_id}", headers=headers)
    assert res.status_code == 404
