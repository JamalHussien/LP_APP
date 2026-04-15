from __future__ import annotations

from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator, model_validator

Sense = Literal["maximize", "minimize"]
Ineq = Literal["<=", ">=", "="]
Mode = Literal["numerical", "graphical"]
ProblemKind = Literal["linear", "integer", "network_flow"]


class ConstraintDTO(BaseModel):
    a: List[float] = Field(min_length=1)
    sense: Ineq
    b: float

    @model_validator(mode="before")
    @classmethod
    def _accept_legacy_keys(cls, values):
        if not isinstance(values, dict):
            return values
        if "coefficients" in values and "a" not in values:
            values["a"] = values.pop("coefficients")
        if "type" in values and "sense" not in values:
            values["sense"] = values.pop("type")
        if "rhs" in values and "b" not in values:
            values["b"] = values.pop("rhs")
        return values


class SolveRequest(BaseModel):
    mode: Mode = "numerical"
    kind: ProblemKind = "linear"
    n: int = 2
    c: List[float] = Field(min_length=1)
    sense: Sense = "maximize"
    constraints: List[ConstraintDTO] = Field(default_factory=list)
    nonneg: bool = True

    @field_validator("constraints")
    @classmethod
    def validate_constraint_length(cls, v, info):
        n = info.data.get("n")
        if n and any(len(c.a) != n for c in v):
            raise ValueError("All constraint coefficients must match n variables")
        return v


class SolveResponse(BaseModel):
    x: List[float]
    objective: Optional[float]
    success: bool
    message: Optional[str] = None


class SteepestDescentRequest(BaseModel):
    expression: Optional[str] = None
    n: Optional[int] = None
    A: Optional[List[List[float]]] = None
    b: Optional[List[float]] = None
    c: float = 0.0
    start: List[float] = Field(min_length=1)
    sense: Sense = "minimize"
    mode: Literal["constant", "optimal"] = "constant"
    alpha: float = 0.1
    max_iters: int = 200
    grad_tol: float = 1e-6
    delta_f_tol: float = 1e-8

    @field_validator("A")
    @classmethod
    def check_matrix(cls, v, info):
        n = info.data.get("n")
        if v is None:
            return v
        if n and (len(v) != n or any(len(row) != n for row in v)):
            raise ValueError("A must be n x n")
        return v

    @field_validator("b")
    @classmethod
    def check_b(cls, v, info):
        n = info.data.get("n")
        if v is None:
            return v
        if n and len(v) != n:
            raise ValueError("b must length n")
        return v


class SteepestDescentResponse(BaseModel):
    points: List[List[float]]
    f_values: List[float]
    grad_norms: List[float]
    grads: List[List[float]]
    alphas: List[float]
    step_modes: List[str] = Field(default_factory=list)
    fallback_reasons: List[Optional[str]] = Field(default_factory=list)
    success: bool
    message: str
    plot: Optional[dict] = None
    variables: List[str] = Field(default_factory=list)


class GoldenSectionRequest(BaseModel):
    expression: str = Field(min_length=1)
    a: float
    b: float
    sense: Sense = "minimize"
    epsilon: float = 1e-5
    max_iters: int = 100

    @model_validator(mode="after")
    def validate_bounds(self):
        if self.a >= self.b:
            raise ValueError("Lower bound a must be less than upper bound b.")
        return self

    @field_validator("epsilon")
    @classmethod
    def validate_epsilon(cls, v: float):
        if v <= 0:
            raise ValueError("epsilon must be positive.")
        return v

    @field_validator("max_iters")
    @classmethod
    def validate_max_iters(cls, v: int):
        if v <= 0:
            raise ValueError("max_iters must be positive.")
        return v


class GoldenSectionIterationResponse(BaseModel):
    iteration: int
    xl: float
    xu: float
    x1: float
    x2: float
    fx1: float
    fx2: float
    intervalWidth: float
    currentBestX: float
    currentBestFx: float


class GoldenSectionResponse(BaseModel):
    x_star: float
    fx_star: float
    iterations: int
    termination_reason: str
    history: List[GoldenSectionIterationResponse]
    success: bool
    plot: Optional[dict] = None
    variable: Optional[str] = None
