"""Deprecated compatibility shim for the legacy top-level renderer module."""

from __future__ import annotations

from optimization.algorithms.linear.renderer_matplotlib import LinearMatplotlibRenderer
from optimization.app.mappers import dto_to_problem
from optimization.core.models import Solution
from models import LPSolution, LPRequest


class MatplotlibRenderer:
    """Legacy adapter that forwards to the canonical LP renderer implementation."""

    def __init__(self) -> None:
        self._renderer = LinearMatplotlibRenderer()

    def render_graph(self, req: LPRequest, solution: LPSolution):
        core_solution = Solution(
            x=solution.x,
            objective=solution.objective,
            success=solution.success,
            message=solution.message,
        )
        return self._renderer.render(dto_to_problem(req), core_solution)
