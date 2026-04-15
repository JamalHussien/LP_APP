"""Application service for registry-backed linear programming solves."""

from __future__ import annotations

from optimization.app.contracts import LinearSolveCommand, LinearSolveResult
from optimization.app.exceptions import ComputationError, FeatureUnavailableError, InputError, PresentationError
from optimization.app.service import SolveService
from optimization.core.errors import RendererError, SolverError, ValidationError
from optimization.core.registry import SolverRegistry


class LinearProgrammingService:
    """Coordinates registry-backed LP solving without HTTP or DTO concerns."""

    def __init__(self, registry: SolverRegistry):
        self.registry = registry

    def execute(self, command: LinearSolveCommand) -> LinearSolveResult:
        if command.mode == "graphical" and command.problem.n not in (2, 3):
            raise InputError("Graphical mode supports 2 or 3 variables")

        try:
            solver = self.registry.resolve_solver(command.problem.kind, command.mode)
        except KeyError as exc:
            raise FeatureUnavailableError(str(exc)) from exc

        renderer = None
        if command.mode == "graphical":
            try:
                renderer = self.registry.resolve_renderer(command.problem.kind, command.mode)
            except KeyError:
                renderer = None

        service = SolveService(solver, renderer)
        try:
            solution, artifact = service.solve(command.problem, render=command.mode == "graphical")
        except ValidationError as exc:
            raise InputError(str(exc)) from exc
        except SolverError as exc:
            raise ComputationError(str(exc)) from exc
        except RendererError as exc:
            raise PresentationError(str(exc)) from exc

        return LinearSolveResult(solution=solution, artifact=artifact)
