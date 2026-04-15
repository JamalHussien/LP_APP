"""Deprecated compatibility shim for the legacy top-level solver module."""

from __future__ import annotations

from optimization.algorithms.linear.solver_scipy import LinearSciPySolver
from optimization.app.mappers import dto_to_problem, solution_to_dto
from models import LPRequest, LPSolution


class SciPySolver:
    """Legacy adapter that forwards to the canonical LP solver implementation."""

    def __init__(self) -> None:
        self._solver = LinearSciPySolver()

    def solve(self, req: LPRequest) -> LPSolution:
        solution = self._solver.solve(dto_to_problem(req))
        return solution_to_dto(solution)
