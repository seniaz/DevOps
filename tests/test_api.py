import json


class TestRoot:
    def test_root_returns_html(self, client):
        resp = client.get("/", headers={"Accept": "text/html"})
        assert resp.status_code == 200
        assert b"Simple Inventory" in resp.data
        assert b"/items" in resp.data

    def test_root_default_accept(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert b"<table" in resp.data


class TestListItems:
    def test_empty_list_json(self, client):
        resp = client.get("/items", headers={"Accept": "application/json"})
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_list_after_create(self, client):
        client.post("/items", json={"name": "Laptop", "quantity": 5})
        resp = client.get("/items", headers={"Accept": "application/json"})
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["name"] == "Laptop"
        assert "id" in data[0]

    def test_list_html(self, client):
        client.post("/items", json={"name": "Monitor", "quantity": 3})
        resp = client.get("/items", headers={"Accept": "text/html"})
        assert resp.status_code == 200
        assert b"Monitor" in resp.data
        assert b"<table" in resp.data

    def test_list_multiple(self, client):
        for name, qty in [("Mouse", 10), ("Keyboard", 7), ("Cable", 50)]:
            client.post("/items", json={"name": name, "quantity": qty})
        resp = client.get("/items", headers={"Accept": "application/json"})
        assert len(resp.get_json()) == 3


class TestCreateItem:
    def test_create_json(self, client):
        resp = client.post("/items", json={"name": "Projector", "quantity": 2})
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["name"] == "Projector"
        assert data["quantity"] == 2
        assert "id" in data
        assert "created_at" in data

    def test_create_html(self, client):
        resp = client.post(
            "/items",
            json={"name": "Tablet", "quantity": 4},
            headers={"Accept": "text/html"},
        )
        assert resp.status_code == 201
        assert b"Tablet" in resp.data

    def test_create_missing_name(self, client):
        resp = client.post("/items", json={"quantity": 1})
        assert resp.status_code == 400

    def test_create_empty_name(self, client):
        resp = client.post("/items", json={"name": "", "quantity": 1})
        assert resp.status_code == 400

    def test_create_negative_quantity(self, client):
        resp = client.post("/items", json={"name": "Test", "quantity": -5})
        assert resp.status_code == 400

    def test_create_invalid_quantity(self, client):
        resp = client.post("/items", json={"name": "Test", "quantity": "abc"})
        assert resp.status_code == 400


class TestGetItem:
    def test_get_by_id_json(self, client):
        post = client.post("/items", json={"name": "Chair", "quantity": 15})
        item_id = post.get_json()["id"]
        resp = client.get(f"/items/{item_id}", headers={"Accept": "application/json"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["id"] == item_id
        assert data["name"] == "Chair"
        assert data["quantity"] == 15
        assert "created_at" in data

    def test_get_by_id_html(self, client):
        post = client.post("/items", json={"name": "Desk", "quantity": 8})
        item_id = post.get_json()["id"]
        resp = client.get(f"/items/{item_id}", headers={"Accept": "text/html"})
        assert resp.status_code == 200
        assert b"Desk" in resp.data
        assert b"<table" in resp.data

    def test_get_not_found(self, client):
        resp = client.get("/items/99999", headers={"Accept": "application/json"})
        assert resp.status_code == 404


class TestErrorHandling:
    def test_404_json(self, client):
        resp = client.get("/items/99999", headers={"Accept": "application/json"})
        assert resp.status_code == 404
        data = resp.get_json()
        assert "error" in data

    def test_404_html(self, client):
        resp = client.get("/items/99999", headers={"Accept": "text/html"})
        assert resp.status_code == 404
        assert b"404" in resp.data
