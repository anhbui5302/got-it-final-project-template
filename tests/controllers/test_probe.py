def test_ping(client):
    response = client.get("/ping")
    assert response.status_code == 405

    response = client.post("/ping")
    assert response.status_code == 200


def test_ready(client):
    response = client.get("/ready")
    assert response.status_code == 200

    response = client.post("/ready")
    assert response.status_code == 405
