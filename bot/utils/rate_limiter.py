"""Rate limiter queue for outbound Discord API requests."""
import asyncio
from typing import Callable, Awaitable, Any
import structlog
import discord

logger = structlog.get_logger(__name__)

class OutboundQueue:
    __slots__ = ("_queue", "_workers", "concurrency", "active_workers", "is_running")

    def __init__(self, concurrency: int = 3) -> None:
        self._queue: asyncio.PriorityQueue[tuple[int, Callable[..., Awaitable[Any]], tuple, dict, asyncio.Future[Any]]] = asyncio.PriorityQueue()
        self._workers: list[asyncio.Task[None]] = []
        self.concurrency = concurrency
        self.active_workers = 0
        self.is_running = False

    def start(self) -> None:
        """Start the rate limiter queue workers."""
        if self.is_running:
            return
        self.is_running = True
        self._workers = [asyncio.create_task(self._worker_loop(i)) for i in range(self.concurrency)]
        logger.info("Outbound queue started", concurrency=self.concurrency)

    def stop(self) -> None:
        """Stop the rate limiter queue workers."""
        self.is_running = False
        for worker in self._workers:
            worker.cancel()
        self._workers.clear()
        logger.info("Outbound queue stopped")

    def enqueue(self, priority: int, coro_func: Callable[..., Awaitable[Any]], *args: Any, **kwargs: Any) -> asyncio.Future[Any]:
        """Enqueue a request."""
        fut: asyncio.Future[Any] = asyncio.Future()
        self._queue.put_nowait((priority, coro_func, args, kwargs, fut))
        return fut

    async def _worker_loop(self, worker_id: int) -> None:
        while self.is_running:
            try:
                priority, coro_func, args, kwargs, fut = await self._queue.get()
                self.active_workers += 1
                
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        result = await coro_func(*args, **kwargs)
                        if not fut.done():
                            fut.set_result(result)
                        break
                    except discord.RateLimited as e:
                        if attempt == max_retries - 1:
                            if not fut.done():
                                fut.set_exception(e)
                        else:
                            await asyncio.sleep(e.retry_after or (2 ** attempt))
                    except discord.HTTPException as e:
                        if e.status == 429: # Rate limit
                            await asyncio.sleep(2 ** attempt)
                        else:
                            if not fut.done():
                                fut.set_exception(e)
                            break
                    except Exception as e:
                        if not fut.done():
                            fut.set_exception(e)
                        break
                
                self._queue.task_done()
                self.active_workers -= 1
                await asyncio.sleep(0.05)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Worker error", worker_id=worker_id, error=str(e))
                self.active_workers -= 1
