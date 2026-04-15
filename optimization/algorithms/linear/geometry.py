from __future__ import annotations

from typing import List, Tuple
import numpy as np
from optimization.core.models import ProblemSpec


def compute_feasible_vertices(problem: ProblemSpec) -> List[Tuple[float, float]]:
    req = problem
    lines = []
    for con in req.constraints:
        a = np.array(con.a, dtype=float)
        if len(a) != 2:
            continue
        lines.append((a[0], a[1], float(con.b)))
    pts = []
    m = len(lines)
    for i in range(m):
        for j in range(i + 1, m):
            A = np.array([[lines[i][0], lines[i][1]], [lines[j][0], lines[j][1]]], dtype=float)
            b = np.array([lines[i][2], lines[j][2]], dtype=float)
            if abs(np.linalg.det(A)) < 1e-9:
                continue
            sol = np.linalg.solve(A, b)
            pts.append((float(sol[0]), float(sol[1])))
    if req.metadata.get("nonneg", True) and len(lines) > 0:
        for ln in lines:
            a1, a2, r = ln
            if abs(a2) > 1e-9:
                pts.append((0.0, float(r / a2)))
            if abs(a1) > 1e-9:
                pts.append((float(r / a1), 0.0))
        pts.append((0.0, 0.0))
    if not pts:
        return []
    pts_arr = np.unique(np.array(pts).round(9), axis=0)
    feasible = []
    for x, y in pts_arr:
        ok = True
        for con in req.constraints:
            a = np.array(con.a, dtype=float)
            val = a[0] * x + a[1] * y
            if con.sense == "<=" and val > con.b + 1e-6:
                ok = False
                break
            if con.sense == ">=" and val < con.b - 1e-6:
                ok = False
                break
            if con.sense == "=" and abs(val - con.b) > 1e-6:
                ok = False
                break
        if ok:
            feasible.append((x, y))
    return feasible
