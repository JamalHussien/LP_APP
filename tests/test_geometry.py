from optimization.core.models import ProblemSpec, Objective, Constraint
from optimization.core.interfaces import ProblemKind
from optimization.algorithms.linear.geometry import compute_feasible_vertices


def test_compute_feasible_vertices_simple_square():
    problem = ProblemSpec(
        kind=ProblemKind.LINEAR,
        n=2,
        objective=Objective(c=[1, 1]),
        constraints=[
            Constraint(a=[1, 0], sense="<=", b=2),
            Constraint(a=[0, 1], sense="<=", b=2),
            Constraint(a=[1, 1], sense="<=", b=3),
        ],
        metadata={"nonneg": True},
    )
    verts = compute_feasible_vertices(problem)
    # Should include origin and axis intercepts
    assert (0.0, 0.0) in verts
    assert len(verts) >= 3
