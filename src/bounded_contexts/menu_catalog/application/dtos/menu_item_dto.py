# application/dtos/menu_item_dto.py

from dataclasses import dataclass

from ...domain.aggregates.menu_item import MenuItem
from ...domain.entities.menu_item_modifier import MenuItemModifier
from ...domain.entities.menu_item_variant import MenuItemVariant


@dataclass(frozen=True)
class MenuItemVariantDTO:
    variant_id: str
    name: str
    price_modifier_amount: str
    currency: str

    @classmethod
    def from_entity(cls, variant: MenuItemVariant) -> "MenuItemVariantDTO":
        return cls(
            variant_id=str(variant.variant_id.value),
            name=variant.name,
            price_modifier_amount=str(variant.price_modifier.amount),
            currency=variant.price_modifier.currency.value,
        )


@dataclass(frozen=True)
class MenuItemModifierDTO:
    modifier_id: str
    name: str
    price_addition_amount: str
    currency: str

    @classmethod
    def from_entity(cls, modifier: MenuItemModifier) -> "MenuItemModifierDTO":
        return cls(
            modifier_id=str(modifier.modifier_id.value),
            name=modifier.name,
            price_addition_amount=str(modifier.price_addition.amount),
            currency=modifier.price_addition.currency.value,
        )


@dataclass(frozen=True)
class MenuItemDTO:
    item_id: str
    name: str
    price_amount: str
    currency: str
    category_id: str
    is_available: bool
    variants: list[MenuItemVariantDTO]
    modifiers: list[MenuItemModifierDTO]

    @classmethod
    def from_aggregate(cls, item: MenuItem) -> "MenuItemDTO":
        return cls(
            item_id=str(item.item_id.value),
            name=item.name,
            price_amount=str(item.base_price.amount),
            currency=item.base_price.currency.value,
            category_id=str(item.category_id.value),
            is_available=item.is_available,
            variants=[
                MenuItemVariantDTO.from_entity(v) for v in item.variants
            ],
            modifiers=[
                MenuItemModifierDTO.from_entity(m) for m in item.modifiers
            ],
        )
