# api/schemas/category_schemas.py

from pydantic import BaseModel, Field


class CreateCategoryRequest(BaseModel):
    name: str = Field(min_length=1)
    display_order: int


class RenameCategoryRequest(BaseModel):
    new_name: str = Field(min_length=1)


class ReorderCategoryRequest(BaseModel):
    new_position: int
