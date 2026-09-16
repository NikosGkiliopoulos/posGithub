# infrastructure/event_bus.py

from collections import defaultdict
from collections.abc import Awaitable, Callable, Sequence

from ..domain.events.event_bus import EventBus
from ..domain.events.menu_events import DomainEvent

EventHandler = Callable[[DomainEvent], Awaitable[None]]


class InMemoryEventBus(EventBus):
    """In-process pub/sub dispatcher — handlers run sequentially,
    in-process, on the same asyncio event loop. No message broker.
    """

    def __init__(self) -> None:
        self._handlers: dict[
            type[DomainEvent], list[EventHandler]
        ] = defaultdict(list)

    def subscribe(
        self, event_type: type[DomainEvent], handler: EventHandler
    ) -> None:
        """Register a handler for a specific event type. Not part of
        the abstract EventBus interface — subscription is a concern
        of the concrete implementation only.
        """
        self._handlers[event_type].append(handler)

    async def publish(self, event: DomainEvent) -> None:
        for handler in self._handlers.get(type(event), []):
            await handler(event)

    async def publish_all(self, events: Sequence[DomainEvent]) -> None:
        for event in events:
            await self.publish(event)
