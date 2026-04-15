from __future__ import annotations

import re
from pathlib import Path

from optimization.app.di import get_registry
from optimization.app.dto import GoldenSectionRequest, SolveRequest, SteepestDescentRequest
from optimization.app.golden_section_service import GoldenSectionApplicationService
from optimization.app.linear_service import LinearProgrammingService
from optimization.app.mappers import dto_to_golden_section_command, dto_to_linear_command, dto_to_sd_command
from optimization.app.steepest_descent_service import SteepestDescentApplicationService


def test_linear_programming_service_solves_numerical_problem():
    service = LinearProgrammingService(get_registry())
    command = dto_to_linear_command(
        SolveRequest(
            mode="numerical",
            kind="linear",
            n=2,
            c=[3, 5],
            sense="maximize",
            constraints=[
                {"a": [1, 0], "sense": "<=", "b": 4},
                {"a": [0, 2], "sense": "<=", "b": 12},
                {"a": [3, 2], "sense": "<=", "b": 18},
            ],
            nonneg=True,
        )
    )

    result = service.execute(command)

    assert result.solution.success is True
    assert result.artifact is None
    assert len(result.solution.x) == 2


def test_steepest_descent_service_returns_variables_and_plot():
    service = SteepestDescentApplicationService()
    command = dto_to_sd_command(
        SteepestDescentRequest(
            expression="x^2 + y^2",
            start=[1, 1],
            sense="minimize",
            mode="constant",
            alpha=0.1,
            max_iters=20,
        )
    )

    report = service.execute(command)

    assert report.variables == ["x", "y"]
    assert report.result.points[0] == [1.0, 1.0]
    assert "data" in report.plot


def test_steepest_descent_command_defaults_to_minimize():
    command = dto_to_sd_command(
        SteepestDescentRequest(
            expression="x^2",
            start=[1],
            mode="constant",
            alpha=0.1,
        )
    )

    assert command.sense == "minimize"


def test_golden_section_service_returns_variable_and_plot():
    service = GoldenSectionApplicationService()
    command = dto_to_golden_section_command(
        GoldenSectionRequest(
            expression="(x - 2)^2",
            a=0,
            b=5,
            sense="minimize",
            epsilon=1e-5,
            max_iters=50,
        )
    )

    report = service.execute(command)

    assert report.variable == "x"
    assert abs(report.result.x_star - 2.0) < 1e-3
    assert "data" in report.plot


def test_internal_backend_modules_do_not_import_legacy_root_modules():
    forbidden_patterns = [
        re.compile(r"^\s*from\s+models\s+import\s+", re.MULTILINE),
        re.compile(r"^\s*import\s+models\b", re.MULTILINE),
        re.compile(r"^\s*from\s+interfaces\s+import\s+", re.MULTILINE),
        re.compile(r"^\s*import\s+interfaces\b", re.MULTILINE),
        re.compile(r"^\s*from\s+solvers\s+import\s+", re.MULTILINE),
        re.compile(r"^\s*import\s+solvers\b", re.MULTILINE),
        re.compile(r"^\s*from\s+renderers\s+import\s+", re.MULTILINE),
        re.compile(r"^\s*import\s+renderers\b", re.MULTILINE),
    ]

    for path in Path("optimization").rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        for pattern in forbidden_patterns:
            assert not pattern.search(source), f"Legacy import found in {path}: {pattern.pattern}"
