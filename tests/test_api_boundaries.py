from __future__ import annotations

from fastapi.testclient import TestClient

from optimization.algorithms.gradient.steepest_descent import SteepestDescentResult
from optimization.algorithms.search.golden_section import GoldenSectionIteration, GoldenSectionResult
from optimization.app.api import create_app
from optimization.app.contracts import GoldenSectionReport, LinearSolveResult, SteepestDescentReport
from optimization.app.di import (
    get_golden_section_service,
    get_linear_programming_service,
    get_steepest_descent_service,
)
from optimization.app.exceptions import FeatureUnavailableError, InputError
from optimization.core.models import Solution


class RecordingLinearService:
    def __init__(self):
        self.command = None

    def execute(self, command):
        self.command = command
        return LinearSolveResult(
            solution=Solution(x=[1.0, 2.0], objective=11.0, success=True, message="ok"),
            artifact=None,
        )


class RecordingSteepestDescentService:
    def __init__(self):
        self.command = None

    def execute(self, command):
        self.command = command
        return SteepestDescentReport(
            result=SteepestDescentResult(
                points=[[0.0], [0.5]],
                f_values=[1.0, 0.25],
                grad_norms=[2.0, 1.0],
                grads=[[2.0], [1.0]],
                alphas=[0.25],
                step_modes=["constant"],
                fallback_reasons=[None],
                success=True,
                message="ok",
                iterations=1,
            ),
            variables=["x"],
            plot={"data": [], "layout": {}},
        )


def test_solve_endpoint_delegates_to_linear_service():
    app = create_app()
    service = RecordingLinearService()
    app.dependency_overrides[get_linear_programming_service] = lambda: service
    client = TestClient(app)

    payload = {
        "mode": "numerical",
        "kind": "linear",
        "n": 2,
        "c": [1, 1],
        "sense": "maximize",
        "constraints": [],
        "nonneg": True,
    }
    res = client.post("/solve", json=payload)

    assert res.status_code == 200
    assert res.json()["success"] is True
    assert service.command is not None
    assert service.command.mode == "numerical"
    assert service.command.problem.n == 2


def test_sd_endpoint_delegates_to_service():
    app = create_app()
    service = RecordingSteepestDescentService()
    app.dependency_overrides[get_steepest_descent_service] = lambda: service
    client = TestClient(app)

    payload = {
        "expression": "x^2",
        "start": [0],
        "sense": "maximize",
        "mode": "constant",
        "alpha": 0.1,
        "max_iters": 5,
        "grad_tol": 1e-6,
        "delta_f_tol": 1e-8,
    }
    res = client.post("/optimize/steepest-descent", json=payload)

    assert res.status_code == 200
    assert res.json()["variables"] == ["x"]
    assert service.command is not None
    assert service.command.expression == "x^2"
    assert service.command.sense == "maximize"


def test_sd_endpoint_defaults_to_minimize_when_sense_is_omitted():
    app = create_app()
    service = RecordingSteepestDescentService()
    app.dependency_overrides[get_steepest_descent_service] = lambda: service
    client = TestClient(app)

    payload = {
        "expression": "x^2",
        "start": [0],
        "mode": "constant",
        "alpha": 0.1,
        "max_iters": 5,
        "grad_tol": 1e-6,
        "delta_f_tol": 1e-8,
    }
    res = client.post("/optimize/steepest-descent", json=payload)

    assert res.status_code == 200
    assert service.command is not None
    assert service.command.sense == "minimize"


def test_api_maps_input_errors_to_400():
    app = create_app()

    class FailingGoldenSectionService:
        def execute(self, command):
            raise InputError("bad interval")

    app.dependency_overrides[get_golden_section_service] = lambda: FailingGoldenSectionService()
    client = TestClient(app)

    payload = {
        "expression": "(x - 2)^2",
        "a": 0,
        "b": 5,
        "sense": "minimize",
        "epsilon": 1e-5,
        "max_iters": 10,
    }
    res = client.post("/optimize/golden-section", json=payload)

    assert res.status_code == 400
    assert res.json()["detail"] == "bad interval"


def test_api_maps_feature_unavailable_errors_to_501():
    app = create_app()

    class FailingLinearService:
        def execute(self, command):
            raise FeatureUnavailableError("solver unavailable")

    app.dependency_overrides[get_linear_programming_service] = lambda: FailingLinearService()
    client = TestClient(app)

    payload = {
        "mode": "numerical",
        "kind": "linear",
        "n": 2,
        "c": [1, 1],
        "sense": "maximize",
        "constraints": [],
        "nonneg": True,
    }
    res = client.post("/solve", json=payload)

    assert res.status_code == 501
    assert res.json()["detail"] == "solver unavailable"


def test_golden_section_response_mapping_stays_thin():
    app = create_app()

    class RecordingGoldenSectionService:
        def __init__(self):
            self.command = None

        def execute(self, command):
            self.command = command
            return GoldenSectionReport(
                result=GoldenSectionResult(
                    x_star=2.0,
                    fx_star=0.0,
                    iterations=1,
                    termination_reason="Interval width below tolerance.",
                    history=[
                        GoldenSectionIteration(
                            iteration=0,
                            xl=0.0,
                            xu=5.0,
                            x1=3.0901699437494745,
                            x2=1.9098300562505255,
                            fx1=1.1884705062547325,
                            fx2=0.008130618755783399,
                            interval_width=5.0,
                            current_best_x=1.9098300562505255,
                            current_best_fx=0.008130618755783399,
                        )
                    ],
                    success=True,
                ),
                variable="x",
                plot={"data": [], "layout": {}},
            )

    service = RecordingGoldenSectionService()
    app.dependency_overrides[get_golden_section_service] = lambda: service
    client = TestClient(app)

    payload = {
        "expression": "(x - 2)^2",
        "a": 0,
        "b": 5,
        "sense": "minimize",
        "epsilon": 1e-5,
        "max_iters": 10,
    }
    res = client.post("/optimize/golden-section", json=payload)

    assert res.status_code == 200
    assert res.json()["variable"] == "x"
    assert service.command is not None
    assert service.command.expression == "(x - 2)^2"
