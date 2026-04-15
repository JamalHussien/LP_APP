from optimization.core.interfaces import SolverStrategy
from optimization.core.models import ProblemSpec, Solution


class IntegerSolverStub(SolverStrategy):
    def solve(self, problem: ProblemSpec) -> Solution:
        raise NotImplementedError("Integer programming solver not yet implemented")
