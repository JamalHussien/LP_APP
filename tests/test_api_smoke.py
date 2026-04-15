from fastapi.testclient import TestClient
from optimization.app.api import create_app


client = TestClient(create_app())


def test_solve_numerical():
    payload = {
        "mode": "numerical",
        "kind": "linear",
        "n": 2,
        "c": [3, 5],
        "sense": "maximize",
        "constraints": [
            {"a": [1, 0], "sense": "<=", "b": 4},
            {"a": [0, 2], "sense": "<=", "b": 12},
            {"a": [3, 2], "sense": "<=", "b": 18},
        ],
        "nonneg": True,
    }
    res = client.post("/solve", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert len(data["x"]) == 2


def test_solve_graphical_png():
    payload = {
        "mode": "graphical",
        "kind": "linear",
        "n": 2,
        "c": [1, 1],
        "sense": "maximize",
        "constraints": [
            {"a": [1, 0], "sense": "<=", "b": 5},
            {"a": [0, 1], "sense": "<=", "b": 5},
            {"a": [1, 1], "sense": "<=", "b": 8},
        ],
        "nonneg": True,
    }
    res = client.post("/solve", json=payload)
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("image/png")
