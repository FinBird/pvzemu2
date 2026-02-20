from collections import deque
from typing import TypeVar, Generic, Iterator, Optional, Any

T = TypeVar('T')


class ObjList(Generic[T]):
    __slots__ = ('_objects', '_free_ids', '_next_id', '_use_recycle')

    def __init__(self, use_recycle: bool = False):
        self._objects: dict[int, T] = {}

        # If ID reuse is needed (like C++), enable use_recycle
        self._use_recycle = use_recycle
        self._free_ids: deque[int] = deque()
        self._next_id = 0

    def add(self, obj: T) -> int:
        """
        Add an object and return its assigned ID.
        The object will have its .id attribute set if it exists.
        """
        if self._use_recycle and self._free_ids:
            obj_id = self._free_ids.popleft()
        else:
            obj_id = self._next_id
            self._next_id += 1

        self._objects[obj_id] = obj

        if hasattr(obj, 'id'):
            object.__setattr__(obj, 'id', obj_id)

        return obj_id

    def get(self, obj_id: int) -> Optional[T]:
        """O(1) retrieval"""
        return self._objects.get(obj_id)

    def remove(self, obj_id: int) -> None:
        """O(1) removal"""
        if obj_id in self._objects:
            del self._objects[obj_id]
            if self._use_recycle:
                self._free_ids.append(obj_id)

    def remove_obj(self, obj: T) -> None:
        """Remove by object instance (requires object to have .id)"""
        if hasattr(obj, 'id'):
            self.remove(obj.id)

    def clear(self) -> None:
        self._objects.clear()
        self._free_ids.clear()
        self._next_id = 0

    def __iter__(self) -> Iterator[T]:
        """Iterate over active objects directly."""
        return iter(self._objects.values())

    def __len__(self) -> int:
        return len(self._objects)

    def to_json_list(self) -> list[dict[str, Any]]:
        """Helper to generate list of dicts for JSON serialization"""
        # Sort by ID to ensure deterministic output order if needed
        # return [obj.to_dict() for _, obj in sorted(self._objects.items())]
        # For performance, just values is fine, but for strict C++ parity maybe sort?
        # C++ iterates array 0..N.
        # Let's sort by ID to be safe and deterministic.
        return [obj.to_dict() for _, obj in sorted(self._objects.items())]
