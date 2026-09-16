# tests/integration/menu_catalog/bounded_contexts/test_sqlalchemy_menu_item_repository.py

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.bounded_contexts.menu_catalog.application.commands.category_commands import (
    CreateCategory,
)
from src.bounded_contexts.menu_catalog.application.commands.menu_item_commands import (
    AddMenuItemVariant,
    CreateMenuItem,
)
from src.bounded_contexts.menu_catalog.application.handlers.category_handlers import (
    create_category,
)
from src.bounded_contexts.menu_catalog.application.handlers.menu_item_handlers import (
    add_menu_item_variant,
    create_menu_item,
)
from src.bounded_contexts.menu_catalog.infrastructure.event_bus import (
    InMemoryEventBus,
)
from src.bounded_contexts.menu_catalog.infrastructure.unit_of_work import (
    SqlAlchemyUnitOfWork,
)


@pytest.mark.asyncio
async def test_menu_item_with_variant_round_trips(
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

    item_uow = SqlAlchemyUnitOfWork(session_factory, event_bus)
    await create_menu_item(
        CreateMenuItem(
            name="Espresso",
            price_amount="2.50",
            currency="EUR",
            category_id=str(category.category_id.value),
        ),
        item_uow,
    )

    read_uow = SqlAlchemyUnitOfWork(session_factory, event_bus)
    async with read_uow:
        item = (await read_uow.menu_items.find_all())[0]

    variant_uow = SqlAlchemyUnitOfWork(session_factory, event_bus)
    await add_menu_item_variant(
        AddMenuItemVariant(
            item_id=str(item.item_id.value),
            name="Διπλό",
            price_modifier_amount="0.80",
            currency="EUR",
        ),
        variant_uow,
    )

    final_uow = SqlAlchemyUnitOfWork(session_factory, event_bus)
    async with final_uow:
        final_item = (await final_uow.menu_items.find_all())[0]

    assert final_item.name == "Espresso"
    assert len(final_item.variants) == 1
    assert final_item.variants[0].name == "Διπλό"
    assert str(final_item.variants[0].price_modifier.amount) == "0.80"
