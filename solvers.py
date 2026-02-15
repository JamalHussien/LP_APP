from typing import Optional
import numpy as np
from scipy.optimize import linprog
from models import LPRequest, LPSolution
from interfaces import ISolver

class SciPySolver(ISolver):
    def solve(self, req: LPRequest) -> LPSolution:
        n = int(req.n)
        c = np.array(req.c, dtype=float)
        A_ub, b_ub, A_eq, b_eq = [], [], [], []
        for con in req.constraints:
            a = np.array(con.a, dtype=float)
            if con.sense == '<=':
                A_ub.append(a); b_ub.append(con.b)
            elif con.sense == '>=':
                A_ub.append(-a); b_ub.append(-con.b)
            else:
                A_eq.append(a); b_eq.append(con.b)
        A_ub = np.array(A_ub) if A_ub else None
        b_ub = np.array(b_ub) if b_ub else None
        A_eq = np.array(A_eq) if A_eq else None
        b_eq = np.array(b_eq) if b_eq else None
        bounds = [(0, None)]*n if req.nonneg else [(None, None)]*n
        c_scipy = -c if req.sense == 'maximize' else c

        res = linprog(c_scipy, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

        if not res.success:
            return LPSolution(x=res.x.tolist() if hasattr(res,'x') else [], objective=None, success=False, message=res.message)
        objective = -res.fun if req.sense == 'maximize' else res.fun
        return LPSolution(x=res.x.tolist(), objective=float(objective), success=True)
