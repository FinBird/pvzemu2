from dataclasses import dataclass
from enum import IntEnum
from typing import Any


class ReanimateType(IntEnum):
    REPEAT = 0
    ONCE = 1


@dataclass(slots=True)
class ReanimFrameStatus:
    frame: int = 0
    next_frame: int = 0
    frame_progress: float = 0.0


@dataclass(slots=True)
class Reanimate:
    fps: float = 0.0
    prev_fps: float = 0.0
    begin_frame: int = 0
    n_frames: int = 0
    n_repeated: int = 0
    progress: float = 0.0
    prev_progress: float = 0.0
    type: ReanimateType = ReanimateType.REPEAT

    def is_in_progress(self, p: float) -> bool:
        if self.prev_progress <= self.progress:
            return self.prev_progress <= p < self.progress
        else:
            return self.prev_progress <= p or p < self.progress

    def to_dict(self) -> dict[str, Any]:
        return {
            "fps": self.fps,
            "prev_fps": self.prev_fps,
            "begin_frame": self.begin_frame,
            "n_frames": self.n_frames,
            "n_repeated": self.n_repeated,
            "progress": self.progress,
            "prev_progress": self.prev_progress,
            "type": "once" if self.type == ReanimateType.ONCE else "repeat"
        }

    def get_frame_status(self) -> ReanimFrameStatus:
        current_frame = self.progress * (self.n_frames - 1) + self.begin_frame
        floored_current_frame = int(current_frame)

        rfs = ReanimFrameStatus()
        rfs.frame_progress = current_frame - floored_current_frame

        end_frame = self.begin_frame + self.n_frames - 1

        if floored_current_frame < end_frame:
            rfs.frame = floored_current_frame
            rfs.next_frame = floored_current_frame + 1
        else:
            rfs.frame = end_frame
            rfs.next_frame = end_frame

        return rfs


_uuid_counter = 0


def get_uuid() -> int:
    global _uuid_counter
    _uuid_counter += 1
    return _uuid_counter
