from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Callable, List, Literal

import numpy as np


OptimizationSense = Literal["minimize", "maximize"]


@dataclass
class GoldenSectionIteration:
    iteration: int
    xl: float
    xu: float
    x1: float
    x2: float
    fx1: float
    fx2: float
    interval_width: float
    current_best_x: float
    current_best_fx: float


@dataclass
class GoldenSectionResult:
    x_star: float
    fx_star: float
    iterations: int
    termination_reason: str
    history: List[GoldenSectionIteration]
    success: bool


class GoldenSectionSearchSolver:
    phi = (sqrt(5.0) - 1.0) / 2.0

    def __init__(self, objective: Callable[[float], float]):
        self.objective = objective

    def _evaluate(self, x: float) -> float:
        try:
            value = float(self.objective(float(x)))
        except Exception as exc:
            raise ValueError(f"Objective evaluation failed at x={x}: {exc}") from exc
        if not np.isfinite(value):
            raise ValueError(f"Objective evaluated to a non-finite value at x={x}: {value}")
        return value

    @staticmethod
    def _x1_is_better(fx1: float, fx2: float, sense: OptimizationSense) -> bool:
        if sense == "maximize":
            return fx1 >= fx2
        return fx1 <= fx2

    @staticmethod
    def _pick_best(x1: float, fx1: float, x2: float, fx2: float, sense: OptimizationSense) -> tuple[float, float]:
        if GoldenSectionSearchSolver._x1_is_better(fx1, fx2, sense):
            return x1, fx1
        return x2, fx2

    @classmethod
    def _distance(cls, xl: float, xu: float) -> float:
        return cls.phi * (xu - xl)

    def _make_iteration(
        self,
        iteration: int,
        xl: float,
        xu: float,
        x1: float,
        x2: float,
        fx1: float,
        fx2: float,
        sense: OptimizationSense,
    ) -> GoldenSectionIteration:
        best_x, best_fx = self._pick_best(x1, fx1, x2, fx2, sense)
        return GoldenSectionIteration(
            iteration=iteration,
            xl=xl,
            xu=xu,
            x1=x1,
            x2=x2,
            fx1=fx1,
            fx2=fx2,
            interval_width=xu - xl,
            current_best_x=best_x,
            current_best_fx=best_fx,
        )

    def solve(
        self,
        a: float,
        b: float,
        epsilon: float = 1e-5,
        max_iters: int = 100,
        sense: OptimizationSense = "minimize",
    ) -> GoldenSectionResult:
        if not np.isfinite(a) or not np.isfinite(b):
            raise ValueError("Bounds a and b must be finite numbers.")
        if a >= b:
            raise ValueError("Lower bound a must be less than upper bound b.")
        if not np.isfinite(epsilon) or epsilon <= 0.0:
            raise ValueError("Tolerance epsilon must be a positive finite number.")
        if max_iters <= 0:
            raise ValueError("max_iters must be a positive integer.")

        xl = float(a)
        xu = float(b)
        d = self._distance(xl, xu)
        x1 = xl + d
        x2 = xu - d
        fx1 = self._evaluate(x1)
        fx2 = self._evaluate(x2)
        history: List[GoldenSectionIteration] = [
            self._make_iteration(
                iteration=0,
                xl=xl,
                xu=xu,
                x1=x1,
                x2=x2,
                fx1=fx1,
                fx2=fx2,
                sense=sense,
            )
        ]

        if history[0].interval_width < epsilon:
            return GoldenSectionResult(
                x_star=history[0].current_best_x,
                fx_star=history[0].current_best_fx,
                iterations=0,
                termination_reason="Interval width below tolerance.",
                history=history,
                success=True,
            )

        for iteration in range(1, max_iters + 1):
            if self._x1_is_better(fx1, fx2, sense):
                xl = x2
                x2 = x1
                fx2 = fx1
                d = self._distance(xl, xu)
                x1 = xl + d
                fx1 = self._evaluate(x1)
            else:
                xu = x1
                x1 = x2
                fx1 = fx2
                d = self._distance(xl, xu)
                x2 = xu - d
                fx2 = self._evaluate(x2)

            history.append(
                self._make_iteration(
                    iteration=iteration,
                    xl=xl,
                    xu=xu,
                    x1=x1,
                    x2=x2,
                    fx1=fx1,
                    fx2=fx2,
                    sense=sense,
                )
            )

            if history[-1].interval_width < epsilon:
                return GoldenSectionResult(
                    x_star=history[-1].current_best_x,
                    fx_star=history[-1].current_best_fx,
                    iterations=iteration,
                    termination_reason="Interval width below tolerance.",
                    history=history,
                    success=True,
                )

        return GoldenSectionResult(
            x_star=history[-1].current_best_x,
            fx_star=history[-1].current_best_fx,
            iterations=max_iters,
            termination_reason="Maximum iterations reached.",
            history=history,
            success=False,
        )
