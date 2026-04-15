from __future__ import annotations

import io
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from typing import Tuple
from optimization.core.interfaces import Renderer, RenderArtifact
from optimization.core.models import ProblemSpec, Solution
from .geometry import compute_feasible_vertices


class LinearMatplotlibRenderer(Renderer):
    def render(self, problem: ProblemSpec, solution: Solution) -> Tuple[bytes, str]:
        if problem.n == 3:
            try:
                import plotly.graph_objs as go
                from plotly.offline import plot as plotly_plot
            except Exception:
                raise ValueError("Plotly is required for 3-variable interactive plots")

            data = [
                go.Scatter3d(
                    x=[solution.x[0] if solution.success else 0],
                    y=[solution.x[1] if solution.success else 0],
                    z=[solution.x[2] if solution.success else 0],
                    mode="markers",
                    marker=dict(size=6, color="red"),
                    name="Optimal",
                )
            ]

            for i, con in enumerate(problem.constraints):
                a = np.array(con.a, dtype=float)
                if len(a) != 3:
                    continue
                xx = np.linspace(-1, 1, 10)
                yy = np.linspace(-1, 1, 10)
                XX, YY = np.meshgrid(xx, yy)
                if abs(a[2]) > 1e-9:
                    ZZ = (con.b - a[0] * XX - a[1] * YY) / a[2]
                    data.append(go.Surface(x=XX, y=YY, z=ZZ, showscale=False, opacity=0.3, name=f"con_{i}"))

            layout = go.Layout(title="3D LP (interactive)", scene=dict(xaxis_title="x1", yaxis_title="x2", zaxis_title="x3"))
            fig = go.Figure(data=data, layout=layout)
            html = plotly_plot(fig, include_plotlyjs="cdn", output_type="div")
            return html.encode("utf-8"), "text/html"

        if problem.n != 2:
            raise ValueError("Graphical rendering supports 2 variables for static plots.")

        feasible = compute_feasible_vertices(problem)
        if not feasible:
            raise ValueError("No feasible region")

        pts = np.array(feasible)
        centroid = pts.mean(axis=0)
        angles = np.arctan2(pts[:, 1] - centroid[1], pts[:, 0] - centroid[0])
        order = np.argsort(angles)
        poly = pts[order]

        fig, ax = plt.subplots(figsize=(6, 6))
        xs = np.linspace(poly[:, 0].min() - 1, poly[:, 0].max() + 1, 400)
        for con in problem.constraints:
            a = con.a
            if len(a) != 2:
                continue
            a0, a1 = a
            if abs(a1) < 1e-9:
                xval = con.b / a0 if abs(a0) > 1e-9 else None
                if xval is not None:
                    ax.axvline(xval, linestyle="--")
            else:
                ys = (con.b - a0 * xs) / a1
                ax.plot(xs, ys, linestyle="--")

        ax.fill(poly[:, 0], poly[:, 1], alpha=0.25, label="Feasible region")
        ax.scatter(poly[:, 0], poly[:, 1], c="k")
        if solution.success and len(solution.x) >= 2:
            ax.plot(solution.x[0], solution.x[1], marker="o", markersize=10, label="Optimal", color="red")
        ax.set_xlabel("x1")
        ax.set_ylabel("x2")
        ax.legend()
        ax.grid(True)
        buf = io.BytesIO()
        fig.tight_layout()
        fig.savefig(buf, format="png")
        plt.close(fig)
        buf.seek(0)
        return buf.read(), "image/png"
