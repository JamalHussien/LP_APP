from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional
import numpy as np


@dataclass
class ObjectiveFunction:
    """Encapsulates objective evaluation and structure information."""

    f: Callable[[np.ndarray], float]
    grad: Callable[[np.ndarray], np.ndarray]
    is_quadratic: bool
    A: Optional[np.ndarray] = None

    @staticmethod
    def from_quadratic(f: Callable[[np.ndarray], float], grad: Callable[[np.ndarray], np.ndarray], A: np.ndarray) -> "ObjectiveFunction":
        return ObjectiveFunction(f=f, grad=grad, is_quadratic=True, A=A)
