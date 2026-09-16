# tests/integration/menu_catalog/bounded_contexts/test_sqlalchemy_category_repository.py

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.bounded_contexts.menu_catalog.application.commands.category_commands import (
    CreateCategory,
    RenameCategory,
)
from src.bounded_contexts.menu_catalog.application.handlers.category_handlers import (
    create_category,
    rename_category,
)
from src.bounded_contexts.menu_catalog.domain.aggregates.category import Category
from src.bounded_contexts.menu_catalog.domain.events.menu_events import (
    CategoryCreatedEvent,
    DomainEvent,
)

from src.bounded_contexts.menu_catalog.domain.value_objects.identifiers import (
    CategoryId,
)
from src.bounded_contexts.menu_catalog.infrastructure.event_bus import (
    InMemoryEventBus,
)
from src.bounded_contexts.menu_catalog.infrastructure.unit_of_work import (
    SqlAlchemyUnitOfWork,
)


@pytest.mark.asyncio
async def test_create_category_persists_across_transactions(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    event_bus = InMemoryEventBus()
    received: list[CategoryCreatedEvent] = []

    async def _on_created(event: DomainEvent) -> None:
        assert isinstance(event, CategoryCreatedEvent)
        received.append(event)

    event_bus.subscribe(CategoryCreatedEvent, _on_created)

    uow = SqlAlchemyUnitOfWork(session_factory, event_bus)
    await create_category(
        CreateCategory(name="Πίτσες", display_order=1), uow
    )

    # νέο UoW/session — προσομοιώνει διαφορετικό HTTP request
    verify_uow = SqlAlchemyUnitOfWork(session_factory, event_bus)
    async with verify_uow:
        categories = await verify_uow.categories.find_all()

    assert len(categories) == 1
    assert categories[0].name == "Πίτσες"
    assert categories[0].display_order == 1

    assert len(received) == 1
    assert received[0].name == "Πίτσες"


@pytest.mark.asyncio
async def test_rename_category_persists(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    event_bus = InMemoryEventBus()

    uow = SqlAlchemyUnitOfWork(session_factory, event_bus)
    await create_category(
        CreateCategory(name="Καφέδες", display_order=1), uow
    )

    verify_uow = SqlAlchemyUnitOfWork(session_factory, event_bus)
    async with verify_uow:
        category = (await verify_uow.categories.find_all())[0]

    rename_uow = SqlAlchemyUnitOfWork(session_factory, event_bus)
    await rename_category(
        RenameCategory(
            category_id=str(category.category_id.value),
            new_name="Ροφήματα",
        ),
        rename_uow,
    )

    final_uow = SqlAlchemyUnitOfWork(session_factory, event_bus)
    async with final_uow:
        categories = await final_uow.categories.find_all()

    assert categories[0].name == "Ροφήματα"


@pytest.mark.asyncio
async def test_uncommitted_changes_are_rolled_back_on_exception(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    from uuid import uuid4

    event_bus = InMemoryEventBus()
    uow = SqlAlchemyUnitOfWork(session_factory, event_bus)

    with pytest.raises(ValueError, match="simulated failure"):
        async with uow:
            category = Category.create(
                category_id=CategoryId(uuid4()),
                name="Ποτά",
                display_order=1,
            )
            await uow.categories.save(category)
            raise ValueError("simulated failure before commit")

    verify_uow = SqlAlchemyUnitOfWork(session_factory, event_bus)
    async with verify_uow:
        categories = await verify_uow.categories.find_all()

    assert categories == []
