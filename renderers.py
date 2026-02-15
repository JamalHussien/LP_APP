import io
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from models import LPRequest, LPSolution
from interfaces import IRenderer
from typing import List, Tuple


def _compute_feasible_vertices(req: LPRequest) -> List[Tuple[float,float]]:
    # Build line representations and compute pairwise intersections (same as original logic)
    lines = []
    for con in req.constraints:
        a = np.array(con.a, dtype=float)
        # For degenerate constraints with >2 variables, raise
        if len(a) != 2:
            continue
        lines.append((a[0], a[1], float(con.b)))
    pts = []
    m = len(lines)
    for i in range(m):
        for j in range(i+1, m):
            A = np.array([[lines[i][0], lines[i][1]],[lines[j][0], lines[j][1]]], dtype=float)
            b = np.array([lines[i][2], lines[j][2]], dtype=float)
            if abs(np.linalg.det(A)) < 1e-9:
                continue
            sol = np.linalg.solve(A, b)
            pts.append((float(sol[0]), float(sol[1])))
    # include axis intersections if nonneg
    if req.nonneg and len(lines)>0:
        for ln in lines:
            a1,a2,r = ln
            if abs(a2) > 1e-9:
                pts.append((0.0, float(r / a2)))
            if abs(a1) > 1e-9:
                pts.append((float(r / a1), 0.0))
        pts.append((0.0,0.0))
    # filter unique
    if not pts:
        return []
    pts_arr = np.unique(np.array(pts).round(9), axis=0)
    # keep only those satisfying all constraints
    feasible = []
    for x,y in pts_arr:
        ok = True
        for con in req.constraints:
            a = np.array(con.a, dtype=float)
            val = a[0]*x + a[1]*y
            if con.sense == '<=' and val > con.b + 1e-6:
                ok=False; break
            if con.sense == '>=' and val < con.b - 1e-6:
                ok=False; break
            if con.sense == '=' and abs(val-con.b) > 1e-6:
                ok=False; break
        if ok:
            feasible.append((x,y))
    return feasible

class MatplotlibRenderer(IRenderer):
    def render_graph(self, req: LPRequest, solution: LPSolution):
        if req.n == 3:
            try:
                import plotly.graph_objs as go
                from plotly.offline import plot as plotly_plot
            except Exception:
                raise ValueError("Plotly is required for 3-variable interactive plots")

            pts = []
            for con in req.constraints:
                a = np.array(con.a, dtype=float)
                if len(a) != 3:
                    continue
            x_opt = solution.x if solution.success else [0,0,0]
            data = [go.Scatter3d(x=[x_opt[0]], y=[x_opt[1]], z=[x_opt[2]], mode='markers', marker=dict(size=6, color='red'), name='Optimal')]

            for i, con in enumerate(req.constraints):
                a = np.array(con.a, dtype=float)
                if len(a) != 3:
                    continue
                xx = np.linspace(-1, 1, 10)
                yy = np.linspace(-1, 1, 10)
                XX, YY = np.meshgrid(xx, yy)
                
                if abs(a[2]) > 1e-9:
                    ZZ = (con.b - a[0]*XX - a[1]*YY) / a[2]
                    data.append(go.Surface(x=XX, y=YY, z=ZZ, showscale=False, opacity=0.3, name=f'con_{i}'))

            layout = go.Layout(title='3D LP (interactive)', scene=dict(xaxis_title='x1', yaxis_title='x2', zaxis_title='x3'))
            fig = go.Figure(data=data, layout=layout)
            html = plotly_plot(fig, include_plotlyjs='cdn', output_type='div')
            return (html.encode('utf-8'), 'text/html')

        if req.n != 2:
            raise ValueError("Graphical rendering supports 2 variables for static plots.")
        feasible = _compute_feasible_vertices(req)
        if not feasible:
            raise ValueError("No feasible region")

        pts = np.array(feasible)
        centroid = pts.mean(axis=0)
        angles = np.arctan2(pts[:,1]-centroid[1], pts[:,0]-centroid[0])
        order = np.argsort(angles)
        poly = pts[order]

        fig, ax = plt.subplots(figsize=(6,6))
        xs = np.linspace(poly[:,0].min()-1, poly[:,0].max()+1, 400)
        for con in req.constraints:
            a = con.a
            if len(a) != 2:
                continue
            a0,a1 = a
            if abs(a1) < 1e-9:
                xval = con.b / a0 if abs(a0) > 1e-9 else None
                if xval is not None:
                    ax.axvline(xval, linestyle='--')
            else:
                ys = (con.b - a0*xs) / a1
                ax.plot(xs, ys, linestyle='--')

        ax.fill(poly[:,0], poly[:,1], alpha=0.25, label='Feasible region')
        ax.scatter(poly[:,0], poly[:,1], c='k')
        if solution.success:
            ax.plot(solution.x[0], solution.x[1], marker='o', markersize=10, label='Optimal', color='red')
        ax.set_xlabel('x1'); ax.set_ylabel('x2'); ax.legend(); ax.grid(True)
        buf = io.BytesIO()
        fig.tight_layout()
        fig.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        return (buf.read(), 'image/png')
