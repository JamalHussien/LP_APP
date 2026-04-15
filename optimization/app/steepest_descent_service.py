"""Application service for steepest descent orchestration."""

from __future__ import annotations

import json

import numpy as np

from optimization.algorithms.gradient.steepest_descent import SteepestDescentSolver, make_quadratic_objective
from optimization.app.contracts import SteepestDescentCommand, SteepestDescentReport
from optimization.app.exceptions import InputError, PresentationError
from optimization.infrastructure.plots import sd_trajectory
from optimization.infrastructure.quadratic_parser import ObjectiveParseError, SymbolicObjectiveParser


class SteepestDescentApplicationService:
    """Parses inputs, executes steepest descent, and prepares presentation data."""

    def execute(self, command: SteepestDescentCommand) -> SteepestDescentReport:
        objective, variables = self._build_objective(command)
        x0 = np.array(command.start, dtype=float)

        try:
            fx0 = objective.f(x0)
            gx0 = objective.grad(x0)
        except Exception as exc:
            raise InputError(f"Objective evaluation failed at the start point: {exc}") from exc

        if not np.isfinite(fx0) or not np.all(np.isfinite(gx0)):
            raise InputError("Objective or gradient evaluated to non-finite values at the start point.")

        solver = SteepestDescentSolver(objective)
        result = solver.solve(
            x0=command.start,
            mode=command.mode,
            sense=command.sense,
            alpha=command.alpha,
            max_iters=command.max_iters,
            grad_tol=command.grad_tol,
            delta_f_tol=command.delta_f_tol,
        )
        self._ensure_finite_result(result)

        try:
            plot = json.loads(sd_trajectory(result.points, result.f_values).to_json())
        except Exception as exc:
            raise PresentationError(f"Could not build steepest descent plot: {exc}") from exc

        return SteepestDescentReport(result=result, variables=variables, plot=plot)

    def _build_objective(self, command: SteepestDescentCommand):
        try:
            if command.expression:
                objective, variables, _ = SymbolicObjectiveParser.parse_expression(command.expression)
                if len(command.start) != len(variables):
                    names = ", ".join(variables)
                    raise InputError(f"Start point must have length {len(variables)} (variables: {names})")
                return objective, variables

            if command.A is None or command.b is None or command.n is None:
                raise InputError("Provide an expression or A, b, n.")

            variables = [f"x{i + 1}" for i in range(len(command.b))]
            if len(command.start) != len(variables):
                names = ", ".join(variables)
                raise InputError(f"Start point must have length {len(variables)} (variables: {names})")

            return make_quadratic_objective(command.A, command.b, command.c), variables
        except ObjectiveParseError as exc:
            raise InputError(str(exc)) from exc
        except InputError:
            raise
        except Exception as exc:
            raise InputError(str(exc)) from exc

    @staticmethod
    def _ensure_finite_result(result) -> None:
        if not np.all(np.isfinite(np.array(result.points, dtype=float))):
            raise InputError("Computation produced non-finite point values; likely diverged.")
        if not np.all(np.isfinite(np.array(result.f_values, dtype=float))):
            raise InputError("Computation produced non-finite objective values; likely diverged.")
        if not np.all(np.isfinite(np.array(result.grad_norms, dtype=float))):
            raise InputError("Computation produced non-finite gradient norms; likely diverged.")
