# api/dependencies.py

from fastapi import Depends

from ....composition_root import CompositionRoot, get_composition_root
from ..domain.repositories.unit_of_work import (
    UnitOfWork,
)


def get_uow(
    root: CompositionRoot = Depends(get_composition_root),
) -> UnitOfWork:
    return root.new_uow()
