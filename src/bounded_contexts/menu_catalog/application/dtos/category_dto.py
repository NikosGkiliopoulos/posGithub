# application/dtos/category_dto.py

from dataclasses import dataclass

from ...domain.aggregates.category import Category


@dataclass(frozen=True)
class CategoryDTO:
    category_id: str
    name: str
    display_order: int

    @classmethod
    def from_aggregate(cls, category: Category) -> "CategoryDTO":
        return cls(
            category_id=str(category.category_id.value),
            name=category.name,
            display_order=category.display_order,
        )
