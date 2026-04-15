import numpy as np
from optimization.algorithms.gradient.steepest_descent import SteepestDescentSolver, make_quadratic_objective, exact_line_search_quadratic


def test_exact_step_convex_quadratic():
    A = [[2, 0], [0, 2]]
    b = [0, 0]
    c = 0
    objective = make_quadratic_objective(A, b, c)
    solver = SteepestDescentSolver(objective)
    res = solver.solve([1, 1], mode="optimal", max_iters=1)
    # alpha should be 0.5 => x1 = [0,0]
    assert len(res.alphas) == 1
    assert abs(res.alphas[0] - 0.5) < 1e-8
    assert np.linalg.norm(res.points[-1]) < 1e-8


def test_exact_step_concave_quadratic_for_maximization():
    A = [[-2, 0], [0, -2]]
    b = [0, 0]
    c = 0
    objective = make_quadratic_objective(A, b, c)
    solver = SteepestDescentSolver(objective)
    res = solver.solve([1, 1], mode="optimal", sense="maximize", max_iters=1)
    assert len(res.alphas) == 1
    assert abs(res.alphas[0] - 0.5) < 1e-8
    assert np.linalg.norm(res.points[-1]) < 1e-8


def test_exact_line_search_quadratic_wrapper_returns_scalar_alpha():
    alpha = exact_line_search_quadratic(np.array([[2.0, 0.0], [0.0, 2.0]]), np.array([2.0, 2.0]))
    assert abs(alpha - 0.5) < 1e-8


def test_constant_mode_alpha_fixed():
    A = [[2, 0], [0, 2]]
    b = [0, 0]
    c = 0
    objective = make_quadratic_objective(A, b, c)
    solver = SteepestDescentSolver(objective)
    res = solver.solve([1, 1], mode="constant", alpha=0.1, max_iters=2)
    assert res.alphas == [0.1, 0.1]


def test_constant_mode_moves_in_opposite_directions_for_minimize_and_maximize():
    A = [[2, 0], [0, 2]]
    b = [0, 0]
    c = 0
    objective = make_quadratic_objective(A, b, c)
    solver = SteepestDescentSolver(objective)
    minimize_res = solver.solve([1, 1], mode="constant", sense="minimize", alpha=0.1, max_iters=1)
    maximize_res = solver.solve([1, 1], mode="constant", sense="maximize", alpha=0.1, max_iters=1)
    assert np.allclose(minimize_res.points[-1], [0.8, 0.8])
    assert np.allclose(maximize_res.points[-1], [1.2, 1.2])


def test_exact_step_not_clamped_for_quadratic():
    A = [[2, 0], [0, 8]]
    b = [0, 0]
    c = 0
    objective = make_quadratic_objective(A, b, c)
    solver = SteepestDescentSolver(objective)
    res = solver.solve([1.0, 0.25], mode="optimal", max_iters=1)
    assert len(res.alphas) == 1
    assert abs(res.alphas[0] - 0.2) < 1e-8
    assert np.allclose(res.points[-1], [0.6, -0.15])


def test_indefinite_denominator_falls_back_instead_of_failing():
    A = [[1, 0], [0, -1]]
    b = [0, 0]
    c = 0
    objective = make_quadratic_objective(A, b, c)
    solver = SteepestDescentSolver(objective)
    res = solver.solve([1, 1], mode="optimal", max_iters=1)
    assert len(res.alphas) == 1
    assert res.step_modes[0] == "backtracking"
    assert res.fallback_reasons[0] is not None
    assert "exact_quadratic_failed" in res.fallback_reasons[0]


def test_indefinite_quadratic_maximization_falls_back_instead_of_failing():
    A = [[1, 0], [0, -1]]
    b = [0, 0]
    c = 0
    objective = make_quadratic_objective(A, b, c)
    solver = SteepestDescentSolver(objective)
    res = solver.solve([1, 1], mode="optimal", sense="maximize", max_iters=1)
    assert len(res.alphas) == 1
    assert res.step_modes[0] == "backtracking"
    assert res.fallback_reasons[0] is not None
    assert "exact_quadratic_failed" in res.fallback_reasons[0]
