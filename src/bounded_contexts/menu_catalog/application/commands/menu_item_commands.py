# application/commands/menu_item_commands.py

from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class CreateMenuItem:
    name: str
    price_amount: str
    currency: str
    category_id: str


@dataclass(frozen=True, kw_only=True)
class RenameMenuItem:
    item_id: str
    new_name: str


@dataclass(frozen=True, kw_only=True)
class RecategorizeMenuItem:
    item_id: str
    new_category_id: str


@dataclass(frozen=True, kw_only=True)
class UpdateMenuItemPrice:
    item_id: str
    new_price_amount: str
    currency: str


@dataclass(frozen=True, kw_only=True)
class ChangeMenuItemAvailability:
    item_id: str
    is_available: bool


@dataclass(frozen=True, kw_only=True)
class RemoveMenuItem:
    item_id: str


@dataclass(frozen=True, kw_only=True)
class AddMenuItemVariant:
    item_id: str
    name: str
    price_modifier_amount: str
    currency: str


@dataclass(frozen=True, kw_only=True)
class UpdateMenuItemVariant:
    item_id: str
    variant_id: str
    new_name: str
    new_price_modifier_amount: str
    currency: str


@dataclass(frozen=True, kw_only=True)
class RemoveMenuItemVariant:
    item_id: str
    variant_id: str


@dataclass(frozen=True, kw_only=True)
class AddMenuItemModifier:
    item_id: str
    name: str
    price_addition_amount: str
    currency: str


@dataclass(frozen=True, kw_only=True)
class UpdateMenuItemModifier:
    item_id: str
    modifier_id: str
    new_name: str
    new_price_addition_amount: str
    currency: str


@dataclass(frozen=True, kw_only=True)
class RemoveMenuItemModifier:
    item_id: str
    modifier_id: str
