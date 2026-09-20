# api/routers/category_router.py

from fastapi import APIRouter, Depends

from ...application import message_bus
from ...application.commands.category_commands import (
    CreateCategory,
    RemoveCategory,
    RenameCategory,
    ReorderCategory,
)
from ...application.dtos.category_dto import CategoryDTO
from ...domain.repositories.unit_of_work import (
    UnitOfWork,
)
from ..dependencies import get_uow
from ..schemas.category_schemas import (
    CreateCategoryRequest,
    RenameCategoryRequest,
    ReorderCategoryRequest,
)

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("", status_code=201, response_model=CategoryDTO)
async def create_category(
    payload: CreateCategoryRequest,
    uow: UnitOfWork = Depends(get_uow),
) -> CategoryDTO:
    command = CreateCategory(name=payload.name, display_order=payload.display_order)
    category = await message_bus.handle(command, uow)
    return CategoryDTO.from_aggregate(category)


@router.get("", response_model=list[CategoryDTO])
async def list_categories(
    uow: UnitOfWork = Depends(get_uow),
) -> list[CategoryDTO]:
    async with uow:
        categories = await uow.categories.find_all()
    return [CategoryDTO.from_aggregate(c) for c in categories]


@router.patch("/{category_id}/rename", response_model=None, status_code=204)
async def rename_category(
    category_id: str,
    payload: RenameCategoryRequest,
    uow: UnitOfWork = Depends(get_uow),
) -> None:
    command = RenameCategory(category_id=category_id, new_name=payload.new_name)
    await message_bus.handle(command, uow)


@router.patch("/{category_id}/reorder", response_model=None, status_code=204)
async def reorder_category(
    category_id: str,
    payload: ReorderCategoryRequest,
    uow: UnitOfWork = Depends(get_uow),
) -> None:
    command = ReorderCategory(
        category_id=category_id, new_position=payload.new_position
    )
    await message_bus.handle(command, uow)


@router.delete("/{category_id}", status_code=204)
async def remove_category(
    category_id: str,
    uow: UnitOfWork = Depends(get_uow),
) -> None:
    command = RemoveCategory(category_id=category_id)
    await message_bus.handle(command, uow)
