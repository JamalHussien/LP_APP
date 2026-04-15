from __future__ import annotations

from typing import Any, Dict, List, Tuple

import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

from optimization.algorithms.gradient.objective import ObjectiveFunction
from optimization.infrastructure.expression_utils import normalize_expression_text


class ObjectiveParseError(ValueError):
    pass


QuadraticParseError = ObjectiveParseError


class SymbolicObjectiveParser:
    """
    Parse a symbolic expression into a callable objective and gradient.
    Detects quadratic structure (constant Hessian) but does not restrict degree.
    """

    @staticmethod
    def _is_quadratic(sympy_expr: sp.Expr, vars_sorted: List[sp.Symbol]) -> bool:
        for v1 in vars_sorted:
            for v2 in vars_sorted:
                for v3 in vars_sorted:
                    if sympy_expr.diff(v1, v2, v3) != 0:
                        return False
        return True

    @staticmethod
    def parse_expression(expr: str) -> Tuple[ObjectiveFunction, List[str], Dict[str, Any]]:
        if not expr or not expr.strip():
            raise ObjectiveParseError("Expression is empty.")

        normalized = normalize_expression_text(expr).replace("^", "**")
        transformations = standard_transformations + (implicit_multiplication_application, convert_xor)
        try:
            sympy_expr = parse_expr(normalized, transformations=transformations, evaluate=True)
        except Exception as exc:
            raise ObjectiveParseError(f"Cannot parse expression: {exc}") from exc

        vars_sorted = sorted(sympy_expr.free_symbols, key=lambda s: s.name)
        if not vars_sorted:
            raise ObjectiveParseError("Expression has no variables.")

        try:
            grad_syms = [sympy_expr.diff(v) for v in vars_sorted]
        except Exception as exc:
            raise ObjectiveParseError(f"Expression not differentiable: {exc}") from exc

        is_quadratic = SymbolicObjectiveParser._is_quadratic(sympy_expr, vars_sorted)
        A = b = c = None
        if is_quadratic:
            hessian = sp.hessian(sympy_expr, vars_sorted)
            A = np.array(hessian.tolist(), dtype=float)
            A = 0.5 * (A + A.T)
            b_vec = sp.Matrix(grad_syms)
            b = np.array(b_vec.subs({v: 0 for v in vars_sorted}), dtype=float).flatten()
            c = float(sympy_expr.subs({v: 0 for v in vars_sorted}))

        f_lam = sp.lambdify(vars_sorted, sympy_expr, modules="numpy")
        grad_lam = sp.lambdify(vars_sorted, grad_syms, modules="numpy")

        def f(x: np.ndarray) -> float:
            return float(f_lam(*list(x)))

        def grad(x: np.ndarray) -> np.ndarray:
            return np.array(grad_lam(*list(x)), dtype=float).flatten()

        if is_quadratic and A is not None:
            objective = ObjectiveFunction.from_quadratic(f=f, grad=grad, A=A)
        else:
            objective = ObjectiveFunction(f=f, grad=grad, is_quadratic=False, A=None)
        meta = {"A": A, "b": b, "c": c, "sympy_expr": sympy_expr}
        return objective, [v.name for v in vars_sorted], meta


class QuadraticFunctionParser(SymbolicObjectiveParser):
    pass
