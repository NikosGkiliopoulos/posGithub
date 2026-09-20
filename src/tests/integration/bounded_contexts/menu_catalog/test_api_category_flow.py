# tests/integration/bounded_contexts/menu_catalog/test_api_category_flow.py

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from pytest import MonkeyPatch
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.composition_root import CompositionRoot
from src.main import app

from src.bounded_contexts.menu_catalog.infrastructure.event_bus import (
    InMemoryEventBus,
)
from src.bounded_contexts.menu_catalog.infrastructure.db.base import mapper_registry

@pytest.fixture(autouse=True)
def _override_composition_root(
    monkeypatch: MonkeyPatch,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    root = CompositionRoot.__new__(CompositionRoot)
    root.session_factory = session_factory
    root.event_bus = InMemoryEventBus()

    monkeypatch.setattr(
        "src.composition_root.get_composition_root", lambda: root
    )
    # Διόρθωση του import path για το Bounded Context:
    monkeypatch.setattr(
        "src.bounded_contexts.menu_catalog.api.dependencies.get_composition_root",
        lambda: root,
    )


@pytest.mark.asyncio
async def test_create_and_list_categories() -> None:
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/categories", json={"name": "Πίτσες", "display_order": 1}
            )
            assert response.status_code == 201
            body = response.json()
            assert body["name"] == "Πίτσες"
            category_id = body["category_id"]

            response = await client.get("/categories")
            assert response.status_code == 200
            categories = response.json()
            assert len(categories) == 1
            assert categories[0]["category_id"] == category_id


@pytest.mark.asyncio
async def test_rename_nonexistent_category_returns_404() -> None:
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.patch(
                "/categories/00000000-0000-0000-0000-000000000000/rename",
                json={"new_name": "X"},
            )
            assert response.status_code == 404


@pytest.mark.asyncio
async def test_remove_category_with_items_returns_409() -> None:
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            cat_response = await client.post(
                "/categories", json={"name": "Ποτά", "display_order": 1}
            )
            category_id = cat_response.json()["category_id"]

            await client.post(
                "/menu-items",
                json={
                    "name": "Cola",
                    "price_amount": "2.00",
                    "currency": "EUR",
                    "category_id": category_id,
                },
            )

            response = await client.delete(f"/categories/{category_id}")
            assert response.status_code == 409
