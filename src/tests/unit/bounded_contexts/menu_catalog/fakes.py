from collections.abc import Sequence

from src.bounded_contexts.menu_catalog.domain.aggregates.category import (
    Category,
)
from src.bounded_contexts.menu_catalog.domain.aggregates.menu_item import (
    MenuItem,
)
from src.bounded_contexts.menu_catalog.domain.events.event_bus import (
    EventBus,)

from src.bounded_contexts.menu_catalog.domain.events.menu_events import (
    DomainEvent,)

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
        self._categories: dict[CategoryId, Category] = {}
        self.seen: set[Category] = set()

    async def save(self, category: Category) -> None:
        self._categories[category.category_id] = category
        self.seen.add(category)

    async def find_by_id(self, category_id: CategoryId) -> Category | None:
        category = self._categories.get(category_id)
        if category:
            self.seen.add(category)
        return category

    async def exists_by_name(self, name: str) -> bool:
        return any(cat.name == name for cat in self._categories.values())

    async def find_all(self) -> list[Category]:
        categories = list(self._categories.values())
        self.seen.update(categories)
        return categories

    async def delete(self, category_id: CategoryId) -> None:
        category = self._categories.pop(category_id, None)
        if category and category in self.seen:
            self.seen.remove(category)


class FakeMenuItemRepository(MenuItemRepository):
    def __init__(self) -> None:
        self._items: dict[MenuItemId, MenuItem] = {}
        self.seen: set[MenuItem] = set()

    async def save(self, menu_item: MenuItem) -> None:
        self._items[menu_item.item_id] = menu_item
        self.seen.add(menu_item)

    async def find_by_id(self, item_id: MenuItemId) -> MenuItem | None:
        item = self._items.get(item_id)
        if item:
            self.seen.add(item)
        return item

    async def exists_by_name_in_category(
        self, name: str, category_id: CategoryId
    ) -> bool:
        return any(
            item.name == name and item.category_id == category_id
            for item in self._items.values()
        )

    async def find_by_category(
        self, category_id: CategoryId
    ) -> list[MenuItem]:
        items = [
            item
            for item in self._items.values()
            if item.category_id == category_id
        ]
        self.seen.update(items)
        return items

    async def find_all(self) -> list[MenuItem]:
        items = list(self._items.values())
        self.seen.update(items)
        return items

    async def delete(self, item_id: MenuItemId) -> None:
        item = self._items.pop(item_id, None)
        if item and item in self.seen:
            self.seen.remove(item)


class FakeEventBus(EventBus):
    def __init__(self) -> None:
        self.published_events: list[DomainEvent] = []

    async def publish_all(self, events: Sequence[DomainEvent]) -> None:
        self.published_events.extend(events)

    async def publish(self, event: DomainEvent) -> None:
        self.published_events.append(event)


class FakeUnitOfWork(UnitOfWork):
    def __init__(self, event_bus: EventBus | None = None) -> None:
        self.categories = FakeCategoryRepository()
        self.menu_items = FakeMenuItemRepository()
        self.event_bus: EventBus = event_bus or FakeEventBus()
        self.committed = False

    async def _commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        pass
