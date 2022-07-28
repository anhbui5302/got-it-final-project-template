import json

import pytest

from main import app
from main.engines.test_helpers import generate_mock_user_token


def test_get_categories_success(client):
    response = client.get("/categories")
    data = response.get_json()
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 4  # categories, page, per_page, total
    assert len(data["categories"]) == 4  # 4 categories in db
    assert data["page"] == 1
    assert data["per_page"] == 20
    assert data["total"] == 4


def test_get_categories_success_with_authorization(client):
    # Authorization header
    access_token = generate_mock_user_token(app, 1)
    response = client.get(
        "/categories", headers={"Authorization": "Bearer " + access_token}
    )
    data = response.get_json()
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 4  # categories, page, per_page, total
    assert len(data["categories"]) == 4  # 4 categories in db
    # categories 1 and 3 belong to user 1
    assert data["categories"][0]["is_owner"]
    assert data["categories"][2]["is_owner"]
    assert data["page"] == 1
    assert data["per_page"] == 20
    assert data["total"] == 4


def test_get_categories_success_with_page(client):
    # page
    response = client.get("/categories", query_string={"page": 3})
    data = response.get_json()
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 4  # categories, page, per_page, total
    assert len(data["categories"]) == 0  # 0 category in page 3
    assert data["page"] == 3
    assert data["per_page"] == 20
    assert data["total"] == 4


def test_get_categories_success_with_per_page(client):
    # per_page
    response = client.get("/categories", query_string={"per_page": 2})
    data = response.get_json()
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 4  # categories, page, per_page, total
    assert len(data["categories"]) == 2  # 2 categories in page 1
    assert data["page"] == 1
    assert data["per_page"] == 2
    assert data["total"] == 4


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
    response = client.get("/categories", headers={"Authorization": jwt})
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400000
    assert data["error_data"] is None


def test_get_categories_fail_incorrect_authorization(client):
    response = client.get("/categories", headers={"Authorization": "Bearer Invalid"})
    data = response.get_json()
    assert response.status_code == 401
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 401000
    assert data["error_data"] is None


@pytest.mark.parametrize("value", ["a", "-1", "0", "1.5"])
def test_get_categories_fail_incorrect_page(client, value):
    # page
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
    # per_page
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
    # Random parameters
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
    # Empty request body
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
    # Missing content-type or content-type is not application/json
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
    # Missing content-type or content-type is not application/json
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
    response = client.delete("/categories/1", headers={"Authorization": jwt})
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400000
    assert data["error_data"] is None


def test_delete_categories_fail_incorrect_authorization(client):
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
