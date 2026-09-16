# application/commands/category_commands.py

from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class CreateCategory:
    name: str
    display_order: int


@dataclass(frozen=True, kw_only=True)
class RenameCategory:
    category_id: str
    new_name: str


@dataclass(frozen=True, kw_only=True)
class ReorderCategory:
    category_id: str
    new_position: int


@dataclass(frozen=True, kw_only=True)
class RemoveCategory:
    category_id: str
