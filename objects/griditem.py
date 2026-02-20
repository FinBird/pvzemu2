from dataclasses import dataclass, field
from typing import Any

from pvzemu2.enums import GridItemType
from pvzemu2.objects.base import get_uuid


@dataclass(slots=True)
class GridItem:
    type: GridItemType
    row: int
    col: int

    id: int = field(init=False)

    countdown: int = 0
    is_disappeared: bool = False

    def __post_init__(self) -> None:
        self.id = get_uuid()

    @property
    def is_freeable(self) -> bool:
        return self.is_disappeared

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.name.lower(),
            "col": self.col,
            "row": self.row,
            "countdown": self.countdown,
            "is_disappeared": self.is_disappeared
        }
