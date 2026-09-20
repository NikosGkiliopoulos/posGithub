# api/routers/menu_item_router.py

from fastapi import APIRouter, Depends

from ...application import message_bus
from ...application.commands.menu_item_commands import (
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
from ...application.dtos.menu_item_dto import MenuItemDTO
from ...domain.repositories.unit_of_work import (
    UnitOfWork,
)
from ..dependencies import get_uow
from ..schemas.menu_item_schemas import (
    AddMenuItemModifierRequest,
    AddMenuItemVariantRequest,
    ChangeMenuItemAvailabilityRequest,
    CreateMenuItemRequest,
    RecategorizeMenuItemRequest,
    RenameMenuItemRequest,
    UpdateMenuItemModifierRequest,
    UpdateMenuItemPriceRequest,
    UpdateMenuItemVariantRequest,
)

from uuid import UUID

from ...domain.exceptions.menu_exceptions import (
    MenuItemNotFoundError,
)
from ...domain.value_objects.identifiers import (
    MenuItemId,
)

router = APIRouter(prefix="/menu-items", tags=["menu-items"])


@router.post("", status_code=201, response_model=MenuItemDTO)
async def create_menu_item(
    payload: CreateMenuItemRequest,
    uow: UnitOfWork = Depends(get_uow),
) -> MenuItemDTO:
    command = CreateMenuItem(
        name=payload.name,
        price_amount=payload.price_amount,
        currency=payload.currency,
        category_id=payload.category_id,
    )
    item = await message_bus.handle(command, uow)
    return MenuItemDTO.from_aggregate(item)


@router.get("", response_model=list[MenuItemDTO])
async def list_menu_items(uow: UnitOfWork = Depends(get_uow)) -> list[MenuItemDTO]:
    async with uow:
        items = await uow.menu_items.find_all()
    return [MenuItemDTO.from_aggregate(i) for i in items]


@router.get("/{item_id}", response_model=MenuItemDTO)
async def get_menu_item(
    item_id: str, uow: UnitOfWork = Depends(get_uow)
) -> MenuItemDTO:

    async with uow:
        item = await uow.menu_items.find_by_id(MenuItemId(UUID(item_id)))
    if item is None:
        raise MenuItemNotFoundError(f"MenuItem {item_id} not found")
    return MenuItemDTO.from_aggregate(item)


@router.patch("/{item_id}/rename", status_code=204)
async def rename_menu_item(
    item_id: str,
    payload: RenameMenuItemRequest,
    uow: UnitOfWork = Depends(get_uow),
) -> None:
    command = RenameMenuItem(item_id=item_id, new_name=payload.new_name)
    await message_bus.handle(command, uow)


@router.patch("/{item_id}/recategorize", status_code=204)
async def recategorize_menu_item(
    item_id: str,
    payload: RecategorizeMenuItemRequest,
    uow: UnitOfWork = Depends(get_uow),
) -> None:
    command = RecategorizeMenuItem(
        item_id=item_id, new_category_id=payload.new_category_id
    )
    await message_bus.handle(command, uow)


@router.patch("/{item_id}/price", status_code=204)
async def update_menu_item_price(
    item_id: str,
    payload: UpdateMenuItemPriceRequest,
    uow: UnitOfWork = Depends(get_uow),
) -> None:
    command = UpdateMenuItemPrice(
        item_id=item_id,
        new_price_amount=payload.new_price_amount,
        currency=payload.currency,
    )
    await message_bus.handle(command, uow)


@router.patch("/{item_id}/availability", status_code=204)
async def change_menu_item_availability(
    item_id: str,
    payload: ChangeMenuItemAvailabilityRequest,
    uow: UnitOfWork = Depends(get_uow),
) -> None:
    command = ChangeMenuItemAvailability(
        item_id=item_id, is_available=payload.is_available
    )
    await message_bus.handle(command, uow)


@router.delete("/{item_id}", status_code=204)
async def remove_menu_item(
    item_id: str, uow: UnitOfWork = Depends(get_uow)
) -> None:
    command = RemoveMenuItem(item_id=item_id)
    await message_bus.handle(command, uow)


# --- Variants ---


@router.post("/{item_id}/variants", status_code=204)
async def add_menu_item_variant(
    item_id: str,
    payload: AddMenuItemVariantRequest,
    uow: UnitOfWork = Depends(get_uow),
) -> None:
    command = AddMenuItemVariant(
        item_id=item_id,
        name=payload.name,
        price_modifier_amount=payload.price_modifier_amount,
        currency=payload.currency,
    )
    await message_bus.handle(command, uow)


@router.patch("/{item_id}/variants/{variant_id}", status_code=204)
async def update_menu_item_variant(
    item_id: str,
    variant_id: str,
    payload: UpdateMenuItemVariantRequest,
    uow: UnitOfWork = Depends(get_uow),
) -> None:
    command = UpdateMenuItemVariant(
        item_id=item_id,
        variant_id=variant_id,
        new_name=payload.new_name,
        new_price_modifier_amount=payload.new_price_modifier_amount,
        currency=payload.currency,
    )
    await message_bus.handle(command, uow)


@router.delete("/{item_id}/variants/{variant_id}", status_code=204)
async def remove_menu_item_variant(
    item_id: str, variant_id: str, uow: UnitOfWork = Depends(get_uow)
) -> None:
    command = RemoveMenuItemVariant(item_id=item_id, variant_id=variant_id)
    await message_bus.handle(command, uow)


# --- Modifiers ---


@router.post("/{item_id}/modifiers", status_code=204)
async def add_menu_item_modifier(
    item_id: str,
    payload: AddMenuItemModifierRequest,
    uow: UnitOfWork = Depends(get_uow),
) -> None:
    command = AddMenuItemModifier(
        item_id=item_id,
        name=payload.name,
        price_addition_amount=payload.price_addition_amount,
        currency=payload.currency,
    )
    await message_bus.handle(command, uow)


@router.patch("/{item_id}/modifiers/{modifier_id}", status_code=204)
async def update_menu_item_modifier(
    item_id: str,
    modifier_id: str,
    payload: UpdateMenuItemModifierRequest,
    uow: UnitOfWork = Depends(get_uow),
) -> None:
    command = UpdateMenuItemModifier(
        item_id=item_id,
        modifier_id=modifier_id,
        new_name=payload.new_name,
        new_price_addition_amount=payload.new_price_addition_amount,
        currency=payload.currency,
    )
    await message_bus.handle(command, uow)


@router.delete("/{item_id}/modifiers/{modifier_id}", status_code=204)
async def remove_menu_item_modifier(
    item_id: str, modifier_id: str, uow: UnitOfWork = Depends(get_uow)
) -> None:
    command = RemoveMenuItemModifier(item_id=item_id, modifier_id=modifier_id)
    await message_bus.handle(command, uow)
