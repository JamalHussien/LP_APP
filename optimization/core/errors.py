class ValidationError(Exception):
    """Input validation failed."""


class SolverError(Exception):
    """Underlying solver failed."""


class RendererError(Exception):
    """Rendering failed."""
