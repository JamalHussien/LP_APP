"""Application service for golden section search orchestration."""

from __future__ import annotations

import json

from optimization.algorithms.search.golden_section import GoldenSectionSearchSolver
from optimization.app.contracts import GoldenSectionCommand, GoldenSectionReport
from optimization.app.exceptions import InputError, PresentationError
from optimization.infrastructure.plots import golden_section_convergence
from optimization.infrastructure.scalar_parser import ScalarFunctionParseError, SymbolicScalarFunctionParser


class GoldenSectionApplicationService:
    """Parses a scalar objective, runs the solver, and prepares presentation data."""

    def execute(self, command: GoldenSectionCommand) -> GoldenSectionReport:
        try:
            objective, variable, _ = SymbolicScalarFunctionParser.parse_expression(command.expression)
            result = GoldenSectionSearchSolver(objective).solve(
                a=command.a,
                b=command.b,
                epsilon=command.epsilon,
                max_iters=command.max_iters,
                sense=command.sense,
            )
        except (ScalarFunctionParseError, ValueError) as exc:
            raise InputError(str(exc)) from exc

        try:
            plot = json.loads(golden_section_convergence(result.history).to_json())
        except Exception as exc:
            raise PresentationError(f"Could not build golden section plot: {exc}") from exc

        return GoldenSectionReport(result=result, variable=variable, plot=plot)
