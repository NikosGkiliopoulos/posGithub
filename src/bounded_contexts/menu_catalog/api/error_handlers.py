# api/error_handlers.py

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from ..domain.exceptions.menu_exceptions import (
    CategoryNotEmptyError,
    CategoryNotFoundError,
    CurrencyMismatchError,
    DuplicateCategoryNameError,
    DuplicateMenuItemNameError,
    DuplicateModifierNameError,
    DuplicateVariantNameError,
    EmptyCategoryNameError,
    EmptyMenuItemNameError,
    InvalidCategoryNameError,
    InvalidPriceError,
    MenuItemNotFoundError,
    ModifierNotFoundError,
    VariantNotFoundError,
)

NOT_FOUND_ERRORS: tuple[type[Exception], ...] = (
    CategoryNotFoundError,
    MenuItemNotFoundError,
    VariantNotFoundError,
    ModifierNotFoundError,
)

CONFLICT_ERRORS: tuple[type[Exception], ...] = (
    DuplicateCategoryNameError,
    DuplicateMenuItemNameError,
    DuplicateVariantNameError,
    DuplicateModifierNameError,
    CategoryNotEmptyError,
)

VALIDATION_ERRORS: tuple[type[Exception], ...] = (
    EmptyCategoryNameError,
    EmptyMenuItemNameError,
    InvalidCategoryNameError,
    InvalidPriceError,
    CurrencyMismatchError,
)


async def _not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


async def _conflict_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


async def _validation_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


def register_error_handlers(app: FastAPI) -> None:
    for exc_type in NOT_FOUND_ERRORS:
        app.add_exception_handler(exc_type, _not_found_handler)
    for exc_type in CONFLICT_ERRORS:
        app.add_exception_handler(exc_type, _conflict_handler)
    for exc_type in VALIDATION_ERRORS:
        app.add_exception_handler(exc_type, _validation_handler)
