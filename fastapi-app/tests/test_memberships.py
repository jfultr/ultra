from fastapi.testclient import TestClient
from conftest import signup_and_login


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_list_members_and_non_member_404(client: TestClient):
    owner_token = signup_and_login(client, "owner@example.com", "password123")
    owner_headers = _auth_header(owner_token)

    # Create a project by owner
    res = client.post("/api/projects/", json={"title": "Proj", "description": "Desc"}, headers=owner_headers)
    assert res.status_code == 201, res.text
    project_id = res.json()["id"]

    # Owner can list members (should contain owner as 'owner')
    res = client.get(f"/api/projects/{project_id}/users", headers=owner_headers)
    assert res.status_code == 200, res.text
    members = res.json()
    assert len(members) == 1
    assert members[0]["role"] == "owner"

    # A non-member should receive 404 when trying to list members
    outsider_token = signup_and_login(client, "outsider@example.com", "password123")
    outsider_headers = _auth_header(outsider_token)
    res = client.get(f"/api/projects/{project_id}/users", headers=outsider_headers)
    assert res.status_code == 404


def test_owner_can_add_member_default_viewer_and_member_can_list(client: TestClient):
    owner_token = signup_and_login(client, "own2@example.com", "password123")
    owner_headers = _auth_header(owner_token)

    # Create
    res = client.post("/api/projects/", json={"title": "P", "description": "D"}, headers=owner_headers)
    assert res.status_code == 201, res.text
    project_id = res.json()["id"]

    # Create a second user
    member_token = signup_and_login(client, "member@example.com", "password123")

    # Owner adds second user without specifying role -> defaults to viewer
    res = client.post(
        f"/api/projects/{project_id}/users",
        json={"principal": "member@example.com"},
        headers=owner_headers,
    )
    assert res.status_code == 200, res.text

    # New member can list members now (should not be 404)
    res = client.get(f"/api/projects/{project_id}/users", headers=_auth_header(member_token))
    assert res.status_code == 200
    roles = {m["role"] for m in res.json()}
    assert "viewer" in roles and "owner" in roles


def test_non_owner_cannot_add_member(client: TestClient):
    owner_token = signup_and_login(client, "own3@example.com", "password123")
    owner_headers = _auth_header(owner_token)

    # Create project by owner
    res = client.post("/api/projects/", json={"title": "P2", "description": "D2"}, headers=owner_headers)
    assert res.status_code == 201, res.text
    project_id = res.json()["id"]

    # Create editor user and add as editor
    editor_token = signup_and_login(client, "editor@example.com", "password123")
    res = client.post(
        f"/api/projects/{project_id}/users",
        json={"principal": "editor@example.com", "role": "editor"},
        headers=owner_headers,
    )
    assert res.status_code == 200

    # Editor attempts to add another member -> forbidden (403)
    # Ensure the target user exists so we test permission (not 404 unknown user)
    signup_and_login(client, "third@example.com", "password123")
    res = client.post(
        f"/api/projects/{project_id}/users",
        json={"principal": "third@example.com"},
        headers=_auth_header(editor_token),
    )
    assert res.status_code == 403


def test_owner_can_update_role_and_non_owner_cannot(client: TestClient):
    owner_token = signup_and_login(client, "own4@example.com", "password123")
    owner_headers = _auth_header(owner_token)

    # Create project
    res = client.post("/api/projects/", json={"title": "P3", "description": "D3"}, headers=owner_headers)
    assert res.status_code == 201, res.text
    project_id = res.json()["id"]

    # Create viewer
    viewer_token = signup_and_login(client, "viewer2@example.com", "password123")
    res = client.post(
        f"/api/projects/{project_id}/users",
        json={"principal": "viewer2@example.com"},
        headers=owner_headers,
    )
    assert res.status_code == 200

    # Owner updates viewer to editor
    res = client.put(
        f"/api/projects/{project_id}/users",
        json={"principal": "viewer2@example.com", "role": "editor"},
        headers=owner_headers,
    )
    assert res.status_code == 200
    assert res.json()["role"] == "editor"

    # Editor tries to make themselves owner -> should be forbidden
    res = client.put(
        f"/api/projects/{project_id}/users",
        json={"principal": "viewer2@example.com", "role": "owner"},
        headers=_auth_header(viewer_token),
    )
    assert res.status_code == 403


def test_owner_can_remove_member_and_non_owner_cannot(client: TestClient):
    owner_token = signup_and_login(client, "own5@example.com", "password123")
    owner_headers = _auth_header(owner_token)

    # Create project
    res = client.post("/api/projects/", json={"title": "P4", "description": "D4"}, headers=owner_headers)
    assert res.status_code == 201, res.text
    project_id = res.json()["id"]

    # Add a member
    victim_token = signup_and_login(client, "victim@example.com", "password123")
    res = client.post(
        f"/api/projects/{project_id}/users",
        json={"principal": "victim@example.com", "role": "viewer"},
        headers=owner_headers,
    )
    assert res.status_code == 200

    # Non-owner (viewer) tries to remove themselves -> 403
    res = client.request(
        "DELETE",
        f"/api/projects/{project_id}/users",
        json={"principal": "victim@example.com", "role": "viewer"},
        headers=_auth_header(victim_token),
    )
    assert res.status_code == 403

    # Owner removes the member -> 204
    res = client.request(
        "DELETE",
        f"/api/projects/{project_id}/users",
        json={"principal": "victim@example.com"},
        headers=owner_headers,
    )
    assert res.status_code == 204

    # Listing members should not include the removed user
    res = client.get(f"/api/projects/{project_id}/users", headers=owner_headers)
    assert res.status_code == 200
    emails = [m.get("user_id") for m in res.json()]
    assert len(res.json()) == 1


def test_invalid_role_and_unknown_email_errors(client: TestClient):
    owner_token = signup_and_login(client, "own6@example.com", "password123")
    owner_headers = _auth_header(owner_token)

    # Create project
    res = client.post("/api/projects/", json={"title": "P5", "description": "D5"}, headers=owner_headers)
    assert res.status_code == 201, res.text
    project_id = res.json()["id"]

    # Unknown user email returns 404 on add
    res = client.post(
        f"/api/projects/{project_id}/users",
        json={"principal": "doesnotexist@example.com"},
        headers=owner_headers,
    )
    assert res.status_code == 404

    # Invalid role in update payload should 422 via Pydantic validation
    res = client.put(
        f"/api/projects/{project_id}/users",
        json={"principal": "doesnotexist@example.com", "role": "invalid-role"},
        headers=owner_headers,
    )
    assert res.status_code == 422


def test_duplicate_add_member_does_not_duplicate_membership(client: TestClient):
    owner_token = signup_and_login(client, "dupown@example.com", "password123")
    owner_headers = _auth_header(owner_token)

    # Create project
    res = client.post("/api/projects/", json={"title": "DupProj", "description": "D"}, headers=owner_headers)
    assert res.status_code == 201
    project_id = res.json()["id"]

    # Create member
    signup_and_login(client, "dupmem@example.com", "password123")

    # Add once
    res = client.post(f"/api/projects/{project_id}/users", json={"principal": "dupmem@example.com"}, headers=owner_headers)
    assert res.status_code == 200
    # Add again
    res = client.post(f"/api/projects/{project_id}/users", json={"principal": "dupmem@example.com"}, headers=owner_headers)
    assert res.status_code == 200

    # Only two memberships should exist: owner + viewer
    res = client.get(f"/api/projects/{project_id}/users", headers=owner_headers)
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_update_and_remove_non_member_forbidden(client: TestClient):
    owner_token = signup_and_login(client, "nmown@example.com", "password123")
    owner_headers = _auth_header(owner_token)

    # Create project
    res = client.post("/api/projects/", json={"title": "NM", "description": "X"}, headers=owner_headers)
    assert res.status_code == 201
    project_id = res.json()["id"]

    # Create another user but do not add to project
    signup_and_login(client, "notmember@example.com", "password123")

    # Update role for non-member -> 403
    res = client.put(
        f"/api/projects/{project_id}/users",
        json={"principal": "notmember@example.com", "role": "editor"},
        headers=owner_headers,
    )
    assert res.status_code == 403

    # Remove non-member -> 403
    res = client.request(
        "DELETE",
        f"/api/projects/{project_id}/users",
        json={"principal": "notmember@example.com"},
        headers=owner_headers,
    )
    assert res.status_code == 403


def test_owner_can_remove_self_and_loses_access(client: TestClient):
    owner_email = "selfown@example.com"
    owner_token = signup_and_login(client, owner_email, "password123")
    owner_headers = _auth_header(owner_token)

    # Create project
    res = client.post("/api/projects/", json={"title": "Self", "description": "Z"}, headers=owner_headers)
    assert res.status_code == 201
    project_id = res.json()["id"]

    # Add another member so the project still has members after owner leaves
    signup_and_login(client, "other@example.com", "password123")
    res = client.post(
        f"/api/projects/{project_id}/users",
        json={"principal": "other@example.com"},
        headers=owner_headers,
    )
    assert res.status_code == 200

    # Owner removes self
    res = client.request(
        "DELETE",
        f"/api/projects/{project_id}/users",
        json={"principal": owner_email},
        headers=owner_headers,
    )
    assert res.status_code == 204

    # Owner no longer has access
    res = client.get(f"/api/projects/{project_id}/users", headers=owner_headers)
    assert res.status_code == 404

    res = client.put(f"/api/projects/{project_id}", json={"title": "Nope"}, headers=owner_headers)
    assert res.status_code == 404

    res = client.delete(f"/api/projects/{project_id}", headers=owner_headers)
    assert res.status_code in (403, 404)


def test_add_member_nonexistent_project_and_email_case_mismatch(client: TestClient):
    owner_token = signup_and_login(client, "npown@example.com", "password123")
    owner_headers = _auth_header(owner_token)

    # Nonexistent project id
    missing_id = 999999999
    # Ensure target user exists so we hit the permission path (not user-not-found)
    signup_and_login(client, "nobody@example.com", "password123")
    res = client.post(
        f"/api/projects/{missing_id}/users",
        json={"principal": "nobody@example.com"},
        headers=owner_headers,
    )
    assert res.status_code == 403

    # Create project and user with lowercase email
    res = client.post("/api/projects/", json={"title": "Case", "description": "C"}, headers=owner_headers)
    assert res.status_code == 201
    project_id = res.json()["id"]
    signup_and_login(client, "mix@example.com", "password123")

    # Try add with uppercase email -> user lookup fails -> 404
    res = client.post(
        f"/api/projects/{project_id}/users",
        json={"principal": "MIX@EXAMPLE.COM"},
        headers=owner_headers,
    )
    assert res.status_code == 404


