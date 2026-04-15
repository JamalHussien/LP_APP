"""Internal command and report types used by application services."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Literal, Optional

from optimization.algorithms.gradient.steepest_descent import SteepestDescentResult
from optimization.algorithms.search.golden_section import GoldenSectionResult
from optimization.core.models import ProblemSpec, Solution


RenderMode = Literal["numerical", "graphical"]
StepMode = Literal["constant", "optimal"]
OptimizationSense = Literal["minimize", "maximize"]


@dataclass(frozen=True)
class LinearSolveCommand:
    problem: ProblemSpec
    mode: RenderMode


@dataclass(frozen=True)
class LinearSolveResult:
    solution: Solution
    artifact: Optional[tuple[bytes, str]]


@dataclass(frozen=True)
class SteepestDescentCommand:
    expression: Optional[str]
    n: Optional[int]
    A: Optional[List[List[float]]]
    b: Optional[List[float]]
    c: float
    start: List[float]
    sense: OptimizationSense
    mode: StepMode
    alpha: float
    max_iters: int
    grad_tol: float
    delta_f_tol: float


@dataclass(frozen=True)
class SteepestDescentReport:
    result: SteepestDescentResult
    variables: List[str]
    plot: dict[str, Any]


@dataclass(frozen=True)
class GoldenSectionCommand:
    expression: str
    a: float
    b: float
    sense: OptimizationSense
    epsilon: float
    max_iters: int


@dataclass(frozen=True)
class GoldenSectionReport:
    result: GoldenSectionResult
    variable: str
    plot: dict[str, Any]
