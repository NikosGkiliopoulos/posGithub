# src/main.py

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.bounded_contexts.menu_catalog.api.error_handlers import register_error_handlers
from src.bounded_contexts.menu_catalog.api.routers.category_router import (
    router as category_router,)

from src.bounded_contexts.menu_catalog.infrastructure.db.base import Base

from src.bounded_contexts.menu_catalog.api.routers.menu_item_router import (
    router as menu_item_router,)

from .composition_root import get_composition_root


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    root = get_composition_root()

    async with root.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield
    await root.dispose()


app = FastAPI(title="orderPOS", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # dev only — ποτέ σε production
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)
app.include_router(category_router)
app.include_router(menu_item_router)
