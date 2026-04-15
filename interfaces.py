"""Deprecated compatibility shims for legacy top-level imports.

The canonical backend interfaces now live under ``optimization.core``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from models import LPSolution, LPRequest


class ISolver(ABC):
    """Legacy adapter contract kept for compatibility."""

    @abstractmethod
    def solve(self, req: LPRequest) -> LPSolution:
        """Solve a legacy LP request and return a legacy solution DTO."""


class IRenderer(ABC):
    """Legacy adapter contract kept for compatibility."""

    @abstractmethod
    def render_graph(self, req: LPRequest, solution: LPSolution):
        """Render a graphical artifact for a legacy LP request."""
