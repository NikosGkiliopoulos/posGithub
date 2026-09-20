# orderPOS

A restaurant Point-of-Sale system built with **Domain-Driven Design (DDD)** and **Event-Driven Architecture (EDA)** in Python.

## Vision

orderPOS aims to cover the full operational cycle of a restaurant: menu management (categories, items, variants, modifiers), floor/table management, order taking and kitchen routing, and eventually payments/receipts. Each functional area is designed as a separate **bounded context**, with clear boundaries and communication between contexts via domain events — not as a single monolithic module.

Right now, **only the first bounded context (`menu_catalog`) is fully complete**, across every layer, from domain logic to a working HTTP API. The remaining pieces (e.g. order management, tables) haven't been started yet.

---

## Architecture

### Domain-Driven Design (DDD)

Each bounded context follows a **layered architecture** with a strict one-way dependency:

```
presentation → application → domain ← infrastructure
```

The **domain layer** is the core — it has no outward dependencies (no knowledge of FastAPI, SQLAlchemy, or HTTP). The **infrastructure layer** implements the abstract interfaces defined by the domain (repository pattern), not the other way around — this makes it possible to swap the ORM or database without touching business logic at all.

### Event-Driven Architecture (EDA)

Every aggregate root raises **domain events** when something business-significant happens (e.g. `MenuItemPriceUpdatedEvent`, `CategoryRenamedEvent`). Events are collected inside the aggregate and published by the Unit of Work **after** a successful commit, through an abstract `EventBus` interface. This lets future bounded contexts (e.g. Order Taking) react to menu changes without a direct dependency between them.

### Patterns used

- **Aggregate Roots** (`Category`, `MenuItem`) — sole entry point for changes, enforce invariants
- **Entities** (`MenuItemVariant`, `MenuItemModifier`) — mutable, identity-based equality, live within their aggregate's boundary
- **Value Objects** (`Money`, `CategoryId`, `MenuItemId`, etc.) — immutable, value-based equality
- **Domain Events** — record business-significant changes, fine-grained (a distinct event per distinct action, not generic "Updated" events)
- **Domain Exceptions** — a custom exception hierarchy instead of generic `ValueError`
- **Repository Pattern** — abstract interfaces in the domain, concrete SQLAlchemy implementations in infrastructure
- **Unit of Work** — atomic transactions + collecting and publishing domain events after commit
- **Command + Handler + Message Bus** (Cosmic Python / *Architecture Patterns with Python* style) — every write operation is an explicit, serializable command dataclass handled by a thin async handler, with the message bus dispatching by type
- **DTOs** — explicit aggregate → DTO conversion in the presentation layer, so the domain model is never exposed directly as an API response
- **Composition Root** — a single wiring point (engine, session factory, event bus) for dependency injection

---

## Current status: `menu_catalog` bounded context

The only bounded context that's complete. Covers: menu categories, items with a base price, variants (e.g. sizes), modifiers (e.g. extras), availability.

### Domain layer
```
domain/
├── aggregates/        # Category, MenuItem
├── entities/           # MenuItemVariant, MenuItemModifier
├── value_objects/      # Money, identifiers (CategoryId, MenuItemId, VariantId, ModifierId)
├── events/             # DomainEvent base + all fine-grained menu events + EventBus interface
├── exceptions/         # MenuCatalogError hierarchy
└── repositories/       # Abstract CategoryRepository, MenuItemRepository, UnitOfWork
```

### Application layer
```
application/
├── commands/           # Immutable dataclasses per write operation
├── handlers/           # Thin async orchestration — no business logic here
├── dtos/               # CategoryDTO, MenuItemDTO (+ nested VariantDTO/ModifierDTO)
└── message_bus.py      # Dispatches command → handler
```

### Infrastructure layer
```
infrastructure/
├── db/                 # SQLAlchemy declarative models + async session setup
├── repositories/        # Concrete SQLAlchemy implementations (explicit domain↔ORM mapping)
├── unit_of_work.py      # SqlAlchemyUnitOfWork
└── event_bus.py         # InMemoryEventBus (in-process pub/sub)
```

### Presentation layer
```
api/
├── routers/             # FastAPI routers: categories, menu-items (+ nested variants/modifiers)
├── schemas/              # Pydantic request models
├── error_handlers.py     # Domain exceptions → correct HTTP status codes (404/409/422/400)
└── dependencies.py       # UoW injection via the composition root
```

A fully working REST API sits on top of this context, with CORS enabled for local development testing.

---

## Tech stack & tooling

| Category | Choice |
|---|---|
| Language | Python 3.11+ (async/await throughout — repositories, UoW, event bus, handlers) |
| Web framework | FastAPI |
| ORM | SQLAlchemy 2.0 (async, declarative mapping) |
| Database (dev) | SQLite via `aiosqlite` |
| Type checking | mypy in **strict mode** |
| Linting | flake8 |
| Testing | pytest + pytest-asyncio |
| HTTP test client | httpx + asgi-lifespan (for API-level integration tests) |

### Testing strategy — two levels

1. **Unit tests (application layer)** — fake/in-memory implementations of the abstract repository/UoW/EventBus interfaces. No real database. These verify business logic correctness: the right events fire, the right exceptions are raised, commit is called correctly.
2. **Integration tests (infrastructure + API layer)** — a real SQLite engine (`StaticPool` to persist the in-memory database across a single test), verifying the actual domain↔ORM mapping (including nested variants/modifiers via `lazy="selectin"`), plus a full HTTP round-trip through `httpx.AsyncClient`.

---

## Running locally

```bash
pip install -r requirements.txt  # fastapi, sqlalchemy, aiosqlite, uvicorn, pytest, pytest-asyncio, httpx, asgi-lifespan
uvicorn src.main:app --reload
```

Database tables are created automatically on startup (`Base.metadata.create_all()` inside the FastAPI `lifespan`) — a development-only convenience, to be replaced with **Alembic migrations** before any production use.

```bash
mypy src
flake8 src
pytest
```

---

## Roadmap — what's missing

- [ ] Alembic migrations (replacing `create_all()`)
- [ ] Bounded context: **Order Taking** (orders, kitchen routing)
- [ ] Bounded context: **Floor & Tables** (dining room/table management)
- [ ] Cross-context communication via domain events (e.g. Order Taking listening to `MenuItemPriceUpdatedEvent`)
- [ ] Authentication/authorization
- [ ] Payments/receipts

directory tree:

```text
posGithub/
├── src/
│   ├── bounded_contexts/
│   │   ├── menu_catalog/
│   │   │   ├── api/
│   │   │   │   ├── routers/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── category_router.py
│   │   │   │   │   └── menu_item_router.py
│   │   │   │   ├── schemas/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── category_schemas.py
│   │   │   │   │   └── menu_item_schemas.py
│   │   │   │   ├── __init__.py
│   │   │   │   ├── dependencies.py
│   │   │   │   └── error_handlers.py
│   │   │   ├── application/
│   │   │   │   ├── commands/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── category_commands.py
│   │   │   │   │   └── menu_item_commands.py
│   │   │   │   ├── dtos/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── category_dto.py
│   │   │   │   │   └── menu_item_dto.py
│   │   │   │   ├── handlers/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── category_handlers.py
│   │   │   │   │   └── menu_item_handlers.py
│   │   │   │   ├── __init__.py
│   │   │   │   └── message_bus.py
│   │   │   ├── domain/
│   │   │   │   ├── aggregates/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── category.py
│   │   │   │   │   └── menu_item.py
│   │   │   │   ├── entities/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── menu_item_modifier.py
│   │   │   │   │   └── menu_item_variant.py
│   │   │   │   ├── events/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── event_bus.py
│   │   │   │   │   └── menu_events.py
│   │   │   │   ├── exceptions/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── menu_exceptions.py
│   │   │   │   ├── repositories/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── category_repository.py
│   │   │   │   │   ├── menu_item_repository.py
│   │   │   │   │   └── unit_of_work.py
│   │   │   │   ├── value_objects/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── identifiers.py
│   │   │   │   │   └── money.py
│   │   │   │   └── __init__.py
│   │   │   ├── infrastructure/
│   │   │   │   ├── db/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── base.py
│   │   │   │   │   ├── models.py
│   │   │   │   │   └── session.py
│   │   │   │   ├── repositories/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── sqlalchemy_category_repository.py
│   │   │   │   │   └── sqlalchemy_menu_item_repository.py
│   │   │   │   ├── __init__.py
│   │   │   │   ├── event_bus.py
│   │   │   │   └── unit_of_work.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── composition_root.py
│   ├── config.py
│   └── main.py
├── tests/
│   ├── integration/
│   │   ├── bounded_contexts/
│   │   │   ├── menu_catalog/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── conftest.py
│   │   │   │   ├── test_api_category_flow.py
│   │   │   │   ├── test_sqlalchemy_category_repository.py
│   │   │   │   └── test_sqlalchemy_menu_item_repository.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── unit/
│   │   ├── bounded_contexts/
│   │   │   ├── menu_catalog/
│   │   │   │   ├── application/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── fakes.py
│   │   │   │   │   └── test_category_handlers.py
│   │   │   │   ├── domain/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── test_category.py
│   │   │   │   │   ├── test_menu_item.py
│   │   │   │   │   ├── test_money.py
│   │   │   │   │   └── test_unit_of_work.py
│   │   │   │   ├── __init__.py
│   │   │   │   └── fakes.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   └── __init__.py
├── .flake8
├── .gitignore
├── mypy.ini
├── pytest.ini
└── requirements.txt
```