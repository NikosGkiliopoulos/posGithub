# infrastructure/repositories/sqlalchemy_category_repository.py

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.aggregates.category import Category
from ...domain.repositories.category_repository import CategoryRepository
from ...domain.value_objects.identifiers import CategoryId
from ..db.models import CategoryModel


def _to_domain(model: CategoryModel) -> Category:
    return Category(
        category_id=CategoryId(UUID(model.id)),
        name=model.name,
        display_order=model.display_order,
    )


class SqlAlchemyCategoryRepository(CategoryRepository):
    """Concrete Category repository backed by SQLAlchemy async session.

    Domain aggregates are mapped to/from CategoryModel explicitly here —
    the domain layer never imports SQLAlchemy.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self._session = session

    async def save(self, category: Category) -> None:
        model = await self._session.get(
            CategoryModel, str(category.category_id.value)
        )
        if model is None:
            self._session.add(
                CategoryModel(
                    id=str(category.category_id.value),
                    name=category.name,
                    display_order=category.display_order,
                )
            )
        else:
            model.name = category.name
            model.display_order = category.display_order
        self.seen.add(category)

    async def find_by_id(self, category_id: CategoryId) -> Category | None:
        model = await self._session.get(CategoryModel, str(category_id.value))
        if model is None:
            return None
        category = _to_domain(model)
        self.seen.add(category)
        return category

    async def exists_by_name(self, name: str) -> bool:
        stmt = select(CategoryModel.id).where(CategoryModel.name == name)
        result = await self._session.execute(stmt)
        return result.first() is not None

    async def find_all(self) -> list[Category]:
        stmt = select(CategoryModel)
        result = await self._session.execute(stmt)
        return [_to_domain(m) for m in result.scalars().all()]

    async def delete(self, category_id: CategoryId) -> None:
        model = await self._session.get(CategoryModel, str(category_id.value))
        if model is not None:
            await self._session.delete(model)
