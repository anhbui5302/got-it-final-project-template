import json

import pytest


def test_register_success(client):
    # Valid email and password
    request_body = {"email": "valid@email.com", "password": "Password123"}
    response = client.post(
        "/users",
        headers={"Content-Type": "application/json"},
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 4  # id, email, created, updated
    assert data["id"] == 3  # Already 2 users inserted
    assert data["email"] == request_body["email"]


def test_register_success_with_redundant_fields(client):
    # Valid email and password with other fields in request body
    request_body = {
        "email": "valid@email1.com",
        "password": "Password123",
        "random": 1,
        "fields": True,
    }
    response = client.post(
        "/users",
        headers={"Content-Type": "application/json"},
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 4  # id, email, created, updated
    assert data["id"] == 4  # Already 3 users inserted
    assert data["email"] == request_body["email"]


def test_register_fail_email_already_exists(client):
    # email already exists in db
    request_body = {"email": "user@abc.com", "password": "Password123"}
    response = client.post(
        "/users",
        headers={"Content-Type": "application/json"},
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400002
    assert len(data["error_data"]) == 1
    error_data_keys = data["error_data"].keys()
    assert "email" in error_data_keys


def test_register_fail_missing_request_body(client):
    # No request body
    response = client.post("/users", headers={"Content-Type": "application/json"})
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400000
    assert data["error_data"] is None


def test_register_fail_missing_content_type(client):
    # No Content-Type header
    request_body = {"email": "valid@email.com", "password": "Password123"}
    response = client.post("/users", data=json.dumps(request_body))
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400000
    assert data["error_data"] is None


def test_register_fail_content_type_not_json(client):
    request_body = {"email": "valid@email.com", "password": "Password123"}
    response = client.post(
        "/users", headers={"Content-Type": "text/plain"}, data=json.dumps(request_body)
    )
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400000
    assert data["error_data"] is None


def test_register_fail_empty_request_body(client):
    request_body = {}
    response = client.post(
        "/users",
        headers={"Content-Type": "application/json"},
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400001
    assert len(data["error_data"]) == 2
    error_data_keys = data["error_data"].keys()
    assert "email" in error_data_keys
    assert "password" in error_data_keys


def test_register_fail_missing_email(client):
    request_body = {"password": "Password123"}
    response = client.post(
        "/users",
        headers={"Content-Type": "application/json"},
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400001
    assert len(data["error_data"]) == 1
    error_data_keys = data["error_data"].keys()
    assert "email" in error_data_keys


def test_register_fail_missing_password(client):
    request_body = {"email": "valid@email.com"}
    response = client.post(
        "/users",
        headers={"Content-Type": "application/json"},
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400001
    assert len(data["error_data"]) == 1
    error_data_keys = data["error_data"].keys()
    assert "password" in error_data_keys


@pytest.mark.parametrize(
    "password",
    ["Aa123", "Aa123456789012345678901234567890z", "aaaaa1", "AAAAA1", "AAAaaa"],
)
def test_register_fail_invalid_password(client, password):
    request_body = {"email": "validemail@true.com", "password": password}
    response = client.post(
        "/users",
        headers={"Content-Type": "application/json"},
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400001
    assert len(data["error_data"]) == 1
    error_data_keys = data["error_data"].keys()
    assert "password" in error_data_keys


@pytest.mark.parametrize(
    "email",
    [
        "Abc.example.com",
        "A@b@c@example.com",
        "i_like_underscore@but_its_not_allowed_in_this_part" ".example.com",
        'just"not"right@example.com',
        'a"b(c)d,e:f;g<h>i[j\\k]l@example.com',
        'this is"not\\allowed@example.com',
        'this\\ still"not\\\\allowed@example.com',
        "QA[icon]CHOCOLATE[icon]@test.com",
    ],
)
def test_register_fail_invalid_email(client, email):
    request_body = {"email": email, "password": "Password123"}
    response = client.post(
        "/users",
        headers={"Content-Type": "application/json"},
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400001
    assert len(data["error_data"]) == 1
    error_data_keys = data["error_data"].keys()
    assert "email" in error_data_keys


def test_register_fail_multiple_fields(client):
    request_body = {"email": "invalidemail", "password": "a"}
    response = client.post(
        "/users",
        headers={"Content-Type": "application/json"},
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400001
    assert len(data["error_data"]) == 2
    error_data_keys = data["error_data"].keys()
    assert "email" in error_data_keys
    assert "password" in error_data_keys


def test_login_success(client):
    # Valid email and password
    request_body = {"email": "user@abc.com", "password": "Password123"}
    response = client.post(
        "/tokens",
        headers={"Content-Type": "application/json"},
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 1
    assert "access_token" in data


def test_login_success_with_redundant_fields(client):
    # Valid email and password with other fields in request body
    request_body = {
        "email": "user@abc.com",
        "password": "Password123",
        "random": 1,
        "fields": True,
    }
    response = client.post(
        "/tokens",
        headers={"Content-Type": "application/json"},
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 1
    assert "access_token" in data


def test_login_fail_email_already_exists(client):
    # Email does not exist in db
    request_body = {"email": "not@indb.com", "password": "Password123"}
    response = client.post(
        "/tokens",
        headers={"Content-Type": "application/json"},
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 401
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 401000
    assert data["error_data"] is None


def test_login_fail_password_incorrect(client):
    # Password is not correct
    request_body = {"email": "user@abc.com", "password": "WrongPassword123"}
    response = client.post(
        "/tokens",
        headers={"Content-Type": "application/json"},
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 401
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 401000
    assert data["error_data"] is None


def test_login_fail_missing_request_body(client):
    response = client.post("/tokens", headers={"Content-Type": "application/json"})
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400000
    assert data["error_data"] is None


def test_login_fail_missing_content_type(client):
    request_body = {"email": "user@abc.com", "password": "Password123"}
    response = client.post("/tokens", data=json.dumps(request_body))
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400000
    assert data["error_data"] is None


def test_login_fail_content_type_not_json(client):
    request_body = {"email": "user@abc.com", "password": "Password123"}
    response = client.post(
        "/tokens", headers={"Content-Type": "text/plain"}, data=json.dumps(request_body)
    )
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400000
    assert data["error_data"] is None


def test_login_fail_empty_request_body(client):
    # Empty body
    request_body = {}
    response = client.post(
        "/tokens",
        headers={"Content-Type": "application/json"},
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400001
    assert len(data["error_data"]) == 2
    error_data_keys = data["error_data"].keys()
    assert "email" in error_data_keys
    assert "password" in error_data_keys


def test_login_fail_missing_email(client):

    request_body = {"password": "Password123"}
    response = client.post(
        "/tokens",
        headers={"Content-Type": "application/json"},
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400001
    assert len(data["error_data"]) == 1
    error_data_keys = data["error_data"].keys()
    assert "email" in error_data_keys


def test_login_fail_missing_password(client):
    # Missing email or password
    request_body = {"email": "user@abc.com"}
    response = client.post(
        "/tokens",
        headers={"Content-Type": "application/json"},
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400001
    assert len(data["error_data"]) == 1
    error_data_keys = data["error_data"].keys()
    assert "password" in error_data_keys


@pytest.mark.parametrize(
    "password",
    ["Aa123", "Aa123456789012345678901234567890z", "aaaaa1", "AAAAA1", "AAAaaa"],
)
def test_login_fail_invalid_password(client, password):
    # Email/password is not valid
    request_body = {"email": "validemail@yay.com", "password": password}
    response = client.post(
        "/tokens",
        headers={"Content-Type": "application/json"},
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400001
    assert len(data["error_data"]) == 1
    error_data_keys = data["error_data"].keys()
    assert "password" in error_data_keys


@pytest.mark.parametrize(
    "email",
    [
        "Abc.example.com",
        "A@b@c@example.com",
        "i_like_underscore@but_its_not_allowed_in_this_part" ".example.com",
        'just"not"right@example.com',
        'a"b(c)d,e:f;g<h>i[j\\k]l@example.com',
        'this is"not\\\allowed@example.com',
        'this\\ still"not\\\\allowed@example.com',
        "QA[icon]CHOCOLATE[icon]@test.com",
    ],
)
def test_login_fail_invalid_email(client, email):
    # Email/password is not valid
    request_body = {"email": email, "password": "Password123"}
    response = client.post(
        "/tokens",
        headers={"Content-Type": "application/json"},
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400001
    assert len(data["error_data"]) == 1
    error_data_keys = data["error_data"].keys()
    assert "email" in error_data_keys


def test_login_fail_invalid_fields(client):
    request_body = {"email": "invalidemail", "password": "a"}
    response = client.post(
        "/tokens",
        headers={"Content-Type": "application/json"},
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400001
    assert len(data["error_data"]) == 2
    error_data_keys = data["error_data"].keys()
    assert "email" in error_data_keys
    assert "password" in error_data_keys
