import json

import pytest

from main import app
from main.engines.test_helpers import generate_mock_user_token


def test_get_categories_success(client):
    # No authorization, no query params.
    response = client.get("/categories")
    data = response.get_json()
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert type(data["categories"]) == list
    assert len(data) == 4  # categories, page, per_page, total
    assert data["page"] == 1
    assert data["per_page"] == 20
    assert "total" in data


def test_get_categories_success_with_authorization(client):
    # With authorization, no query params.
    access_token = generate_mock_user_token(app, 1)
    response = client.get(
        "/categories", headers={"Authorization": "Bearer " + access_token}
    )
    data = response.get_json()
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 4  # categories, page, per_page, total
    assert type(data["categories"]) == list
    assert data["page"] == 1
    assert data["per_page"] == 20
    assert "total" in data


def test_get_categories_success_with_page(client):
    # With page
    response = client.get("/categories", query_string={"page": 3})
    data = response.get_json()
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 4  # categories, page, per_page, total
    assert type(data["categories"]) == list
    assert data["page"] == 3
    assert data["per_page"] == 20
    assert "total" in data


def test_get_categories_success_with_per_page(client):
    # With per_page
    response = client.get("/categories", query_string={"per_page": 2})
    data = response.get_json()
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 4  # categories, page, per_page, total
    assert type(data["categories"]) == list
    assert data["page"] == 1
    assert data["per_page"] == 2
    assert "total" in data


@pytest.mark.parametrize(
    "jwt",
    [
        generate_mock_user_token(app, 1),
        "Bearer ",
        "random string",
        "Bearer" + generate_mock_user_token(app, 1),
        "JWT " + generate_mock_user_token(app, 1),
    ],
)
def test_get_categories_fail_invalid_authorization(client, jwt):
    # Token has invalid format
    response = client.get("/categories", headers={"Authorization": jwt})
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400000
    assert data["error_data"] is None


def test_get_categories_fail_incorrect_authorization(client):
    # Token is invalid
    response = client.get("/categories", headers={"Authorization": "Bearer Invalid"})
    data = response.get_json()
    assert response.status_code == 401
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 401000
    assert data["error_data"] is None


@pytest.mark.parametrize("value", ["a", "-1", "0", "1.5"])
def test_get_categories_fail_incorrect_page(client, value):
    # page value is invalid
    response = client.get("/categories", query_string={"page": value})
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400001
    assert len(data["error_data"]) == 1
    error_data_keys = data["error_data"].keys()
    assert "page" in error_data_keys


@pytest.mark.parametrize("value", ["a", "-1", "0", "1.5"])
def test_get_categories_fail_incorrect_per_page(client, value):
    # per_page value is invalid
    response = client.get("/categories", query_string={"per_page": value})
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400001
    assert len(data["error_data"]) == 1
    error_data_keys = data["error_data"].keys()
    assert "per_page" in error_data_keys


def test_post_categories_success(client):
    access_token = generate_mock_user_token(app, 1)
    request_body = {"name": "test"}
    response = client.post(
        "/categories",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + access_token,
        },
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 5  # id, name, is_owner, created, updated
    assert data["name"] == "test"
    assert data["is_owner"]


def test_post_categories_success_with_redundant_fields(client):
    access_token = generate_mock_user_token(app, 1)
    # Random fields
    request_body = {"name": "test2", "random": True}
    response = client.post(
        "/categories",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + access_token,
        },
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 5  # id, name, is_owner, created, updated
    assert data["name"] == "test2"
    assert data["is_owner"]


def test_post_categories_fail_missing_name(client):
    # name is missing from request body
    access_token = generate_mock_user_token(app, 1)
    request_body = {"random": "test"}
    response = client.post(
        "/categories",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + access_token,
        },
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400001
    assert len(data["error_data"]) == 1
    error_data_keys = data["error_data"].keys()
    assert "name" in error_data_keys


def test_post_categories_fail_missing_request_body(client):
    # Request body is not valid json
    access_token = generate_mock_user_token(app, 1)
    response = client.post(
        "/categories",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + access_token,
        },
    )
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400000
    assert data["error_data"] is None


def test_post_categories_fail_empty_request_body(client):
    # Empty request body
    access_token = generate_mock_user_token(app, 1)
    request_body = {}
    response = client.post(
        "/categories",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + access_token,
        },
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400001
    assert len(data["error_data"]) == 1
    error_data_keys = data["error_data"].keys()
    assert "name" in error_data_keys


@pytest.mark.parametrize("name", ["", "x" * 256, " " * 10 + "x" * 256 + " " * 10])
def test_post_categories_fail_invalid_name(client, name):
    # name format is invalid
    access_token = generate_mock_user_token(app, 1)
    request_body = {"name": name}
    response = client.post(
        "/categories",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + access_token,
        },
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400001
    assert len(data["error_data"]) == 1
    error_data_keys = data["error_data"].keys()
    assert "name" in error_data_keys


def test_post_categories_fail_missing_content_type(client):
    access_token = generate_mock_user_token(app, 1)
    # Missing content-type
    request_body = {"name": "test"}
    response = client.post(
        "/categories",
        headers={"Authorization": "Bearer " + access_token},
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400000
    assert data["error_data"] is None


def test_post_categories_fail_content_type_not_json(client):
    access_token = generate_mock_user_token(app, 1)
    # Content-Type is not application/json
    request_body = {"name": "test"}
    response = client.post(
        "/categories",
        headers={
            "Authorization": "Bearer " + access_token,
            "Content-Type": "text/plain",
        },
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400000
    assert data["error_data"] is None


def test_post_categories_fail_missing_authorization(client):
    # Missing authorization header
    request_body = {"name": "test"}
    response = client.post(
        "/categories",
        headers={"Content-Type": "application/json"},
        data=json.dumps(request_body),
    )

    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400000
    assert data["error_data"] is None


@pytest.mark.parametrize(
    "jwt",
    [
        generate_mock_user_token(app, 1),
        "Bearer ",
        "random string",
        "Bearer" + generate_mock_user_token(app, 1),
        "JWT " + generate_mock_user_token(app, 1),
    ],
)
def test_post_categories_fail_invalid_authorization(client, jwt):
    # Token format is invalid
    request_body = {"name": "test"}
    response = client.post(
        "/categories",
        headers={"Authorization": jwt, "Content-Type": "application/json"},
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400000
    assert data["error_data"] is None


def test_post_categories_fail_incorrect_authorization(client):
    # Token is invalid
    request_body = {"name": "test"}
    response = client.post(
        "/categories",
        headers={"Authorization": "Bearer Invalid", "Content-Type": "application/json"},
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 401
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 401000
    assert data["error_data"] is None


def test_post_categories_fail_name_existed(client):
    # name provided already exists
    access_token = generate_mock_user_token(app, 3)
    request_body = {"name": "category1"}
    response = client.post(
        "/categories",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + access_token,
        },
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400002
    assert len(data["error_data"]) == 1
    error_data_keys = data["error_data"].keys()
    assert "name" in error_data_keys


def test_delete_categories_success(client):
    access_token = generate_mock_user_token(app, 1)

    response = client.delete(
        "/categories/1", headers={"Authorization": "Bearer " + access_token}
    )
    data = response.get_json()
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 0

    # Also check if items in the categories are deleted as well
    response = client.get(
        "/items/1", headers={"Authorization": "Bearer " + access_token}
    )
    data = response.get_json()
    assert response.status_code == 404
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 404000
    assert data["error_data"] is None

    response = client.get(
        "/items/5", headers={"Authorization": "Bearer " + access_token}
    )
    data = response.get_json()
    assert response.status_code == 404
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 404000
    assert data["error_data"] is None


@pytest.mark.parametrize("category_id", ["a", "-1", "0", "1.5"])
def test_delete_categories_fail_invalid_url_params(client, category_id):
    # url variable is invalid
    access_token = generate_mock_user_token(app, 1)

    response = client.delete(
        "/categories/" + category_id,
        headers={"Authorization": "Bearer " + access_token},
    )
    data = response.get_json()
    assert response.status_code == 404
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 404000
    assert data["error_data"] is None


def test_delete_categories_fail_missing_authorization(client):
    # Authorization header is missing
    response = client.delete("/categories/1")
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400000
    assert data["error_data"] is None


@pytest.mark.parametrize(
    "jwt",
    [
        generate_mock_user_token(app, 1),
        "Bearer ",
        "random string",
        "Bearer" + generate_mock_user_token(app, 1),
        "JWT " + generate_mock_user_token(app, 1),
    ],
)
def test_delete_categories_fail_invalid_authorization(client, jwt):
    # Token format is invalid
    response = client.delete("/categories/1", headers={"Authorization": jwt})
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400000
    assert data["error_data"] is None


def test_delete_categories_fail_incorrect_authorization(client):
    # Token is invalid
    response = client.delete(
        "/categories/1", headers={"Authorization": "Bearer Invalid"}
    )
    data = response.get_json()
    assert response.status_code == 401
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 401000
    assert data["error_data"] is None


def test_delete_categories_fail_forbidden(client):
    # Trying to delete a category another user created.
    # Category 2 belongs to user with id 2
    access_token = generate_mock_user_token(app, 1)
    response = client.delete(
        "/categories/2", headers={"Authorization": "Bearer " + access_token}
    )
    data = response.get_json()
    assert response.status_code == 403
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 403000
    assert data["error_data"] is None


def test_delete_categories_fail_not_found(client):
    # The specified category is not found
    access_token = generate_mock_user_token(app, 1)
    response = client.delete(
        "/categories/200", headers={"Authorization": "Bearer " + access_token}
    )
    data = response.get_json()
    assert response.status_code == 404
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 404000
    assert data["error_data"] is None
