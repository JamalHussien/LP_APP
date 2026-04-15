from __future__ import annotations

from typing import List

from optimization.app.dto import (
    GoldenSectionRequest,
    GoldenSectionIterationResponse,
    GoldenSectionResponse,
    SolveRequest,
    SolveResponse,
    SteepestDescentRequest,
    SteepestDescentResponse,
)
from optimization.app.contracts import (
    GoldenSectionCommand,
    GoldenSectionReport,
    LinearSolveCommand,
    SteepestDescentCommand,
    SteepestDescentReport,
)
from optimization.core.interfaces import ProblemKind
from optimization.core.models import Bound, Constraint, Objective, ProblemSpec, Solution


def dto_to_problem(req: SolveRequest) -> ProblemSpec:
    bounds: List[Bound] = [Bound(0.0, None) if req.nonneg else Bound(None, None) for _ in range(req.n)]
    problem = ProblemSpec(
        kind=ProblemKind(req.kind),
        n=req.n,
        objective=Objective(c=req.c, sense=req.sense),
        constraints=[Constraint(a=c.a, sense=c.sense, b=c.b) for c in req.constraints],
        bounds=bounds,
        metadata={"mode": req.mode, "nonneg": req.nonneg},
    )
    problem.validate()
    return problem


def dto_to_linear_command(req: SolveRequest) -> LinearSolveCommand:
    return LinearSolveCommand(problem=dto_to_problem(req), mode=req.mode)


def dto_to_sd_command(req: SteepestDescentRequest) -> SteepestDescentCommand:
    return SteepestDescentCommand(
        expression=req.expression,
        n=req.n,
        A=req.A,
        b=req.b,
        c=req.c,
        start=req.start,
        sense=req.sense,
        mode=req.mode,
        alpha=req.alpha,
        max_iters=req.max_iters,
        grad_tol=req.grad_tol,
        delta_f_tol=req.delta_f_tol,
    )


def dto_to_golden_section_command(req: GoldenSectionRequest) -> GoldenSectionCommand:
    return GoldenSectionCommand(
        expression=req.expression,
        a=req.a,
        b=req.b,
        sense=req.sense,
        epsilon=req.epsilon,
        max_iters=req.max_iters,
    )


def solution_to_dto(sol: Solution) -> SolveResponse:
    return SolveResponse(x=sol.x, objective=sol.objective, success=sol.success, message=sol.message)


def steepest_descent_report_to_dto(report: SteepestDescentReport) -> SteepestDescentResponse:
    result = report.result
    return SteepestDescentResponse(
        points=result.points,
        f_values=result.f_values,
        grad_norms=result.grad_norms,
        grads=result.grads,
        alphas=result.alphas,
        step_modes=result.step_modes,
        fallback_reasons=result.fallback_reasons,
        success=result.success,
        message=result.message,
        plot=report.plot,
        variables=report.variables,
    )


def golden_section_report_to_dto(report: GoldenSectionReport) -> GoldenSectionResponse:
    result = report.result
    history = [
        GoldenSectionIterationResponse(
            iteration=item.iteration,
            xl=item.xl,
            xu=item.xu,
            x1=item.x1,
            x2=item.x2,
            fx1=item.fx1,
            fx2=item.fx2,
            intervalWidth=item.interval_width,
            currentBestX=item.current_best_x,
            currentBestFx=item.current_best_fx,
        )
        for item in result.history
    ]
    return GoldenSectionResponse(
        x_star=result.x_star,
        fx_star=result.fx_star,
        iterations=result.iterations,
        termination_reason=result.termination_reason,
        history=history,
        success=result.success,
        plot=report.plot,
        variable=report.variable,
    )
