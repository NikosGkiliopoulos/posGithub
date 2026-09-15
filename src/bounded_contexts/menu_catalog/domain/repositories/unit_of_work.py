from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self

from src.bounded_contexts.menu_catalog.domain.repositories.category_repository import (
    CategoryRepository,
)
from src.bounded_contexts.menu_catalog.domain.repositories.menu_item_repository import (
    MenuItemRepository,
)

from ..aggregates.category import Category
from ..aggregates.menu_item import MenuItem
from ..events.event_bus import EventBus


class UnitOfWork(ABC):
    """Abstract Async Interface for the Unit of Work pattern.

    Ensures atomic transactions across repositories, manages the Python
    async context manager lifecycle (__aenter__ / __aexit__), and publishes
    domain events collected from every aggregate touched during the
    transaction after a successful commit.

    Concrete subclasses (e.g. SqlAlchemyUnitOfWork) must:
      - call super().__init__(event_bus=...) with a concrete EventBus
      - set self.categories / self.menu_items to concrete repositories
      - implement `_commit()` with the actual persistence commit
        (e.g. `await self._session.commit()`)
    """

    categories: CategoryRepository
    menu_items: MenuItemRepository

    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            await self.rollback()

    async def commit(self) -> None:
        """Commit all changes made during the transaction, then publish
        every domain event raised by aggregates touched in this UoW.
        """
        await self._commit()
        await self._publish_events()

    @abstractmethod
    async def _commit(self) -> None:
        """Infra-specific commit (e.g. session.commit()).

        Implemented by concrete subclasses — never called directly by
        application code, only via `commit()`.
        """
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        """Rollback the transaction, discarding uncommitted changes."""
        raise NotImplementedError

    async def _publish_events(self) -> None:
        for aggregate in self._collect_seen_aggregates():
            events = aggregate.collect_events()
            if events:
                await self.event_bus.publish_all(events)

    def _collect_seen_aggregates(self) -> list[Category | MenuItem]:
        return [*self.categories.seen, *self.menu_items.seen]
