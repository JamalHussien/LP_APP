import math

from optimization.algorithms.search.golden_section import GoldenSectionSearchSolver


def test_golden_section_minimize_quadratic():
    solver = GoldenSectionSearchSolver(lambda x: (x - 2.0) ** 2)
    result = solver.solve(0.0, 5.0, epsilon=1e-5, max_iters=200, sense="minimize")

    assert result.success is True
    assert abs(result.x_star - 2.0) < 1e-3
    assert result.fx_star < 1e-5
    assert result.history
    assert result.history[0].iteration == 0
    assert len(result.history) == result.iterations + 1
    assert result.history[-1].interval_width < 1e-5


def test_golden_section_initial_snapshot_uses_requested_x1_x2_definition():
    solver = GoldenSectionSearchSolver(lambda x: (x - 2.0) ** 2)
    result = solver.solve(0.0, 5.0, epsilon=1e-5, max_iters=1, sense="minimize")

    first = result.history[0]
    d = solver.phi * (first.xu - first.xl)
    assert first.iteration == 0
    assert abs(first.x1 - (first.xl + d)) < 1e-12
    assert abs(first.x2 - (first.xu - d)) < 1e-12
    assert first.x1 > first.x2


def test_golden_section_matches_requested_d_example_on_zero_to_two():
    f = lambda x: x**4 - 14 * x**3 + 60 * x**2 - 70 * x
    solver = GoldenSectionSearchSolver(f)
    result = solver.solve(0.0, 2.0, epsilon=1e-5, max_iters=1, sense="minimize")

    first = result.history[0]
    assert abs(solver._distance(first.xl, first.xu) - 1.2360679774997898) < 1e-12
    assert abs(first.x1 - 1.2360679774997898) < 1e-12
    assert abs(first.x2 - 0.7639320225002102) < 1e-12


def test_golden_section_maximize_concave_quadratic():
    solver = GoldenSectionSearchSolver(lambda x: -((x - 3.0) ** 2) + 5.0)
    result = solver.solve(0.0, 6.0, epsilon=1e-5, max_iters=200, sense="maximize")

    assert result.success is True
    assert abs(result.x_star - 3.0) < 1e-3
    assert abs(result.fx_star - 5.0) < 1e-4


def test_golden_section_history_shrinks_interval():
    solver = GoldenSectionSearchSolver(lambda x: (x - 1.5) ** 2 + 1.0)
    result = solver.solve(0.0, 4.0, epsilon=1e-4, max_iters=50, sense="minimize")

    widths = [step.interval_width for step in result.history]
    assert widths == sorted(widths, reverse=True)
    assert len(result.history) == result.iterations + 1
    assert all(step.xl < step.xu for step in result.history)
    assert all(math.isfinite(step.current_best_fx) for step in result.history)


def test_golden_section_returns_k0_even_when_interval_already_within_tolerance():
    solver = GoldenSectionSearchSolver(lambda x: (x - 2.0) ** 2)
    result = solver.solve(0.0, 1.0, epsilon=2.0, max_iters=50, sense="minimize")

    assert result.success is True
    assert result.iterations == 0
    assert len(result.history) == 1
    assert result.history[0].iteration == 0
    assert result.history[0].interval_width == 1.0


def test_golden_section_rejects_invalid_interval():
    solver = GoldenSectionSearchSolver(lambda x: x**2)
    try:
        solver.solve(3.0, 1.0)
        assert False, "Expected invalid interval to raise"
    except ValueError as exc:
        assert "Lower bound a must be less than upper bound b" in str(exc)


def test_golden_section_surfaces_evaluation_errors():
    solver = GoldenSectionSearchSolver(lambda x: float("nan"))
    try:
        solver.solve(0.0, 1.0)
        assert False, "Expected evaluation failure to raise"
    except ValueError as exc:
        assert "non-finite" in str(exc)
