"""Saga compensation pattern implementation for Discord operations."""
import structlog
from typing import Callable, Awaitable, Any

logger = structlog.get_logger(__name__)

class DiscordTransaction:
    __slots__ = ("operation_name", "_compensations", "completed_steps", "failed_rollbacks")

    def __init__(self, operation_name: str) -> None:
        self.operation_name = operation_name
        self._compensations: list[Callable[[], Awaitable[Any]]] = []
        self.completed_steps = 0
        self.failed_rollbacks = 0

    def register_compensation(self, undo_coro_func: Callable[[], Awaitable[Any]]) -> None:
        """Register a compensation function to be called on rollback."""
        self._compensations.append(undo_coro_func)

    async def __aenter__(self) -> "DiscordTransaction":
        logger.info("Transaction started", operation=self.operation_name)
        return self

    async def __aexit__(self, exc_type: type | None, exc_val: Exception | None, exc_tb: Any) -> None:
        if exc_type is not None:
            logger.error(
                "Transaction failed, initiating rollback",
                operation=self.operation_name,
                error=str(exc_val)
            )
            while self._compensations:
                comp = self._compensations.pop()
                try:
                    await comp()
                    self.completed_steps -= 1
                except Exception as e:
                    self.failed_rollbacks += 1
                    logger.critical(
                        "Rollback step failed",
                        operation=self.operation_name,
                        error=str(e)
                    )
            logger.info(
                "Transaction rollback complete",
                operation=self.operation_name,
                failed_rollbacks=self.failed_rollbacks
            )
        else:
            logger.info("Transaction successful", operation=self.operation_name)
