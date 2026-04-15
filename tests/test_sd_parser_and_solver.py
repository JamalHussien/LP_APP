import numpy as np
from fastapi.testclient import TestClient
import sympy as sp

from optimization.infrastructure.quadratic_parser import SymbolicObjectiveParser, ObjectiveParseError
from optimization.algorithms.gradient.steepest_descent import SteepestDescentSolver, make_quadratic_objective
from optimization.app.api import create_app


def test_parser_quartic_expression_parses_and_grad():
    expr = "x^4 + y^4 - 3*x^2 - 3*y^2 + 2*x*y"
    objective, vars_order, meta = SymbolicObjectiveParser.parse_expression(expr)
    assert vars_order == ["x", "y"]
    x0 = np.array([0.5, -0.25], dtype=float)
    fx = objective.f(x0)
    gx = objective.grad(x0)
    assert np.isfinite(fx)
    assert np.all(np.isfinite(gx))
    assert meta["A"] is None  # not quadratic


def test_parser_accepts_unicode_minus_signs():
    expr = "x*y^2 \u2212 x^2 \u2212 y"
    objective, vars_order, meta = SymbolicObjectiveParser.parse_expression(expr)
    assert vars_order == ["x", "y"]
    x0 = np.array([1.0, 0.0], dtype=float)
    assert np.isfinite(objective.f(x0))
    assert np.all(np.isfinite(objective.grad(x0)))
    assert meta["sympy_expr"].free_symbols == set(sp.symbols("x y"))


def test_nonquadratic_uses_backtracking_alpha_monotone():
    expr = "-2*x**2 + 2*x*y + 2*y**3"
    objective, _, _ = SymbolicObjectiveParser.parse_expression(expr)
    solver = SteepestDescentSolver(objective)
    res = solver.solve([0.2, 0.1], mode="optimal", max_iters=3)
    assert res.alphas, "alphas should be recorded"
    assert res.step_modes[0] in ("exact_line", "backtracking")
    assert res.alphas[0] > 0.0
    assert np.all(np.isfinite(np.array(res.points)))


def test_api_accepts_nonquadratic_expression():
    client = TestClient(create_app())
    payload = {
        "expression": "-2*x^2 + 2*x*y + 2*y^3",
        "start": [0.1, 0.1],
        "mode": "optimal",
        "alpha": 0.1,
        "max_iters": 5,
    }
    res = client.post("/optimize/steepest-descent", json=payload)
    assert res.status_code in (200, 400)
    if res.status_code == 200:
        data = res.json()
        assert "alphas" in data
        assert len(data["alphas"]) >= 1
        assert data["success"] in (True, False)
        assert np.all(np.isfinite(np.array(data["points"])))
    else:
        msg = res.json()
        assert "detail" in msg


def test_api_accepts_unicode_minus_expression():
    client = TestClient(create_app())
    payload = {
        "expression": "x*y^2 \u2212 x^2 \u2212 y",
        "start": [1.0, 0.0],
        "mode": "optimal",
        "max_iters": 1,
    }
    res = client.post("/optimize/steepest-descent", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["variables"] == ["x", "y"]
    assert len(data["points"]) >= 2


def test_api_rejects_start_length_mismatch():
    client = TestClient(create_app())
    payload = {
        "expression": "x^2 + y^2",
        "start": [0.0, 0.0, 0.0],
        "mode": "constant",
        "alpha": 0.1,
    }
    res = client.post("/optimize/steepest-descent", json=payload)
    assert res.status_code == 400


def test_exact_line_search_nonquadratic_alpha_value():
    expr = "x*y**2 - x**2 - y"
    objective, _, _ = SymbolicObjectiveParser.parse_expression(expr)
    solver = SteepestDescentSolver(objective)
    res = solver.solve([1.0, 0.0], mode="optimal", max_iters=1)
    assert res.step_modes[0] == "exact_line"
    assert abs(res.alphas[0] - 1.5408) < 1e-2


def test_exact_line_search_can_maximize_nonquadratic_objective():
    objective, _, _ = SymbolicObjectiveParser.parse_expression("-(x - 2)^4")
    solver = SteepestDescentSolver(objective)
    res = solver.solve([1.0], mode="optimal", sense="maximize", max_iters=1)
    assert res.step_modes[0] == "exact_line"
    assert abs(res.alphas[0] - 0.25) < 1e-2
    assert res.f_values[-1] > res.f_values[0]


def test_expression_quadratic_matches_matrix_exact_step():
    matrix_solver = SteepestDescentSolver(make_quadratic_objective([[2, 0], [0, 8]], [0, 0], 0.0))
    expression_objective, _, _ = SymbolicObjectiveParser.parse_expression("x^2 + 4*y^2")
    expression_solver = SteepestDescentSolver(expression_objective)

    matrix_res = matrix_solver.solve([1.0, 0.25], mode="optimal", max_iters=1)
    expression_res = expression_solver.solve([1.0, 0.25], mode="optimal", max_iters=1)

    assert abs(matrix_res.alphas[0] - 0.2) < 1e-8
    assert abs(expression_res.alphas[0] - matrix_res.alphas[0]) < 1e-8
    assert np.allclose(expression_res.points[-1], matrix_res.points[-1])


def test_exact_line_search_can_expand_beyond_default_unit_scale():
    objective, _, _ = SymbolicObjectiveParser.parse_expression("x^4")
    solver = SteepestDescentSolver(objective)
    res = solver.solve([0.1], mode="optimal", max_iters=1)
    assert res.step_modes[0] == "exact_line"
    assert abs(res.alphas[0] - 25.0) < 1e-2


def test_api_accepts_maximize_sense_for_steepest_descent():
    client = TestClient(create_app())
    payload = {
        "expression": "-(x - 2)^4",
        "start": [1.0],
        "sense": "maximize",
        "mode": "optimal",
        "max_iters": 2,
    }
    res = client.post("/optimize/steepest-descent", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data["alphas"]) >= 1
    assert data["f_values"][-1] >= data["f_values"][0]
