from __future__ import annotations

from typing import Dict, Tuple
from .interfaces import SolverStrategy, Renderer, ProblemKind


class SolverRegistry:
    """Simple in-memory registry for solvers and renderers keyed by (problem kind, mode)."""

    def __init__(self) -> None:
        self._solvers: Dict[Tuple[str, str], SolverStrategy] = {}
        self._renderers: Dict[Tuple[str, str], Renderer] = {}

    def register_solver(self, kind: ProblemKind, mode: str, solver: SolverStrategy) -> None:
        self._solvers[(kind.value, mode)] = solver

    def register_renderer(self, kind: ProblemKind, mode: str, renderer: Renderer) -> None:
        self._renderers[(kind.value, mode)] = renderer

    def resolve_solver(self, kind: ProblemKind, mode: str) -> SolverStrategy:
        key = (kind.value, mode)
        if key not in self._solvers:
            raise KeyError(f"No solver registered for {key}")
        return self._solvers[key]

    def resolve_renderer(self, kind: ProblemKind, mode: str) -> Renderer:
        key = (kind.value, mode)
        if key not in self._renderers:
            raise KeyError(f"No renderer registered for {key}")
        return self._renderers[key]
