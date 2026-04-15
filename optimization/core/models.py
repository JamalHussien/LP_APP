from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Literal, Optional, Dict
from .interfaces import ProblemKind

Sense = Literal["maximize", "minimize"]
Ineq = Literal["<=", ">=", "="]


@dataclass
class Constraint:
    a: List[float]
    sense: Ineq
    b: float


@dataclass
class Objective:
    c: List[float]
    sense: Sense = "maximize"


@dataclass
class Bound:
    lower: Optional[float] = 0.0
    upper: Optional[float] = None


@dataclass
class ProblemSpec:
    kind: ProblemKind
    n: int
    objective: Objective
    constraints: List[Constraint] = field(default_factory=list)
    bounds: List[Bound] = field(default_factory=list)
    metadata: Dict[str, float] = field(default_factory=dict)

    def validate(self) -> None:
        if self.n <= 0:
            raise ValueError("Number of variables must be positive")
        if len(self.objective.c) != self.n:
            raise ValueError("Objective coefficients length must equal n")
        if any(len(c.a) != self.n for c in self.constraints):
            raise ValueError("All constraints must have n coefficients")
        if self.bounds and len(self.bounds) != self.n:
            raise ValueError("Bounds length must equal n when provided")


@dataclass
class Solution:
    x: List[float]
    objective: Optional[float]
    success: bool
    message: Optional[str] = None
