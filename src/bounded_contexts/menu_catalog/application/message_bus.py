# application/message_bus.py

from typing import Any, Awaitable, Callable

from ..domain.repositories.unit_of_work import UnitOfWork
from .commands.category_commands import (
    CreateCategory,
    RemoveCategory,
    RenameCategory,
    ReorderCategory,
)
from .commands.menu_item_commands import (
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
from .handlers import category_handlers, menu_item_handlers

Command = Any
Handler = Callable[[Command, UnitOfWork], Awaitable[Any]]

COMMAND_HANDLERS: dict[type, Handler] = {
    CreateCategory: category_handlers.create_category,
    RenameCategory: category_handlers.rename_category,
    ReorderCategory: category_handlers.reorder_category,
    RemoveCategory: category_handlers.remove_category,
    CreateMenuItem: menu_item_handlers.create_menu_item,
    RenameMenuItem: menu_item_handlers.rename_menu_item,
    RecategorizeMenuItem: menu_item_handlers.recategorize_menu_item,
    UpdateMenuItemPrice: menu_item_handlers.update_menu_item_price,
    ChangeMenuItemAvailability: menu_item_handlers.change_menu_item_availability,
    RemoveMenuItem: menu_item_handlers.remove_menu_item,
    AddMenuItemVariant: menu_item_handlers.add_menu_item_variant,
    UpdateMenuItemVariant: menu_item_handlers.update_menu_item_variant,
    RemoveMenuItemVariant: menu_item_handlers.remove_menu_item_variant,
    AddMenuItemModifier: menu_item_handlers.add_menu_item_modifier,
    UpdateMenuItemModifier: menu_item_handlers.update_menu_item_modifier,
    RemoveMenuItemModifier: menu_item_handlers.remove_menu_item_modifier,
}


async def handle(command: Command, uow: UnitOfWork) -> Any:
    handler = COMMAND_HANDLERS.get(type(command))
    if handler is None:
        raise ValueError(
            f"No handler registered for command {type(command).__name__}"
        )
    return await handler(command, uow)
