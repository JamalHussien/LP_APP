from __future__ import annotations

from functools import lru_cache

from optimization.app.golden_section_service import GoldenSectionApplicationService
from optimization.app.linear_service import LinearProgrammingService
from optimization.app.steepest_descent_service import SteepestDescentApplicationService
from optimization.core.registry import SolverRegistry
from optimization.core.interfaces import ProblemKind
from optimization.algorithms.linear.solver_scipy import LinearSciPySolver
from optimization.algorithms.linear.renderer_matplotlib import LinearMatplotlibRenderer


@lru_cache
def get_registry() -> SolverRegistry:
    """Return the registry for problem-spec-based algorithms such as LP."""

    registry = SolverRegistry()
    registry.register_solver(ProblemKind.LINEAR, "numerical", LinearSciPySolver())
    registry.register_solver(ProblemKind.LINEAR, "graphical", LinearSciPySolver())
    registry.register_renderer(ProblemKind.LINEAR, "graphical", LinearMatplotlibRenderer())
    return registry


@lru_cache
def get_linear_programming_service() -> LinearProgrammingService:
    """Return the LP application service wired to the shared solver registry."""

    return LinearProgrammingService(get_registry())


@lru_cache
def get_steepest_descent_service() -> SteepestDescentApplicationService:
    """Return the steepest descent application service."""

    return SteepestDescentApplicationService()


@lru_cache
def get_golden_section_service() -> GoldenSectionApplicationService:
    """Return the golden section search application service."""

    return GoldenSectionApplicationService()
