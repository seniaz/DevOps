def test_alive_returns_200(client):
    resp = client.get("/health/alive")
    assert resp.status_code == 200
    assert resp.data == b"OK"


def test_ready_returns_200_when_db_ok(client):
    resp = client.get("/health/ready")
    assert resp.status_code == 200
    assert resp.data == b"OK"
