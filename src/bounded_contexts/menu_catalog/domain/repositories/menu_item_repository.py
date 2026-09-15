# domain/repositories/menu_item_repository.py

from abc import ABC, abstractmethod

from src.bounded_contexts.menu_catalog.domain.aggregates.menu_item import MenuItem
from src.bounded_contexts.menu_catalog.domain.value_objects.identifiers import (
    CategoryId,
    MenuItemId,
)


class MenuItemRepository(ABC):
    """Async repository interface for managing MenuItem Aggregate Roots."""

    def __init__(self) -> None:
        self.seen: set[MenuItem] = set()

    @abstractmethod
    async def save(self, menu_item: MenuItem) -> None:
        pass

    @abstractmethod
    async def find_by_id(self, item_id: MenuItemId) -> MenuItem | None:
        pass

    @abstractmethod
    async def exists_by_name_in_category(
        self, name: str, category_id: CategoryId
    ) -> bool:
        pass

    @abstractmethod
    async def find_by_category(self, category_id: CategoryId) -> list[MenuItem]:
        pass

    @abstractmethod
    async def find_all(self) -> list[MenuItem]:
        pass

    @abstractmethod
    async def delete(self, item_id: MenuItemId) -> None:
        pass
