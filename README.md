# orderPOS

Point-of-Sale σύστημα για εστιατόρια, χτισμένο με **Domain-Driven Design (DDD)** και **Event-Driven Architecture (EDA)** σε Python.

## Όραμα

Το orderPOS στοχεύει να καλύψει ολόκληρο τον κύκλο λειτουργίας ενός εστιατορίου: διαχείριση μενού (κατηγορίες, πιάτα, variants, modifiers), διαχείριση τραπεζιών/χώρου εστιατορίου, λήψη και δρομολόγηση παραγγελιών προς την κουζίνα, και εν τέλει πληρωμές/αποδείξεις. Κάθε λειτουργικό κομμάτι σχεδιάζεται ως ξεχωριστό **bounded context**, με σαφή όρια και επικοινωνία μεταξύ τους μέσω domain events — όχι ως ένα ενιαίο monolith modules.

Αυτή τη στιγμή, **μόνο το πρώτο bounded context (`menu_catalog`) είναι πλήρως ολοκληρωμένο**, σε όλα τα layers, από domain logic μέχρι λειτουργικό HTTP API. Τα υπόλοιπα κομμάτια (π.χ. διαχείριση παραγγελιών, τραπέζια) δεν έχουν ξεκινήσει ακόμα.

---

## Αρχιτεκτονική

### Domain-Driven Design (DDD)

Κάθε bounded context ακολουθεί **layered architecture** με αυστηρή μονόδρομη εξάρτηση:

```
presentation → application → domain ← infrastructure
```

Το **domain layer** είναι ο πυρήνας — δεν έχει καμία εξάρτηση προς τα έξω (καμία γνώση για FastAPI, SQLAlchemy, ή HTTP). Το **infrastructure layer** υλοποιεί τα abstract interfaces που ορίζει το domain (repository pattern), όχι το αντίστροφο — αυτό επιτρέπει να αλλάξεις ORM ή database χωρίς να αγγίξεις καθόλου τη business logic.

### Event-Driven Architecture (EDA)

Κάθε aggregate root παράγει **domain events** όταν συμβαίνει κάτι σημαντικό στο business (π.χ. `MenuItemPriceUpdatedEvent`, `CategoryRenamedEvent`). Τα events μαζεύονται μέσα στο aggregate και δημοσιεύονται από το Unit of Work **μετά** από επιτυχές commit, μέσω ενός abstract `EventBus` interface. Αυτό επιτρέπει σε μελλοντικά bounded contexts (π.χ. Order Taking) να αντιδρούν σε αλλαγές του μενού χωρίς άμεση εξάρτηση μεταξύ τους.

### Patterns που χρησιμοποιήθηκαν

- **Aggregate Roots** (`Category`, `MenuItem`) — μοναδικό entry point για αλλαγές, εγγυώνται invariants
- **Entities** (`MenuItemVariant`, `MenuItemModifier`) — mutable, identity-based equality, ζουν μέσα στο aggregate boundary τους
- **Value Objects** (`Money`, `CategoryId`, `MenuItemId`, κλπ) — immutable, ισότητα βάσει τιμής
- **Domain Events** — καταγραφή business-significant αλλαγών, fine-grained (ξεχωριστό event ανά διακριτή ενέργεια, όχι γενικά "Updated" events)
- **Domain Exceptions** — ιεραρχία custom exceptions αντί για γενικά `ValueError`
- **Repository Pattern** — abstract interfaces στο domain, concrete SQLAlchemy υλοποιήσεις στο infrastructure
- **Unit of Work** — atomic transactions + συγκέντρωση και δημοσίευση domain events μετά το commit
- **Command + Handler + Message Bus** (στυλ Cosmic Python / *Architecture Patterns with Python*) — κάθε write operation περνάει ως explicit, serializable command dataclass σε thin async handler, με το message bus να κάνει dispatch by type
- **DTOs** — explicit μετατροπή aggregate → DTO στο presentation layer, ώστε το domain model να μην εκτίθεται ποτέ απευθείας ως API response
- **Composition Root** — ένα σημείο wiring (engine, session factory, event bus) για dependency injection

---

## Τρέχουσα κατάσταση: `menu_catalog` bounded context

Το μοναδικό ολοκληρωμένο bounded context. Καλύπτει: κατηγορίες μενού, πιάτα με βασική τιμή, variants (π.χ. μεγέθη), modifiers (π.χ. extras), διαθεσιμότητα.

### Domain layer
```
domain/
├── aggregates/        # Category, MenuItem
├── entities/           # MenuItemVariant, MenuItemModifier
├── value_objects/      # Money, identifiers (CategoryId, MenuItemId, VariantId, ModifierId)
├── events/             # DomainEvent base + όλα τα fine-grained menu events + EventBus interface
├── exceptions/         # Ιεραρχία MenuCatalogError
└── repositories/       # Abstract CategoryRepository, MenuItemRepository, UnitOfWork
```

### Application layer
```
application/
├── commands/           # Immutable dataclasses ανά write operation
├── handlers/           # Thin async orchestration — καμία business logic εδώ
├── dtos/               # CategoryDTO, MenuItemDTO (+ nested VariantDTO/ModifierDTO)
└── message_bus.py      # Dispatch command → handler
```

### Infrastructure layer
```
infrastructure/
├── db/                 # SQLAlchemy declarative models + async session setup
├── repositories/        # Concrete SQLAlchemy υλοποιήσεις (explicit domain↔ORM mapping)
├── unit_of_work.py      # SqlAlchemyUnitOfWork
└── event_bus.py         # InMemoryEventBus (in-process pub/sub)
```

### Presentation layer
```
api/
├── routers/             # FastAPI routers: categories, menu-items (+ nested variants/modifiers)
├── schemas/              # Pydantic request models
├── error_handlers.py     # Domain exceptions → σωστά HTTP status codes (404/409/422/400)
└── dependencies.py       # UoW injection μέσω composition root
```

Πλήρες λειτουργικό REST API πάνω από αυτό το context, με CORS ενεργοποιημένο για τοπικό development testing.

---

## Tech stack & εργαλεία

| Κατηγορία | Επιλογή |
|---|---|
| Γλώσσα | Python 3.11+ (async/await παντού — repositories, UoW, event bus, handlers) |
| Web framework | FastAPI |
| ORM | SQLAlchemy 2.0 (async, declarative mapping) |
| Database (dev) | SQLite μέσω `aiosqlite` |
| Type checking | mypy σε **strict mode** |
| Linting | flake8 |
| Testing | pytest + pytest-asyncio |
| HTTP test client | httpx + asgi-lifespan (για API-level integration tests) |

### Testing strategy — δύο επίπεδα

1. **Unit tests (application layer)** — fakes/in-memory υλοποιήσεις των abstract repository/UoW/EventBus interfaces. Καμία πραγματική βάση. Ελέγχουν business logic ορθότητας: σωστά events, σωστά exceptions, commit καλείται σωστά.
2. **Integration tests (infrastructure + API layer)** — πραγματικό SQLite engine (`StaticPool` για in-memory persistence μέσα στο test), επιβεβαιώνουν το πραγματικό domain↔ORM mapping (συμπεριλαμβανομένων nested variants/modifiers μέσω `lazy="selectin"`), και πλήρες HTTP round-trip μέσω `httpx.AsyncClient`.

---

## Τρέξιμο τοπικά

```bash
pip install -r requirements.txt  # fastapi, sqlalchemy, aiosqlite, uvicorn, pytest, pytest-asyncio, httpx, asgi-lifespan
uvicorn src.main:app --reload
```

Τα database tables δημιουργούνται αυτόματα στο startup (`Base.metadata.create_all()` μέσα στο FastAPI `lifespan`) — προσωρινή λύση για development, θα αντικατασταθεί από **Alembic migrations** πριν οποιαδήποτε production χρήση.

```bash
mypy src
flake8 src
pytest
```

---

## Roadmap — τι λείπει

- [ ] Alembic migrations (αντί για `create_all()`)
- [ ] Bounded context: **Order Taking** (παραγγελίες, δρομολόγηση προς κουζίνα)
- [ ] Bounded context: **Floor & Tables** (διαχείριση τραπεζιών/χώρου εστιατορίου)
- [ ] Επικοινωνία μεταξύ contexts μέσω domain events (π.χ. Order Taking ακούει `MenuItemPriceUpdatedEvent`)
- [ ] Authentication/authorization
- [ ] Πληρωμές/αποδείξεις


Πλήρης δομή των φακέλων και των αρχείων του project σε μορφή directory tree:

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