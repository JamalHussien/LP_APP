from __future__ import annotations

from typing import Optional, Tuple
from optimization.core.errors import ValidationError, SolverError, RendererError
from optimization.core.interfaces import SolverStrategy, Renderer
from optimization.core.models import ProblemSpec, Solution


class SolveService:
    """Small orchestration helper for registry-backed problem specs.

    This service validates the problem, invokes the selected solver, and
    optionally invokes a renderer. It intentionally does not know about HTTP,
    request DTOs, symbolic parsing, or UI-specific payloads.
    """

    def __init__(self, solver: SolverStrategy, renderer: Optional[Renderer] = None):
        self.solver = solver
        self.renderer = renderer

    def solve(self, problem: ProblemSpec, render: bool = False) -> Tuple[Solution, Optional[Tuple[bytes, str]]]:
        try:
            problem.validate()
        except Exception as exc:
            raise ValidationError(str(exc)) from exc

        try:
            solution = self.solver.solve(problem)
        except Exception as exc:  # solver backends may throw many exceptions
            raise SolverError(str(exc)) from exc

        artifact = None
        if render:
            if not self.renderer:
                raise RendererError("No renderer available for graphical mode")
            try:
                art = self.renderer.render(problem, solution)
                if isinstance(art, tuple):
                    artifact = art
                else:
                    artifact = (art.payload, art.media_type)
            except Exception as exc:
                raise RendererError(str(exc)) from exc
        return solution, artifact
