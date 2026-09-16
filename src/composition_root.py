# src/composition_root.py

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .bounded_contexts.menu_catalog.domain.events.event_bus import EventBus
from .bounded_contexts.menu_catalog.domain.repositories.unit_of_work import (
    UnitOfWork,
)
from .bounded_contexts.menu_catalog.infrastructure.event_bus import (
    InMemoryEventBus,
)
from .bounded_contexts.menu_catalog.infrastructure.unit_of_work import (
    SqlAlchemyUnitOfWork,
)
from .config import Settings, get_settings


class CompositionRoot:
    """Single point of construction for infrastructure dependencies.

    Built once at application startup, held for the app's lifetime.
    Individual requests get a fresh UnitOfWork per request via
    `new_uow()` — never share a UoW/session across requests.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self.engine: AsyncEngine = create_async_engine(
            settings.database_url, echo=False
        )
        self.session_factory: async_sessionmaker[AsyncSession] = (
            async_sessionmaker(self.engine, expire_on_commit=False)
        )
        self.event_bus: EventBus = InMemoryEventBus()

    def new_uow(self) -> UnitOfWork:
        return SqlAlchemyUnitOfWork(self.session_factory, self.event_bus)

    async def dispose(self) -> None:
        await self.engine.dispose()


_composition_root: CompositionRoot | None = None


def get_composition_root() -> CompositionRoot:
    global _composition_root
    if _composition_root is None:
        _composition_root = CompositionRoot(get_settings())
    return _composition_root
