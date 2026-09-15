# tests/unit/bounded_contexts/menu_catalog/application/test_category_handlers.py

import pytest

from src.bounded_contexts.menu_catalog.application.commands.category_commands import (
    CreateCategory,
    RenameCategory,
)
from src.bounded_contexts.menu_catalog.application.handlers.category_handlers import (
    create_category,
    rename_category,
)
from src.bounded_contexts.menu_catalog.domain.events.menu_events import (
    CategoryCreatedEvent,
    CategoryRenamedEvent,
)
from src.bounded_contexts.menu_catalog.domain.exceptions.menu_exceptions import (
    CategoryNotFoundError,
)

from .fakes import FakeEventBus, FakeUnitOfWork


@pytest.mark.asyncio
async def test_create_category_saves_and_publishes_event() -> None:
    uow = FakeUnitOfWork()
    command = CreateCategory(name="Πίτσες", display_order=1)

    await create_category(command, uow)

    saved = await uow.categories.find_all()
    assert len(saved) == 1
    assert saved[0].name == "Πίτσες"
    assert uow.committed is True

    event_bus = uow.event_bus
    assert isinstance(event_bus, FakeEventBus)
    assert any(
        isinstance(e, CategoryCreatedEvent) for e in event_bus.published
    )


@pytest.mark.asyncio
async def test_rename_category_not_found_raises() -> None:
    uow = FakeUnitOfWork()
    command = RenameCategory(
        category_id="00000000-0000-0000-0000-000000000000",
        new_name="X",
    )

    with pytest.raises(CategoryNotFoundError):
        await rename_category(command, uow)


@pytest.mark.asyncio
async def test_rename_category_publishes_renamed_event() -> None:
    uow = FakeUnitOfWork()
    await create_category(
        CreateCategory(name="Καφέδες", display_order=1), uow
    )
    category = (await uow.categories.find_all())[0]

    await rename_category(
        RenameCategory(
            category_id=str(category.category_id.value),
            new_name="Ροφήματα",
        ),
        uow,
    )

    event_bus = uow.event_bus
    assert isinstance(event_bus, FakeEventBus)
    renamed_events = [
        e for e in event_bus.published if isinstance(e, CategoryRenamedEvent)
    ]
    assert len(renamed_events) == 1
    assert renamed_events[0].old_name == "Καφέδες"
    assert renamed_events[0].new_name == "Ροφήματα"
