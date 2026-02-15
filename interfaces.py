from abc import ABC, abstractmethod
from typing import Any
from models import LPRequest, LPSolution

class ISolver(ABC):
    @abstractmethod
    def solve(self, req: LPRequest) -> LPSolution:
        """Solve an LP request and return solution DTO"""

class IRenderer(ABC):
    @abstractmethod
    def render_graph(self, req: LPRequest, solution: LPSolution) -> bytes:
        """Return image bytes (PNG) for graphical mode"""
