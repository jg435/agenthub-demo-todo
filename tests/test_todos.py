import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"ok": True}


def test_create_and_list():
    r = client.post("/todos", json={"title": "write tests"})
    assert r.status_code == 201
    todo = r.json()
    assert todo["title"] == "write tests" and todo["done"] is False
    assert todo in client.get("/todos").json()


@pytest.mark.parametrize("title", ["", "   ", "\t\n"])
def test_empty_title_rejected(title):
    assert client.post("/todos", json={"title": title}).status_code == 422


def test_title_is_stripped():
    assert client.post("/todos", json={"title": "  padded  "}).json()["title"] == "padded"


def test_toggle_done():
    todo_id = client.post("/todos", json={"title": "toggle"}).json()["id"]
    response = client.patch(f"/todos/{todo_id}")
    assert response.status_code == 200
    assert response.json()["done"] is True
    assert client.patch(f"/todos/{todo_id}").json()["done"] is False
    assert client.patch("/todos/999999").status_code == 404


def test_delete():
    todo_id = client.post("/todos", json={"title": "temp"}).json()["id"]
    assert client.delete(f"/todos/{todo_id}").status_code == 204
    assert client.delete(f"/todos/{todo_id}").status_code == 404
