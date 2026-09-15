# tests/unit/bounded_contexts/menu_catalog/application/fakes.py

from collections.abc import Sequence

from src.bounded_contexts.menu_catalog.domain.aggregates.category import Category
from src.bounded_contexts.menu_catalog.domain.aggregates.menu_item import MenuItem
from src.bounded_contexts.menu_catalog.domain.events.event_bus import EventBus
from src.bounded_contexts.menu_catalog.domain.events.menu_events import DomainEvent
from src.bounded_contexts.menu_catalog.domain.repositories.category_repository import (
    CategoryRepository,
)
from src.bounded_contexts.menu_catalog.domain.repositories.menu_item_repository import (
    MenuItemRepository,
)
from src.bounded_contexts.menu_catalog.domain.repositories.unit_of_work import (
    UnitOfWork,
)
from src.bounded_contexts.menu_catalog.domain.value_objects.identifiers import (
    CategoryId,
    MenuItemId,
)


class FakeCategoryRepository(CategoryRepository):
    def __init__(self) -> None:
        super().__init__()
        self._data: dict[CategoryId, Category] = {}

    async def save(self, category: Category) -> None:
        self._data[category.category_id] = category
        self.seen.add(category)

    async def find_by_id(self, category_id: CategoryId) -> Category | None:
        category = self._data.get(category_id)
        if category is not None:
            self.seen.add(category)
        return category

    async def exists_by_name(self, name: str) -> bool:
        return any(c.name == name for c in self._data.values())

    async def find_all(self) -> list[Category]:
        return list(self._data.values())

    async def delete(self, category_id: CategoryId) -> None:
        self._data.pop(category_id, None)


class FakeMenuItemRepository(MenuItemRepository):
    def __init__(self) -> None:
        super().__init__()
        self._data: dict[MenuItemId, MenuItem] = {}

    async def save(self, menu_item: MenuItem) -> None:
        self._data[menu_item.item_id] = menu_item
        self.seen.add(menu_item)

    async def find_by_id(self, item_id: MenuItemId) -> MenuItem | None:
        item = self._data.get(item_id)
        if item is not None:
            self.seen.add(item)
        return item

    async def exists_by_name_in_category(
        self, name: str, category_id: CategoryId
    ) -> bool:
        return any(
            i.name == name and i.category_id == category_id
            for i in self._data.values()
        )

    async def find_by_category(self, category_id: CategoryId) -> list[MenuItem]:
        return [i for i in self._data.values() if i.category_id == category_id]

    async def find_all(self) -> list[MenuItem]:
        return list(self._data.values())

    async def delete(self, item_id: MenuItemId) -> None:
        self._data.pop(item_id, None)


class FakeEventBus(EventBus):
    def __init__(self) -> None:
        self.published: list[DomainEvent] = []

    async def publish(self, event: DomainEvent) -> None:
        self.published.append(event)

    async def publish_all(self, events: Sequence[DomainEvent]) -> None:
        self.published.extend(events)


class FakeUnitOfWork(UnitOfWork):
    def __init__(self) -> None:
        super().__init__(event_bus=FakeEventBus())
        self.categories = FakeCategoryRepository()
        self.menu_items = FakeMenuItemRepository()
        self.committed = False
        self.rolled_back = False

    async def _commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True
