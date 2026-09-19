# application/handlers/category_handlers.py

from uuid import UUID, uuid4

from ...domain.aggregates.category import Category
from ...domain.exceptions.menu_exceptions import (
    CategoryNotEmptyError,
    CategoryNotFoundError,
)

from ...domain.repositories.unit_of_work import UnitOfWork
from ...domain.value_objects.identifiers import CategoryId
from ..commands.category_commands import (
    CreateCategory,
    RemoveCategory,
    RenameCategory,
    ReorderCategory,
)


async def create_category(command: CreateCategory, uow: UnitOfWork) -> Category:
    async with uow:
        category = Category.create(
            category_id=CategoryId(uuid4()),
            name=command.name,
            display_order=command.display_order,
        )
        await uow.categories.save(category)
        await uow.commit()
        return category


async def rename_category(command: RenameCategory, uow: UnitOfWork) -> None:
    async with uow:
        category = await uow.categories.find_by_id(
            CategoryId(UUID(command.category_id)))

        if category is None:
            raise CategoryNotFoundError(f"Category {command.category_id} not found")
        category.rename(command.new_name)
        await uow.categories.save(category)
        await uow.commit()


async def reorder_category(command: ReorderCategory, uow: UnitOfWork) -> None:
    async with uow:
        category = await uow.categories.find_by_id(
            CategoryId(UUID(command.category_id)))

        if category is None:
            raise CategoryNotFoundError(f"Category {command.category_id} not found")
        category.reorder(command.new_position)
        await uow.categories.save(category)
        await uow.commit()


async def remove_category(command: RemoveCategory, uow: UnitOfWork) -> None:
    async with uow:
        cat_id = CategoryId(UUID(command.category_id))
        category = await uow.categories.find_by_id(cat_id)
        if category is None:
            raise CategoryNotFoundError(f"Category {command.category_id} not found")

        items_in_category = await uow.menu_items.find_by_category(category.category_id)
        if items_in_category:
            raise CategoryNotEmptyError(
                f"Category {command.category_id} still has "
                f"{len(items_in_category)} menu item(s)"
            )

        category.remove()
        await uow.categories.save(category)
        await uow.commit()
