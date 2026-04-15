from optimization.core.interfaces import SolverStrategy
from optimization.core.models import ProblemSpec, Solution


class NetworkFlowSolverStub(SolverStrategy):
    def solve(self, problem: ProblemSpec) -> Solution:
        raise NotImplementedError("Network flow solver not yet implemented")
