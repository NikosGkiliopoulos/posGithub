# infrastructure/db/models.py

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class CategoryModel(Base):
    __tablename__ = "categories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    display_order: Mapped[int] = mapped_column(nullable=False)


class MenuItemModel(Base):
    __tablename__ = "menu_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    price_amount: Mapped[str] = mapped_column(String(32), nullable=False)
    price_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    category_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("categories.id"), nullable=False
    )
    is_available: Mapped[bool] = mapped_column(nullable=False, default=True)

    variants: Mapped[list["MenuItemVariantModel"]] = relationship(
        back_populates="menu_item",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    modifiers: Mapped[list["MenuItemModifierModel"]] = relationship(
        back_populates="menu_item",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class MenuItemVariantModel(Base):
    __tablename__ = "menu_item_variants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    menu_item_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("menu_items.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    price_modifier_amount: Mapped[str] = mapped_column(String(32), nullable=False)
    price_modifier_currency: Mapped[str] = mapped_column(String(3), nullable=False)

    menu_item: Mapped["MenuItemModel"] = relationship(back_populates="variants")


class MenuItemModifierModel(Base):
    __tablename__ = "menu_item_modifiers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    menu_item_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("menu_items.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    price_addition_amount: Mapped[str] = mapped_column(String(32), nullable=False)
    price_addition_currency: Mapped[str] = mapped_column(String(3), nullable=False)

    menu_item: Mapped["MenuItemModel"] = relationship(back_populates="modifiers")
