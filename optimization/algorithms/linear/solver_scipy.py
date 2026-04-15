from __future__ import annotations

import numpy as np
from scipy.optimize import linprog

from optimization.core.interfaces import SolverStrategy
from optimization.core.models import ProblemSpec, Solution


class LinearSciPySolver(SolverStrategy):
    def solve(self, problem: ProblemSpec) -> Solution:
        if problem.kind.value != "linear":
            raise ValueError(f"Unsupported problem kind: {problem.kind}")

        n = int(problem.n)
        c = np.array(problem.objective.c, dtype=float)
        A_ub, b_ub, A_eq, b_eq = [], [], [], []
        for con in problem.constraints:
            a = np.array(con.a, dtype=float)
            if con.sense == "<=":
                A_ub.append(a)
                b_ub.append(con.b)
            elif con.sense == ">=":
                A_ub.append(-a)
                b_ub.append(-con.b)
            else:
                A_eq.append(a)
                b_eq.append(con.b)
        A_ub = np.array(A_ub) if A_ub else None
        b_ub = np.array(b_ub) if b_ub else None
        A_eq = np.array(A_eq) if A_eq else None
        b_eq = np.array(b_eq) if b_eq else None

        bounds = []
        if problem.bounds:
            for b in problem.bounds:
                bounds.append((b.lower, b.upper))
        else:
            bounds = [(0, None)] * n

        c_scipy = -c if problem.objective.sense == "maximize" else c

        res = linprog(
            c_scipy,
            A_ub=A_ub,
            b_ub=b_ub,
            A_eq=A_eq,
            b_eq=b_eq,
            bounds=bounds,
            method="highs",
        )

        if not res.success:
            return Solution(
                x=res.x.tolist() if hasattr(res, "x") and res.x is not None else [],
                objective=None,
                success=False,
                message=res.message,
            )
        objective = -res.fun if problem.objective.sense == "maximize" else res.fun
        return Solution(x=res.x.tolist(), objective=float(objective), success=True)
