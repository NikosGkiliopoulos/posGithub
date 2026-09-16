# infrastructure/repositories/sqlalchemy_menu_item_repository.py

from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.aggregates.menu_item import MenuItem
from ...domain.entities.menu_item_modifier import MenuItemModifier
from ...domain.entities.menu_item_variant import MenuItemVariant
from ...domain.repositories.menu_item_repository import MenuItemRepository
from ...domain.value_objects.identifiers import (
    CategoryId,
    MenuItemId,
    ModifierId,
    VariantId,
)
from ...domain.value_objects.money import CURRENCY, Money
from ..db.models import MenuItemModel, MenuItemModifierModel, MenuItemVariantModel


def _to_domain(model: MenuItemModel) -> MenuItem:
    return MenuItem(
        item_id=MenuItemId(UUID(model.id)),
        name=model.name,
        base_price=Money(
            Decimal(model.price_amount), CURRENCY(model.price_currency)
        ),
        category_id=CategoryId(UUID(model.category_id)),
        is_available=model.is_available,
        variants=[
            MenuItemVariant(
                variant_id=VariantId(UUID(v.id)),
                name=v.name,
                price_modifier=Money(
                    Decimal(v.price_modifier_amount),
                    CURRENCY(v.price_modifier_currency),
                ),
            )
            for v in model.variants
        ],
        modifiers=[
            MenuItemModifier(
                modifier_id=ModifierId(UUID(m.id)),
                name=m.name,
                price_addition=Money(
                    Decimal(m.price_addition_amount),
                    CURRENCY(m.price_addition_currency),
                ),
            )
            for m in model.modifiers
        ],
    )


class SqlAlchemyMenuItemRepository(MenuItemRepository):
    """Concrete MenuItem repository backed by SQLAlchemy async session.

    On update, child rows (variants/modifiers) are fully replaced rather
    than diffed — simpler and safe given menus have small child counts.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self._session = session

    async def save(self, menu_item: MenuItem) -> None:
        model = await self._session.get(MenuItemModel, str(menu_item.item_id.value))

        variant_models = [
            MenuItemVariantModel(
                id=str(v.variant_id.value),
                name=v.name,
                price_modifier_amount=str(v.price_modifier.amount),
                price_modifier_currency=v.price_modifier.currency.value,
            )
            for v in menu_item.variants
        ]
        modifier_models = [
            MenuItemModifierModel(
                id=str(m.modifier_id.value),
                name=m.name,
                price_addition_amount=str(m.price_addition.amount),
                price_addition_currency=m.price_addition.currency.value,
            )
            for m in menu_item.modifiers
        ]

        if model is None:
            self._session.add(
                MenuItemModel(
                    id=str(menu_item.item_id.value),
                    name=menu_item.name,
                    price_amount=str(menu_item.base_price.amount),
                    price_currency=menu_item.base_price.currency.value,
                    category_id=str(menu_item.category_id.value),
                    is_available=menu_item.is_available,
                    variants=variant_models,
                    modifiers=modifier_models,
                )
            )
        else:
            model.name = menu_item.name
            model.price_amount = str(menu_item.base_price.amount)
            model.price_currency = menu_item.base_price.currency.value
            model.category_id = str(menu_item.category_id.value)
            model.is_available = menu_item.is_available
            model.variants[:] = variant_models
            model.modifiers[:] = modifier_models

        self.seen.add(menu_item)

    async def find_by_id(self, item_id: MenuItemId) -> MenuItem | None:
        model = await self._session.get(MenuItemModel, str(item_id.value))
        if model is None:
            return None
        item = _to_domain(model)
        self.seen.add(item)
        return item

    async def exists_by_name_in_category(
        self, name: str, category_id: CategoryId
    ) -> bool:
        stmt = select(MenuItemModel.id).where(
            MenuItemModel.name == name,
            MenuItemModel.category_id == str(category_id.value),
        )
        result = await self._session.execute(stmt)
        return result.first() is not None

    async def find_by_category(self, category_id: CategoryId) -> list[MenuItem]:
        stmt = select(MenuItemModel).where(
            MenuItemModel.category_id == str(category_id.value)
        )
        result = await self._session.execute(stmt)
        return [_to_domain(m) for m in result.scalars().all()]

    async def find_all(self) -> list[MenuItem]:
        stmt = select(MenuItemModel)
        result = await self._session.execute(stmt)
        return [_to_domain(m) for m in result.scalars().all()]

    async def delete(self, item_id: MenuItemId) -> None:
        model = await self._session.get(MenuItemModel, str(item_id.value))
        if model is not None:
            await self._session.delete(model)
