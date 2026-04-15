from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Literal, Optional, Protocol

import numpy as np
from scipy.optimize import minimize_scalar

from .objective import ObjectiveFunction


OptimizationSense = Literal["minimize", "maximize"]


@dataclass
class SteepestDescentResult:
    points: List[List[float]]
    f_values: List[float]
    grad_norms: List[float]
    grads: List[List[float]]
    alphas: List[float]
    step_modes: List[str]
    fallback_reasons: List[Optional[str]]
    success: bool
    message: str
    iterations: int


@dataclass
class StepComputationResult:
    alpha: float
    mode: str
    fallback_reason: Optional[str] = None


class StepSizeStrategy(Protocol):
    mode_name: str

    def __call__(
        self,
        x: np.ndarray,
        g: np.ndarray,
        f: Callable[[np.ndarray], float],
        sense: OptimizationSense,
    ) -> StepComputationResult: ...


def search_direction(g: np.ndarray, sense: OptimizationSense) -> np.ndarray:
    return -g if sense == "minimize" else g


class ConstantStep:
    mode_name = "constant"

    def __init__(self, alpha: float):
        self.alpha = alpha

    def __call__(
        self,
        x: np.ndarray,
        g: np.ndarray,
        f: Callable[[np.ndarray], float],
        sense: OptimizationSense,
    ) -> StepComputationResult:
        return StepComputationResult(float(self.alpha), self.mode_name)


class ExactQuadraticStep:
    """Closed-form optimal step for quadratic along the sense-aware gradient direction."""

    mode_name = "exact_quadratic"

    def __init__(self, A: np.ndarray, eps: float = 1e-12):
        self.A = A
        self.eps = eps

    def __call__(
        self,
        x: np.ndarray,
        g: np.ndarray,
        f: Callable[[np.ndarray], float],
        sense: OptimizationSense,
    ) -> StepComputationResult:
        denom = float(g @ (self.A @ g))
        numer = float(g @ g)
        if sense == "minimize":
            if denom <= self.eps:
                raise ValueError(f"incompatible_quadratic_curvature_for_minimize: gTAg={denom}")
            alpha_exact = numer / denom
        else:
            if denom >= -self.eps:
                raise ValueError(f"incompatible_quadratic_curvature_for_maximize: gTAg={denom}")
            alpha_exact = -numer / denom
        if not np.isfinite(alpha_exact) or alpha_exact < 0.0:
            raise ValueError(f"invalid_quadratic_alpha: alpha={alpha_exact}")
        return StepComputationResult(float(alpha_exact), self.mode_name)


class ExactLineSearch1D:
    """Exact (1-D) line search using adaptive bracketing on a sense-aware merit function."""

    mode_name = "exact_line"

    def __init__(
        self,
        alpha0: float = 1.0,
        expansion: float = 2.0,
        shrink: float = 0.5,
        min_alpha: float = 1e-12,
        max_bracket_expansions: int = 20,
        max_shrinks: int = 25,
        tol: float = 1e-5,
        max_iter: int = 100,
    ):
        self.alpha0 = alpha0
        self.expansion = expansion
        self.shrink = shrink
        self.min_alpha = min_alpha
        self.max_bracket_expansions = max_bracket_expansions
        self.max_shrinks = max_shrinks
        self.tol = tol
        self.max_iter = max_iter

    def _bounded_minimize(self, phi: Callable[[float], float], lower: float, upper: float) -> StepComputationResult:
        if not np.isfinite(lower) or not np.isfinite(upper) or upper <= lower:
            raise ValueError(f"invalid_bracket: lower={lower}, upper={upper}")
        try:
            res = minimize_scalar(
                phi,
                bounds=(lower, upper),
                method="bounded",
                options={"xatol": self.tol, "maxiter": self.max_iter},
            )
        except Exception as exc:
            raise ValueError(f"line_search_failed: {exc}") from exc

        if not res.success or not np.isfinite(res.x) or not np.isfinite(res.fun):
            raise ValueError(f"line_search_failed: success={res.success}, alpha={res.x}, f={res.fun}")

        return StepComputationResult(float(res.x), self.mode_name)

    def _recover_finite_upper(
        self,
        phi: Callable[[float], float],
        lower: float,
        upper: float,
    ) -> Optional[tuple[float, float]]:
        candidate = upper
        for _ in range(self.max_shrinks):
            candidate = 0.5 * (lower + candidate)
            value = phi(candidate)
            if np.isfinite(value):
                return float(candidate), float(value)
        return None

    def __call__(
        self,
        x: np.ndarray,
        g: np.ndarray,
        f: Callable[[np.ndarray], float],
        sense: OptimizationSense,
    ) -> StepComputationResult:
        direction = search_direction(g, sense)

        def objective_along(a: float) -> float:
            return float(f(x + a * direction))

        def merit(a: float) -> float:
            value = objective_along(a)
            return value if sense == "minimize" else -value

        merit0 = merit(0.0)
        if not np.isfinite(merit0):
            raise ValueError("nonfinite_at_origin")

        alpha_mid = float(self.alpha0)
        merit_mid = merit(alpha_mid)
        shrink_count = 0
        while not np.isfinite(merit_mid) and shrink_count < self.max_shrinks:
            alpha_mid *= self.shrink
            if alpha_mid < self.min_alpha:
                break
            merit_mid = merit(alpha_mid)
            shrink_count += 1

        if not np.isfinite(merit_mid):
            raise ValueError(f"finite_trial_not_found_from_alpha0={self.alpha0}")

        if merit_mid >= merit0:
            return self._bounded_minimize(merit, 0.0, alpha_mid)

        alpha_left = 0.0
        alpha_curr = alpha_mid
        merit_curr = merit_mid
        for _ in range(self.max_bracket_expansions):
            alpha_right = alpha_curr * self.expansion
            merit_right = merit(alpha_right)
            if not np.isfinite(merit_right):
                recovered = self._recover_finite_upper(merit, alpha_curr, alpha_right)
                if recovered is None:
                    raise ValueError(f"finite_upper_bound_not_found: lower={alpha_curr}, upper={alpha_right}")
                alpha_right, merit_right = recovered
            if merit_right >= merit_curr:
                return self._bounded_minimize(merit, alpha_left, alpha_right)
            alpha_left = alpha_curr
            alpha_curr = alpha_right
            merit_curr = merit_right

        raise ValueError(f"bracket_not_found_after_{self.max_bracket_expansions}_expansions")


class BacktrackingLineSearch:
    mode_name = "backtracking"

    def __init__(
        self,
        alpha0: float = 1.0,
        rho: float = 0.5,
        c: float = 1e-4,
        min_alpha: float = 1e-12,
        max_step_norm: float = 1.0,
        max_backtracks: int = 50,
    ):
        self.alpha0 = alpha0
        self.rho = rho
        self.c = c
        self.min_alpha = min_alpha
        self.max_step_norm = max_step_norm
        self.max_backtracks = max_backtracks

    def __call__(
        self,
        x: np.ndarray,
        g: np.ndarray,
        f: Callable[[np.ndarray], float],
        sense: OptimizationSense,
    ) -> StepComputationResult:
        alpha = self.alpha0
        fx = f(x)
        direction = search_direction(g, sense)
        predicted_change = float(g @ direction)
        g_norm = np.linalg.norm(g)
        for _ in range(self.max_backtracks):
            if g_norm > 0 and alpha * g_norm > self.max_step_norm:
                alpha *= self.rho
                if alpha < self.min_alpha:
                    break
                continue
            x_trial = x + alpha * direction
            f_trial = f(x_trial)
            if not np.isfinite(f_trial):
                alpha *= self.rho
                if alpha < self.min_alpha:
                    break
                continue
            armijo_bound = fx + self.c * alpha * predicted_change
            if sense == "minimize" and f_trial <= armijo_bound:
                return StepComputationResult(float(alpha), self.mode_name)
            if sense == "maximize" and f_trial >= armijo_bound:
                return StepComputationResult(float(alpha), self.mode_name)
            alpha *= self.rho
            if alpha < self.min_alpha:
                break
        return StepComputationResult(float(alpha), self.mode_name, "min_alpha_reached")


def backtracking_line_search(
    f: Callable[[np.ndarray], float],
    grad: Callable[[np.ndarray], np.ndarray],
    x: np.ndarray,
    alpha0: float = 1.0,
    rho: float = 0.5,
    c: float = 1e-4,
    sense: OptimizationSense = "minimize",
) -> float:
    """Deprecated wrapper maintained for backward compatibility."""

    return BacktrackingLineSearch(alpha0=alpha0, rho=rho, c=c)(x, grad(x), f, sense).alpha


def exact_line_search_quadratic(
    A: np.ndarray,
    g: np.ndarray,
    eps: float = 1e-12,
    sense: OptimizationSense = "minimize",
) -> float:
    """Deprecated wrapper maintained for backward compatibility."""

    return ExactQuadraticStep(A, eps)(np.zeros_like(g), g, lambda _: 0.0, sense).alpha


class SteepestDescentSolver:
    def __init__(self, objective: ObjectiveFunction):
        self.obj = objective

    @classmethod
    def from_functions(
        cls,
        f: Callable[[np.ndarray], float],
        grad: Callable[[np.ndarray], np.ndarray],
        A: Optional[np.ndarray] = None,
        is_quadratic: Optional[bool] = None,
    ) -> "SteepestDescentSolver":
        obj = ObjectiveFunction(
            f=f,
            grad=grad,
            is_quadratic=bool(is_quadratic) if is_quadratic is not None else A is not None,
            A=A,
        )
        return cls(obj)

    def solve(
        self,
        x0: List[float],
        mode: str = "constant",
        sense: OptimizationSense = "minimize",
        alpha: float = 0.1,
        max_iters: int = 200,
        grad_tol: float = 1e-6,
        delta_f_tol: float = 1e-8,
        max_step_norm: float = 1.0,
        iterate_norm_max: float = 1e6,
        f_value_max: float = 1e300,
    ) -> SteepestDescentResult:
        x = np.array(x0, dtype=float)
        f0 = float(self.obj.f(x))
        g0 = self.obj.grad(x)
        if not np.isfinite(f0) or not np.all(np.isfinite(g0)):
            return SteepestDescentResult(
                [x.tolist()],
                [f0],
                [float(np.linalg.norm(g0))],
                [g0.tolist()],
                [],
                [],
                [],
                False,
                "Objective or gradient is non-finite at start",
                0,
            )

        points = [x.tolist()]
        f_values = [f0]
        grad_norms = [float(np.linalg.norm(g0))]
        grads = [g0.tolist()]
        alphas: List[float] = []
        step_modes: List[str] = []
        fallback_reasons: List[Optional[str]] = []

        if mode == "constant":
            strategies: List[StepSizeStrategy] = [ConstantStep(alpha)]
            fallback_strategy: Optional[StepSizeStrategy] = None
        elif mode == "optimal":
            strategies = []
            if self.obj.is_quadratic and self.obj.A is not None:
                strategies.append(ExactQuadraticStep(self.obj.A))
            strategies.append(ExactLineSearch1D())
            fallback_strategy = BacktrackingLineSearch(alpha0=1.0, max_step_norm=max_step_norm)
        else:
            strategies = [BacktrackingLineSearch(alpha0=1.0, max_step_norm=max_step_norm)]
            fallback_strategy = None

        for k in range(max_iters):
            g = self.obj.grad(x)
            g_norm = np.linalg.norm(g)
            if g_norm < grad_tol:
                return SteepestDescentResult(points, f_values, grad_norms, grads, alphas, step_modes, fallback_reasons, True, "Gradient tolerance reached", k)
            if not np.isfinite(g_norm):
                return SteepestDescentResult(points, f_values, grad_norms, grads, alphas, step_modes, fallback_reasons, False, "Gradient became non-finite", k)
            if np.linalg.norm(x) > iterate_norm_max:
                return SteepestDescentResult(points, f_values, grad_norms, grads, alphas, step_modes, fallback_reasons, False, "Iterates diverged (norm too large)", k)
            if abs(f_values[-1]) > f_value_max:
                return SteepestDescentResult(points, f_values, grad_norms, grads, alphas, step_modes, fallback_reasons, False, "Objective magnitude too large (diverged)", k)

            step_result: Optional[StepComputationResult] = None
            strategy_failures: List[str] = []
            for strategy in strategies:
                try:
                    step_result = strategy(x, g, self.obj.f, sense)
                    break
                except Exception as exc:
                    if mode != "optimal":
                        return SteepestDescentResult(points, f_values, grad_norms, grads, alphas, step_modes, fallback_reasons, False, f"Step computation failed: {exc}", k)
                    strategy_failures.append(f"{strategy.mode_name}_failed: {exc}")

            if step_result is None:
                if fallback_strategy is None:
                    return SteepestDescentResult(points, f_values, grad_norms, grads, alphas, step_modes, fallback_reasons, False, "Step computation failed", k)
                step_result = fallback_strategy(x, g, self.obj.f, sense)

            if strategy_failures:
                if step_result.fallback_reason:
                    step_result.fallback_reason = f"{'; '.join(strategy_failures)}; {step_result.fallback_reason}"
                else:
                    step_result.fallback_reason = "; ".join(strategy_failures)

            step = step_result.alpha
            step_mode = step_result.mode
            fallback_reason = step_result.fallback_reason

            if not np.isfinite(step) or step < 0:
                return SteepestDescentResult(points, f_values, grad_norms, grads, alphas, step_modes, fallback_reasons, False, "Step size became non-finite or negative", k)

            x_next = x + step * search_direction(g, sense)
            f_next = float(self.obj.f(x_next))
            if not np.isfinite(f_next):
                return SteepestDescentResult(points, f_values, grad_norms, grads, alphas, step_modes, fallback_reasons, False, "Objective became non-finite", k)

            alphas.append(float(step))
            step_modes.append(step_mode)
            fallback_reasons.append(fallback_reason)
            points.append(x_next.tolist())
            f_values.append(f_next)
            g_next = self.obj.grad(x_next)
            if not np.all(np.isfinite(g_next)):
                return SteepestDescentResult(points, f_values, grad_norms, grads, alphas, step_modes, fallback_reasons, False, "Gradient became non-finite", k + 1)
            grad_norms.append(float(np.linalg.norm(g_next)))
            grads.append(g_next.tolist())

            if abs(f_values[-2] - f_values[-1]) < delta_f_tol:
                return SteepestDescentResult(points, f_values, grad_norms, grads, alphas, step_modes, fallback_reasons, True, "Objective improvement below threshold", k + 1)

            x = x_next

        return SteepestDescentResult(points, f_values, grad_norms, grads, alphas, step_modes, fallback_reasons, False, "Max iterations reached", max_iters)


def make_quadratic_objective(A: List[List[float]], b: List[float], c: float = 0.0) -> ObjectiveFunction:
    A_np = np.array(A, dtype=float)
    b_np = np.array(b, dtype=float)

    def f(x: np.ndarray) -> float:
        return 0.5 * float(x.T @ A_np @ x) + float(b_np @ x) + c

    def grad(x: np.ndarray) -> np.ndarray:
        return A_np @ x + b_np

    return ObjectiveFunction.from_quadratic(f=f, grad=grad, A=A_np)


def make_quadratic(A: List[List[float]], b: List[float], c: float = 0.0):
    obj = make_quadratic_objective(A, b, c)
    return obj.f, obj.grad
