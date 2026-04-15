from __future__ import annotations

from typing import Any, Callable, Dict, Tuple

import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

from .expression_utils import normalize_expression_text


class ScalarFunctionParseError(ValueError):
    pass


class SymbolicScalarFunctionParser:
    @staticmethod
    def parse_expression(expr: str) -> Tuple[Callable[[float], float], str, Dict[str, Any]]:
        if not expr or not expr.strip():
            raise ScalarFunctionParseError("Expression is empty.")

        normalized = normalize_expression_text(expr).replace("^", "**")
        transformations = standard_transformations + (implicit_multiplication_application, convert_xor)
        try:
            sympy_expr = parse_expr(normalized, transformations=transformations, evaluate=True)
        except Exception as exc:
            raise ScalarFunctionParseError(f"Cannot parse expression: {exc}") from exc

        vars_sorted = sorted(sympy_expr.free_symbols, key=lambda s: s.name)
        if len(vars_sorted) != 1:
            if not vars_sorted:
                raise ScalarFunctionParseError("Expression must contain exactly one variable.")
            names = ", ".join(v.name for v in vars_sorted)
            raise ScalarFunctionParseError(f"Golden Section Search requires exactly one variable; found: {names}")

        variable = vars_sorted[0]
        f_lam = sp.lambdify(variable, sympy_expr, modules="numpy")

        def f(x: float) -> float:
            try:
                with np.errstate(all="ignore"):
                    raw_value = f_lam(float(x))
            except Exception as exc:
                raise ValueError(f"Objective evaluation failed at x={x}: {exc}") from exc

            arr = np.asarray(raw_value)
            if arr.shape != ():
                raise ValueError(f"Objective must evaluate to a scalar value at x={x}.")

            scalar = arr.item()
            if np.iscomplexobj(scalar):
                if not np.isfinite(scalar) or abs(scalar.imag) > 1e-12:
                    raise ValueError(f"Objective evaluated to a non-real value at x={x}: {scalar}")
                scalar = float(scalar.real)
            else:
                scalar = float(scalar)

            if not np.isfinite(scalar):
                raise ValueError(f"Objective evaluated to a non-finite value at x={x}: {scalar}")
            return scalar

        return f, variable.name, {"sympy_expr": sympy_expr, "variable": variable.name}
