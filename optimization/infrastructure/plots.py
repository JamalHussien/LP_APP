from __future__ import annotations

import numpy as np
from typing import List, Tuple
import plotly.graph_objects as go


def sd_trajectory(points: List[List[float]], f_values: List[float]):
    pts = np.array(points)
    dim = pts.shape[1]
    if dim == 1:
        x = pts[:, 0]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=list(range(len(x))), y=x, mode="lines+markers", name="x"))
        fig.update_layout(title="Gradient Search Path (1D)", xaxis_title="Iteration", yaxis_title="x")
        return fig
    if dim == 2:
        x = pts[:, 0]
        y = pts[:, 1]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=y, mode="markers+lines", name="Path", line=dict(color="#2563eb")))
        fig.add_trace(go.Scatter(x=[x[0]], y=[y[0]], mode="markers", marker=dict(color="red", size=10), name="Start"))
        fig.add_trace(go.Scatter(x=[x[-1]], y=[y[-1]], mode="markers", marker=dict(color="green", size=10), name="End"))
        fig.update_layout(title="Gradient Search Path (2D)", xaxis_title="x1", yaxis_title="x2")
        return fig
    # fallback: iteration vs f(x)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(range(len(f_values))), y=f_values, mode="lines+markers", name="f(x)"))
    fig.update_layout(title="Objective over iterations", xaxis_title="Iteration", yaxis_title="f(x)")
    return fig


def golden_section_convergence(history):
    fig = go.Figure()
    if not history:
        fig.update_layout(
            title="Golden Section Search Convergence",
            xaxis_title="Iteration",
            yaxis_title="x",
            annotations=[
                {
                    "text": "No iterations were needed because the initial interval already met the tolerance.",
                    "xref": "paper",
                    "yref": "paper",
                    "x": 0.5,
                    "y": 0.5,
                    "showarrow": False,
                }
            ],
        )
        return fig

    iterations = [item.iteration for item in history]
    lowers = [item.xl for item in history]
    uppers = [item.xu for item in history]
    best_x = [item.current_best_x for item in history]
    widths = [item.interval_width for item in history]

    fig.add_trace(go.Scatter(x=iterations, y=lowers, mode="lines+markers", name="xl", line=dict(color="#2563eb")))
    fig.add_trace(go.Scatter(x=iterations, y=uppers, mode="lines+markers", name="xu", line=dict(color="#0f766e")))
    fig.add_trace(go.Scatter(x=iterations, y=best_x, mode="lines+markers", name="Best x", line=dict(color="#f59e0b")))
    fig.add_trace(
        go.Scatter(
            x=iterations,
            y=widths,
            mode="lines+markers",
            name="Interval width",
            yaxis="y2",
            line=dict(color="#ef4444", dash="dot"),
        )
    )
    fig.update_layout(
        title="Golden Section Search Convergence",
        xaxis_title="Iteration",
        yaxis_title="x",
        yaxis2=dict(title="Interval width", overlaying="y", side="right"),
        legend=dict(orientation="h"),
    )
    return fig
