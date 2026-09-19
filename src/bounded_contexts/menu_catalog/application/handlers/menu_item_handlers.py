# application/handlers/menu_item_handlers.py

from decimal import Decimal
from uuid import UUID

from ...domain.aggregates.menu_item import MenuItem
from ...domain.exceptions.menu_exceptions import MenuItemNotFoundError
from ...domain.repositories.unit_of_work import UnitOfWork
from ...domain.value_objects.identifiers import (
    CategoryId,
    MenuItemId,
    ModifierId,
    VariantId,
)
from ...domain.value_objects.money import CURRENCY, Money
from ..commands.menu_item_commands import (
    AddMenuItemModifier,
    AddMenuItemVariant,
    ChangeMenuItemAvailability,
    CreateMenuItem,
    RecategorizeMenuItem,
    RemoveMenuItem,
    RemoveMenuItemModifier,
    RemoveMenuItemVariant,
    RenameMenuItem,
    UpdateMenuItemModifier,
    UpdateMenuItemPrice,
    UpdateMenuItemVariant,
)


async def _get_item_or_raise(uow: UnitOfWork, item_id: str) -> MenuItem:
    item = await uow.menu_items.find_by_id(MenuItemId(UUID(item_id)))
    if item is None:
        raise MenuItemNotFoundError(f"MenuItem {item_id} not found")
    return item


async def create_menu_item(command: CreateMenuItem, uow: UnitOfWork) -> MenuItem:
    async with uow:
        item = MenuItem.create(
            name=command.name,
            base_price=Money(
                Decimal(command.price_amount), CURRENCY(command.currency)
            ),
            category_id=CategoryId(UUID(command.category_id)),
        )
        await uow.menu_items.save(item)
        await uow.commit()
        return item


async def rename_menu_item(command: RenameMenuItem, uow: UnitOfWork) -> None:
    async with uow:
        item = await _get_item_or_raise(uow, command.item_id)
        item.rename(command.new_name)
        await uow.menu_items.save(item)
        await uow.commit()


async def recategorize_menu_item(
    command: RecategorizeMenuItem, uow: UnitOfWork
) -> None:
    async with uow:
        item = await _get_item_or_raise(uow, command.item_id)
        item.change_category(CategoryId(UUID(command.new_category_id)))
        await uow.menu_items.save(item)
        await uow.commit()


async def update_menu_item_price(
    command: UpdateMenuItemPrice, uow: UnitOfWork
) -> None:
    async with uow:
        item = await _get_item_or_raise(uow, command.item_id)
        item.update_price(
            Money(Decimal(command.new_price_amount), CURRENCY(command.currency))
        )
        await uow.menu_items.save(item)
        await uow.commit()


async def change_menu_item_availability(
    command: ChangeMenuItemAvailability, uow: UnitOfWork
) -> None:
    async with uow:
        item = await _get_item_or_raise(uow, command.item_id)
        item.set_availability(command.is_available)
        await uow.menu_items.save(item)
        await uow.commit()


async def remove_menu_item(command: RemoveMenuItem, uow: UnitOfWork) -> None:
    async with uow:
        item = await _get_item_or_raise(uow, command.item_id)
        item.remove()
        await uow.menu_items.save(item)
        await uow.commit()


async def add_menu_item_variant(
    command: AddMenuItemVariant, uow: UnitOfWork
) -> None:
    async with uow:
        item = await _get_item_or_raise(uow, command.item_id)
        item.add_variant(
            name=command.name,
            price_modifier=Money(
                Decimal(command.price_modifier_amount), CURRENCY(command.currency)
            ),
        )
        await uow.menu_items.save(item)
        await uow.commit()


async def update_menu_item_variant(
    command: UpdateMenuItemVariant, uow: UnitOfWork
) -> None:
    async with uow:
        item = await _get_item_or_raise(uow, command.item_id)
        item.update_variant(
            VariantId(UUID(command.variant_id)),
            command.new_name,
            Money(
                Decimal(command.new_price_modifier_amount),
                CURRENCY(command.currency),
            ),
        )
        await uow.menu_items.save(item)
        await uow.commit()


async def remove_menu_item_variant(
    command: RemoveMenuItemVariant, uow: UnitOfWork
) -> None:
    async with uow:
        item = await _get_item_or_raise(uow, command.item_id)
        item.remove_variant(VariantId(UUID(command.variant_id)))
        await uow.menu_items.save(item)
        await uow.commit()


async def add_menu_item_modifier(
    command: AddMenuItemModifier, uow: UnitOfWork
) -> None:
    async with uow:
        item = await _get_item_or_raise(uow, command.item_id)
        item.add_modifier(
            name=command.name,
            price_addition=Money(
                Decimal(command.price_addition_amount), CURRENCY(command.currency)
            ),
        )
        await uow.menu_items.save(item)
        await uow.commit()


async def update_menu_item_modifier(
    command: UpdateMenuItemModifier, uow: UnitOfWork
) -> None:
    async with uow:
        item = await _get_item_or_raise(uow, command.item_id)
        item.update_modifier(
            ModifierId(UUID(command.modifier_id)),
            command.new_name,
            Money(
                Decimal(command.new_price_addition_amount),
                CURRENCY(command.currency),
            ),
        )
        await uow.menu_items.save(item)
        await uow.commit()


async def remove_menu_item_modifier(
    command: RemoveMenuItemModifier, uow: UnitOfWork
) -> None:
    async with uow:
        item = await _get_item_or_raise(uow, command.item_id)
        item.remove_modifier(ModifierId(UUID(command.modifier_id)))
        await uow.menu_items.save(item)
        await uow.commit()
