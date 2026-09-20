# api/schemas/menu_item_schemas.py

from pydantic import BaseModel, Field


class CreateMenuItemRequest(BaseModel):
    name: str = Field(min_length=1)
    price_amount: str
    currency: str
    category_id: str


class RenameMenuItemRequest(BaseModel):
    new_name: str = Field(min_length=1)


class RecategorizeMenuItemRequest(BaseModel):
    new_category_id: str


class UpdateMenuItemPriceRequest(BaseModel):
    new_price_amount: str
    currency: str


class ChangeMenuItemAvailabilityRequest(BaseModel):
    is_available: bool


class AddMenuItemVariantRequest(BaseModel):
    name: str = Field(min_length=1)
    price_modifier_amount: str
    currency: str


class UpdateMenuItemVariantRequest(BaseModel):
    new_name: str = Field(min_length=1)
    new_price_modifier_amount: str
    currency: str


class AddMenuItemModifierRequest(BaseModel):
    name: str = Field(min_length=1)
    price_addition_amount: str
    currency: str


class UpdateMenuItemModifierRequest(BaseModel):
    new_name: str = Field(min_length=1)
    new_price_addition_amount: str
    currency: str
