import json

import pytest

from main import app
from main.engines.test_helpers import generate_mock_user_token


def test_get_items_success(client):
    # No authorization header, no query params
    response = client.get("/items")
    data = response.get_json()
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 4  # items, page, per_page, total
    assert type(data["items"]) == list
    assert data["page"] == 1
    assert data["per_page"] == 20
    assert "total" in data


def test_get_items_success_with_authorization(client):
    generate_mock_user_token(app, 1)
    access_token = generate_mock_user_token(app, 1)

    # With authorization header
    response = client.get("/items", headers={"Authorization": "Bearer " + access_token})
    data = response.get_json()
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 4  # items, page, per_page, total
    assert type(data["items"]) == list
    assert data["page"] == 1
    assert data["per_page"] == 20
    assert "total" in data


def test_get_items_success_with_category_id(client):
    # With category_id
    response = client.get("/items", query_string={"category_id": "1"})
    data = response.get_json()
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 4  # items, page, per_page, total
    assert type(data["items"]) == list
    assert data["page"] == 1
    assert data["per_page"] == 20
    assert "total" in data


def test_get_items_success_with_page(client):
    # With pagepage
    response = client.get("/items", query_string={"page": "2"})
    data = response.get_json()
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 4  # items, page, per_page, total
    assert type(data["items"]) == list
    assert data["page"] == 2
    assert data["per_page"] == 20
    assert "total" in data


def test_get_items_success_with_per_page(client):
    # per_page
    response = client.get("/items", query_string={"per_page": "3"})
    data = response.get_json()
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 4  # items, page, per_page, total
    assert type(data["items"]) == list
    assert data["page"] == 1
    assert data["per_page"] == 3
    assert "total" in data


@pytest.mark.parametrize("value", ["a", "-1", "0", "1.5"])
def test_get_items_fail_invalid_query_params(client, value):
    # category_id is invalid
    response = client.get("/items", query_string={"category_id": value})
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400001
    assert len(data["error_data"]) == 1
    error_data_keys = data["error_data"].keys()
    assert "category_id" in error_data_keys


@pytest.mark.parametrize("value", ["a", "-1", "0", "1.5"])
def test_get_items_fail_invalid_category_id(client, value):
    # category_id is invalid
    response = client.get("/items", query_string={"category_id": value})
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400001
    assert len(data["error_data"]) == 1
    error_data_keys = data["error_data"].keys()
    assert "category_id" in error_data_keys


def test_get_items_fail_category_does_not_exist(client):
    # category specified by id does not exist
    response = client.get("/items", query_string={"category_id": 200})
    data = response.get_json()
    assert response.status_code == 404
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 404000
    assert data["error_data"] is None


@pytest.mark.parametrize("value", ["a", "-1", "0", "1.5"])
def test_get_items_fail_invalid_page(client, value):
    # page is invalid
    response = client.get("/items", query_string={"page": value})
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400001
    assert len(data["error_data"]) == 1
    error_data_keys = data["error_data"].keys()
    assert "page" in error_data_keys


@pytest.mark.parametrize("value", ["a", "-1", "0", "1.5"])
def test_get_items_fail_invalid_per_page(client, value):
    # per_page is invalid
    response = client.get("/items", query_string={"per_page": value})
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400001
    assert len(data["error_data"]) == 1
    error_data_keys = data["error_data"].keys()
    assert "per_page" in error_data_keys


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
def test_get_items_fail_invalid_authorization(client, jwt):
    # Token format is invalid
    response = client.get("/items", headers={"Authorization": jwt})
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400000
    assert data["error_data"] is None


def test_get_items_fail_incorrect_authorization(client):
    # Token is invalid
    response = client.get("/items", headers={"Authorization": "Bearer Invalid"})
    data = response.get_json()
    assert response.status_code == 401
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 401000
    assert data["error_data"] is None


def test_get_item_success(client):
    # No authorization header
    response = client.get("/items/1")
    data = response.get_json()
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    # id, name, description, category_id, is_owner, created, updated
    assert len(data) == 7


def test_get_item_success_with_params(client):
    # With authorization header
    access_token = generate_mock_user_token(app, 1)
    response = client.get(
        "/items/1", headers={"Authorization": "Bearer " + access_token}
    )
    data = response.get_json()
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    # id, name, description, category_id, is_owner, created, updated
    assert len(data) == 7


@pytest.mark.parametrize("item_id", ["a", "-1", "0", "1.5"])
def test_get_item_fail_invalid_url_params(client, item_id):
    # url param is invalid
    response = client.get("/items/" + item_id)
    data = response.get_json()
    assert response.status_code == 404
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 404000
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
def test_get_item_fail_invalid_authorization(client, jwt):
    # Token format is invalid
    response = client.get("/items/1", headers={"Authorization": jwt})
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400000
    assert data["error_data"] is None


def test_get_item_fail_incorrect_authorization(client):
    # Token is invalid
    response = client.get("/items/1", headers={"Authorization": "Bearer Invalid"})
    data = response.get_json()
    assert response.status_code == 401
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 401000
    assert data["error_data"] is None


def test_get_item_fail_not_found(client):
    # Item does not exist in the database
    response = client.get("/items/200")
    data = response.get_json()
    assert response.status_code == 404
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 404000
    assert data["error_data"] is None


def test_post_items_success(client):
    access_token = generate_mock_user_token(app, 1)
    request_body = {"name": "test", "description": "test", "category_id": 1}
    response = client.post(
        "/items",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + access_token,
        },
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    # id, name, description, category_id, is_owner, created, updated
    assert len(data) == 7
    assert data["name"] == "test"
    assert data["description"] == "test"
    assert data["category_id"] == 1
    assert data["is_owner"]


def test_post_items_success_with_redundant_fields(client):
    access_token = generate_mock_user_token(app, 1)
    # Request body contains extra fields
    request_body = {
        "name": "test2",
        "description": "test",
        "category_id": 1,
        "random": True,
    }
    response = client.post(
        "/items",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + access_token,
        },
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    # id, name, description, category_id, is_owner, created, updated
    assert len(data) == 7
    assert data["name"] == "test2"
    assert data["description"] == "test"
    assert data["category_id"] == 1
    assert data["is_owner"]


def test_post_items_fail_missing_request_body(client):
    # request body is not valid json
    access_token = generate_mock_user_token(app, 1)

    response = client.post(
        "/items",
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


def test_post_items_fail_missing_all_fields(client):
    # Request body is missing all fields
    access_token = generate_mock_user_token(app, 1)

    request_body = {}
    response = client.post(
        "/items",
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
    assert len(data["error_data"]) == 3
    error_data_keys = data["error_data"].keys()
    assert "name" in error_data_keys
    assert "description" in error_data_keys
    assert "category_id" in error_data_keys


def test_post_items_fail_missing_name(client):
    access_token = generate_mock_user_token(app, 1)
    # Request body is missing name
    request_body = {"description": "test", "category_id": 1, "random": "test"}
    response = client.post(
        "/items",
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


def test_post_items_fail_missing_description(client):
    access_token = generate_mock_user_token(app, 1)

    # Request body is missing description
    request_body = {"name": "test2", "category_id": 1, "random": "test"}
    response = client.post(
        "/items",
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
    assert "description" in error_data_keys


def test_post_items_fail_missing_category_id(client):
    access_token = generate_mock_user_token(app, 1)

    # Request body is missing category_id
    request_body = {"name": "test3", "description": "test", "random": "test"}
    response = client.post(
        "/items",
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
    assert "category_id" in error_data_keys


def test_post_items_fail_category_does_not_exist(client):
    access_token = generate_mock_user_token(app, 1)
    # Request body contains extra fields
    request_body = {"name": "test2", "description": "test", "category_id": 200}
    # category specified by id does not exist
    response = client.post(
        "/items",
        query_string={"category_id": 200},
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + access_token,
        },
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 404
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 404000
    assert data["error_data"] is None


def test_post_items_fail_content_type_not_json(client):
    # Content-Type is not "application/json"
    access_token = generate_mock_user_token(app, 1)
    request_body = {"name": "test", "description": "test", "category_id": 1}
    response = client.post(
        "/items",
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


def test_post_items_fail_missing_content_type(client):
    access_token = generate_mock_user_token(app, 1)
    # Missing Content-Type
    request_body = {"name": "test", "description": "test", "category_id": 1}
    response = client.post(
        "/items",
        headers={"Authorization": "Bearer " + access_token},
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400000
    assert data["error_data"] is None


def test_post_items_fail_missing_authorization(client):
    # Authorization header is missing
    request_body = {"name": "test", "description": "test", "category_id": 1}
    response = client.post(
        "/items",
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
def test_post_items_fail_invalid_authorization(client, jwt):
    # Token format is invalid
    request_body = {"name": "test", "description": "test", "category_id": 1}
    response = client.post(
        "/items",
        headers={"Authorization": jwt, "Content-Type": "application/json"},
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400000
    assert data["error_data"] is None


def test_post_items_fail_incorrect_authorization(client):
    # Token is invalid
    request_body = {"name": "test", "description": "test", "category_id": 1}
    response = client.post(
        "/items",
        headers={"Authorization": "Bearer Invalid", "Content-Type": "application/json"},
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 401
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 401000
    assert data["error_data"] is None


def test_post_items_fail_name_existed(client):
    # Specified name already exists
    access_token = generate_mock_user_token(app, 1)
    request_body = {"name": "item1", "description": "test", "category_id": 1}
    response = client.post(
        "/items",
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


def test_put_items_success(client):
    access_token = generate_mock_user_token(app, 1)
    request_body = {"name": "testing", "description": "test", "category_id": 1}
    response = client.put(
        "/items/1",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + access_token,
        },
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    # id, name, description, category_id, is_owner, created, updated
    assert len(data) == 7
    assert data["name"] == "testing"
    assert data["description"] == "test"
    assert data["category_id"] == 1
    assert data["is_owner"]


def test_put_items_success_with_redundant_fields(client):
    # Request body contains extra fields
    access_token = generate_mock_user_token(app, 1)
    request_body = {
        "name": "testing",
        "description": "test",
        "category_id": 1,
        "random": True,
    }
    response = client.put(
        "/items/1",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + access_token,
        },
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    # id, name, description, category_id, is_owner, created, updated
    assert len(data) == 7
    assert data["name"] == "testing"
    assert data["description"] == "test"
    assert data["category_id"] == 1
    assert data["is_owner"]


@pytest.mark.parametrize("item_id", ["a", "-1", "0", "1.5"])
def test_put_items_fail_invalid_url_params(client, item_id):
    # url param is invalid
    access_token = generate_mock_user_token(app, 1)
    request_body = {"name": "testing", "description": "test", "category_id": 1}
    response = client.put(
        "/items/" + item_id,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + access_token,
        },
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 404
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 404000
    assert data["error_data"] is None


def test_put_items_fail_missing_authorization(client):
    # Authorization header is missing
    request_body = {"name": "testing", "description": "test", "category_id": 1}
    response = client.put(
        "/items/1",
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
def test_put_items_fail_invalid_authorization(client, jwt):
    # Token format is invalid
    request_body = {"name": "testing", "description": "test", "category_id": 1}
    response = client.put(
        "/items/1",
        headers={"Content-Type": "application/json", "Authorization": jwt},
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400000
    assert data["error_data"] is None


def test_put_items_fail_incorrect_authorization(client):
    # token is invalid
    request_body = {"name": "testing", "description": "test", "category_id": 1}
    response = client.put(
        "/items/1",
        headers={"Content-Type": "application/json", "Authorization": "Bearer Invalid"},
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 401
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 401000
    assert data["error_data"] is None


def test_put_items_fail_missing_request_body(client):
    # Request body is missing or not valid json
    access_token = generate_mock_user_token(app, 1)

    response = client.put(
        "/items/1",
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


def test_put_items_fail_missing_all_fields(client):
    # All fields in request body are missing
    access_token = generate_mock_user_token(app, 1)

    request_body = {}
    response = client.put(
        "/items/1",
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
    assert len(data["error_data"]) == 3
    error_data_keys = data["error_data"].keys()
    assert "name" in error_data_keys
    assert "description" in error_data_keys
    assert "category_id" in error_data_keys


def test_put_items_fail_missing_name(client):
    access_token = generate_mock_user_token(app, 1)

    # name is missing from request body
    request_body = {"description": "test", "category_id": 1}
    response = client.put(
        "/items/1",
        headers={
            "Authorization": "Bearer " + access_token,
            "Content-Type": "application/json",
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


def test_put_items_fail_missing_description(client):
    access_token = generate_mock_user_token(app, 1)

    request_body = {"name": "testing", "category_id": 1}
    response = client.put(
        "/items/1",
        headers={
            "Authorization": "Bearer " + access_token,
            "Content-Type": "application/json",
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
    assert "description" in error_data_keys


def test_put_items_fail_missing_category_id(client):
    access_token = generate_mock_user_token(app, 1)

    # category_id is missing from request body
    request_body = {"name": "testing", "description": "test"}
    response = client.put(
        "/items/1",
        headers={
            "Authorization": "Bearer " + access_token,
            "Content-Type": "application/json",
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
    assert "category_id" in error_data_keys


def test_put_items_fail_category_does_not_exist(client):
    access_token = generate_mock_user_token(app, 1)
    # Category specified by id does not exist
    request_body = {"name": "test1", "description": "test", "category_id": 200}
    response = client.put(
        "/items/1",
        query_string={"category_id": 200},
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + access_token,
        },
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 404
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 404000
    assert data["error_data"] is None


@pytest.mark.parametrize("name", ["", "x" * 256, " " * 10 + "x" * 256 + " " * 10])
def test_put_items_fail_invalid_name(client, name):
    # name is invalid
    access_token = generate_mock_user_token(app, 1)

    request_body = {"name": name, "description": "test", "category_id": 1}
    response = client.put(
        "/items/1",
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


def test_put_items_fail_name_already_exists(client):
    # another item with the same name already exists
    access_token = generate_mock_user_token(app, 1)

    request_body = {"name": "item2", "description": "test", "category_id": 1}
    response = client.put(
        "/items/1",
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


@pytest.mark.parametrize(
    "description", ["", "x" * 65536, " " * 10 + "x" * 65536 + " " * 10]
)
def test_put_items_fail_invalid_description(client, description):
    # description is invalid
    access_token = generate_mock_user_token(app, 1)

    request_body = {"name": "testing", "description": description, "category_id": 1}
    response = client.put(
        "/items/1",
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
    assert "description" in error_data_keys


@pytest.mark.parametrize("category_id", [0, -1, 1.5, "a", True])
def test_put_items_fail_invalid_category_id(client, category_id):
    # category_id is invalid
    access_token = generate_mock_user_token(app, 1)

    request_body = {
        "name": "testing",
        "description": "test",
        "category_id": category_id,
    }
    response = client.put(
        "/items/1",
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
    assert "category_id" in error_data_keys


def test_put_items_fail_forbidden(client):
    # trying to edit an item belonging to another user.
    # item 2 belongs to user with id 2
    access_token = generate_mock_user_token(app, 1)
    request_body = {"name": "testing", "description": "test", "category_id": 1}
    response = client.put(
        "/items/2",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + access_token,
        },
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 403
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 403000
    assert data["error_data"] is None


def test_put_items_fail_not_found(client):
    # item is not found
    access_token = generate_mock_user_token(app, 1)
    request_body = {"name": "testing", "description": "test", "category_id": 1}
    response = client.put(
        "/items/200",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + access_token,
        },
        data=json.dumps(request_body),
    )
    data = response.get_json()
    assert response.status_code == 404
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 404000
    assert data["error_data"] is None


def test_delete_items_success(client):
    access_token = generate_mock_user_token(app, 1)

    response = client.delete(
        "/items/1", headers={"Authorization": "Bearer " + access_token}
    )

    data = response.get_json()
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 0


@pytest.mark.parametrize("item_id", ["a", "-1", "0", "1.5"])
def test_delete_items_fail_invalid_url_params(client, item_id):
    # url param is invalid
    access_token = generate_mock_user_token(app, 1)

    response = client.delete(
        "/items/" + item_id, headers={"Authorization": "Bearer " + access_token}
    )
    data = response.get_json()
    assert response.status_code == 404
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 404000
    assert data["error_data"] is None


def test_delete_items_fail_missing_authorization(client):
    # Authorization header is missing
    response = client.delete("/items/1")
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
def test_delete_items_fail_invalid_authorization(client, jwt):
    # token format is invalid
    response = client.delete("/items/1", headers={"Authorization": jwt})
    data = response.get_json()
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 400000
    assert data["error_data"] is None


def test_delete_items_fail_incorrect_authorization(client):
    # token is invalid
    response = client.delete("/items/1", headers={"Authorization": "Bearer Invalid"})
    data = response.get_json()
    assert response.status_code == 401
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 401000
    assert data["error_data"] is None


def test_delete_items_fail_forbidden(client):
    # Trying to delete an item belonging to another user.
    # item 2 belongs to user with id 2
    access_token = generate_mock_user_token(app, 1)
    response = client.delete(
        "/items/2", headers={"Authorization": "Bearer " + access_token}
    )
    data = response.get_json()
    assert response.status_code == 403
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 403000
    assert data["error_data"] is None


def test_delete_items_fail_not_found(client):
    # item is not found.
    access_token = generate_mock_user_token(app, 1)
    response = client.delete(
        "/items/200", headers={"Authorization": "Bearer " + access_token}
    )
    data = response.get_json()
    assert response.status_code == 404
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == 3
    assert data["error_code"] == 404000
    assert data["error_data"] is None
