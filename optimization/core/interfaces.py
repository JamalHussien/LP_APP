from __future__ import annotations

from typing import Protocol, Any
from dataclasses import dataclass
from enum import Enum


class ProblemKind(str, Enum):
    LINEAR = "linear"
    INTEGER = "integer"
    NETWORK_FLOW = "network_flow"


class SolverStrategy(Protocol):
    """Algorithm contract: solve a problem spec and return a solution."""

    def solve(self, problem: "ProblemSpec") -> "Solution":
        ...


class Renderer(Protocol):
    """Optional rendering contract: produce an artifact (bytes or (bytes, mime))."""

    def render(self, problem: "ProblemSpec", solution: "Solution") -> "RenderArtifact":
        ...


@dataclass
class RenderArtifact:
    payload: bytes
    media_type: str = "application/octet-stream"
