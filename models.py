"""Deprecated compatibility shims for legacy top-level DTO imports.

The canonical request/response models now live under ``optimization.app.dto``.
"""

from optimization.app.dto import ConstraintDTO as Constraint
from optimization.app.dto import GoldenSectionRequest, GoldenSectionResponse
from optimization.app.dto import SolveRequest as LPRequest
from optimization.app.dto import SolveResponse as LPSolution
from optimization.app.dto import SteepestDescentRequest, SteepestDescentResponse

__all__ = [
    "Constraint",
    "GoldenSectionRequest",
    "GoldenSectionResponse",
    "LPRequest",
    "LPSolution",
    "SteepestDescentRequest",
    "SteepestDescentResponse",
]
