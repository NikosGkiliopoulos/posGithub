# infrastructure/unit_of_work.py

from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ...menu_catalog.domain.events.event_bus import EventBus
from ...menu_catalog.domain.repositories.unit_of_work import UnitOfWork
from .repositories.sqlalchemy_category_repository import SqlAlchemyCategoryRepository
from .repositories.sqlalchemy_menu_item_repository import (
    SqlAlchemyMenuItemRepository,
)


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        event_bus: EventBus,
    ) -> None:
        super().__init__(event_bus=event_bus)
        self._session_factory = session_factory
        self._session: AsyncSession | None = None

    async def __aenter__(self) -> Self:
        self._session = self._session_factory()
        self.categories = SqlAlchemyCategoryRepository(self._session)
        self.menu_items = SqlAlchemyMenuItemRepository(self._session)
        return await super().__aenter__()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await super().__aexit__(exc_type, exc_val, exc_tb)
        assert self._session is not None
        await self._session.close()

    async def _commit(self) -> None:
        assert self._session is not None
        await self._session.commit()

    async def rollback(self) -> None:
        if self._session is not None:
            await self._session.rollback()
