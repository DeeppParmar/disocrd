"""Custom exceptions for the bot."""

class BotError(Exception):
    """Base exception class for all bot errors."""
    
    __slots__ = ("message",)
    
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class PermissionError(BotError):
    """Raised when a user lacks required permissions."""
    pass


class SetupError(BotError):
    """Raised when server setup encounters an error."""
    pass


class ConfigError(BotError):
    """Raised when there is a configuration error."""
    pass


class RateLimitError(BotError):
    """Raised when a rate limit is hit."""
    pass


class RollbackError(BotError):
    """Raised when a setup rollback fails."""
    pass


class ResourceNotFoundError(BotError):
    """Raised when a requested resource is not found."""
    pass


class ResourceAlreadyExistsError(BotError):
    """Raised when attempting to create a resource that already exists."""
    pass


class HierarchyError(BotError):
    """Raised when an action violates the role hierarchy."""
    pass
