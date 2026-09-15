# domain/repositories/category_repository.py

from abc import ABC, abstractmethod

from src.bounded_contexts.menu_catalog.domain.aggregates.category import Category
from src.bounded_contexts.menu_catalog.domain.value_objects.identifiers import (
    CategoryId,
)


class CategoryRepository(ABC):
    """Async repository interface for managing Category Aggregate Roots."""

    def __init__(self) -> None:
        self.seen: set[Category] = set()

    @abstractmethod
    async def save(self, category: Category) -> None:
        pass

    @abstractmethod
    async def find_by_id(self, category_id: CategoryId) -> Category | None:
        pass

    @abstractmethod
    async def exists_by_name(self, name: str) -> bool:
        pass

    @abstractmethod
    async def find_all(self) -> list[Category]:
        pass

    @abstractmethod
    async def delete(self, category_id: CategoryId) -> None:
        pass
