from fastapi.testclient import TestClient

from optimization.app.api import create_app


client = TestClient(create_app())


def test_golden_section_api_minimization():
    payload = {
        "expression": "(x - 2)^2",
        "a": 0,
        "b": 5,
        "sense": "minimize",
        "epsilon": 1e-5,
        "max_iters": 200,
    }
    res = client.post("/optimize/golden-section", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert abs(data["x_star"] - 2.0) < 1e-3
    assert data["variable"] == "x"
    assert data["history"][0]["iteration"] == 0
    assert len(data["history"]) == data["iterations"] + 1
    assert data["history"][0]["x1"] > data["history"][0]["x2"]
    assert "plot" in data


def test_golden_section_api_maximization():
    payload = {
        "expression": "-(x - 3)^2 + 5",
        "a": 0,
        "b": 6,
        "sense": "maximize",
        "epsilon": 1e-5,
        "max_iters": 200,
    }
    res = client.post("/optimize/golden-section", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert abs(data["x_star"] - 3.0) < 1e-3
    assert abs(data["fx_star"] - 5.0) < 1e-4
    assert data["history"][0]["iteration"] == 0


def test_golden_section_api_returns_k0_when_interval_is_already_small():
    payload = {
        "expression": "(x - 2)^2",
        "a": 0,
        "b": 1,
        "sense": "minimize",
        "epsilon": 2,
        "max_iters": 10,
    }
    res = client.post("/optimize/golden-section", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["iterations"] == 0
    assert len(data["history"]) == 1
    assert data["history"][0]["iteration"] == 0


def test_golden_section_api_matches_requested_d_example_on_zero_to_two():
    payload = {
        "expression": "x^4 - 14*x^3 + 60*x^2 - 70*x",
        "a": 0,
        "b": 2,
        "sense": "minimize",
        "epsilon": 1e-5,
        "max_iters": 10,
    }
    res = client.post("/optimize/golden-section", json=payload)
    assert res.status_code == 200
    data = res.json()
    first = data["history"][0]
    assert abs(first["x1"] - 1.2360679774997898) < 1e-12
    assert abs(first["x2"] - 0.7639320225002102) < 1e-12


def test_golden_section_api_rejects_invalid_interval():
    payload = {
        "expression": "(x - 2)^2",
        "a": 5,
        "b": 0,
        "sense": "minimize",
        "epsilon": 1e-5,
        "max_iters": 50,
    }
    res = client.post("/optimize/golden-section", json=payload)
    assert res.status_code == 422


def test_golden_section_api_handles_bad_expression_evaluation():
    payload = {
        "expression": "sqrt(x)",
        "a": -4,
        "b": -1,
        "sense": "minimize",
        "epsilon": 1e-5,
        "max_iters": 20,
    }
    res = client.post("/optimize/golden-section", json=payload)
    assert res.status_code == 400
    assert "non-finite" in res.json()["detail"]
