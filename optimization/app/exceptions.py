"""Application-layer exception types mapped to HTTP responses in the API adapter."""


class ApplicationError(Exception):
    """Base class for failures raised by application services."""


class InputError(ApplicationError):
    """The request payload or parsed input is invalid."""


class ComputationError(ApplicationError):
    """The underlying computation could not be completed successfully."""


class PresentationError(ApplicationError):
    """A result was computed but could not be rendered or serialized."""


class FeatureUnavailableError(ApplicationError):
    """The requested capability is not implemented or not registered."""
