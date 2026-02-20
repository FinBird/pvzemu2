from dataclasses import dataclass, field
from typing import Any

from pvzemu2.enums import (
    ProjectileType,
    ProjectileMotionType,
    DamageFlags,
    ZombieType,
    ZombieAccessoriesType2
)
from pvzemu2.geometry import Rect
from pvzemu2.objects.base import get_uuid
from pvzemu2.objects.zombie import Zombie


@dataclass(slots=True)
class Projectile:
    type: ProjectileType
    row: int
    x: float
    y: float

    id: int = field(init=False)
    motion_type: ProjectileMotionType = ProjectileMotionType.STRAIGHT

    int_x: int = 0
    int_y: int = 0
    shadow_y: float = 0.0

    dx: float = 0.0
    dy1: float = 0.0
    dy2: float = 0.0
    ddy: float = 0.0
    dddy: float = 0.0

    # Attack box structure matching C++ (only width and height)
    attack_box_width: int = 40
    attack_box_height: int = 40
    flags: int = 0  # 使用 AttackFlags.value

    time_since_created: int = 0
    countdown: int = 0
    last_torchwood_col: int = -1
    target: int = -1  # 目标僵尸 ID，匹配 C++ 的 target 字段

    cannon_x: float = 0.0
    cannon_row: int = 0

    is_disappeared: bool = False
    is_visible: bool = True

    # DAMAGE array matching C++ (14 elements)
    DAMAGE = [20, 20, 40, 80, 20, 80, 40, 20, 20, 75, 20, 300, 40, 0]

    @property
    def is_freeable(self) -> bool:
        return self.is_disappeared

    def __post_init__(self) -> None:
        self.id = get_uuid()
        self.int_x = int(self.x)
        self.int_y = int(self.y)

    def get_attack_box(self) -> Rect:
        """获取攻击判定框，匹配 C++ 实现"""
        r = Rect(0, 0, 0, 0)

        if self.type in (ProjectileType.PEA, ProjectileType.SNOW_PEA):
            r.x = self.int_x - 15
            r.y = self.int_y
            r.width = self.attack_box_width + 15
            r.height = self.attack_box_height

        elif self.type in (ProjectileType.WINTERMELON, ProjectileType.MELON):
            r.x = self.int_x + 20
            r.y = self.int_y
            r.width = 60
            r.height = self.attack_box_height

        elif self.type == ProjectileType.FIRE_PEA:
            r.x = self.int_x
            r.y = self.int_y
            r.height = self.attack_box_height
            r.width = self.attack_box_width - 10

        elif self.type == ProjectileType.CACTUS:
            r.x = self.int_x - 25
            r.y = self.int_y
            r.width = self.attack_box_width + 25
            r.height = self.attack_box_height

        elif self.type == ProjectileType.COB_CANNON:
            r.x = self.attack_box_width // 2 + self.int_x - 115
            r.y = self.attack_box_height // 2 + self.int_y - 115
            r.height = 230
            r.width = 230

        else:
            r.x = self.int_x
            r.y = self.int_y
            r.width = self.attack_box_width
            r.height = self.attack_box_height

        return r

    def get_flags_with_zombie(self, z: "Zombie") -> int:
        flags = 0

        # Match C++ logic exactly
        if (self.type == ProjectileType.FIRE_PEA and
                (z.type == ZombieType.CATAPULT or
                 z.type == ZombieType.ZOMBONI or
                 z.accessory_2_type == ZombieAccessoriesType2.SCREEN_DOOR or
                 z.accessory_2_type == ZombieAccessoriesType2.LADDER) and
                (self.motion_type == ProjectileMotionType.PARABOLA or
                 self.motion_type == ProjectileMotionType.LEFT_STRAIGHT or
                 self.motion_type == ProjectileMotionType.STARFRUIT)):
            flags = DamageFlags.BYPASSES_SHIELD
        else:
            flags = DamageFlags.DAMAGE_HITS_SHIELD_AND_BODY

        if self.type in (ProjectileType.SNOW_PEA, ProjectileType.WINTERMELON):
            flags |= DamageFlags.DAMAGE_FREEZE

        return flags

    def to_dict(self) -> dict[str, Any]:
        attack_box = self.get_attack_box()
        attack_box_dict = {
            "x": attack_box.x,
            "y": attack_box.y,
            "width": attack_box.width,
            "height": attack_box.height
        }

        return {
            "id": self.id,
            "type": self.type.name.lower(),
            "motion_type": self.motion_type.name.lower(),
            "int_x": self.int_x,
            "int_y": self.int_y,
            "row": self.row,
            "y": self.y,
            "x": self.x,
            "shadow_y": self.shadow_y,
            "dx": self.dx,
            "dy1": self.dy1,
            "dy2": self.dy2,
            "ddy": self.ddy,
            "dddy": self.dddy,
            "attack_box": attack_box_dict,
            "flags": {
                "disable_ballon_pop": bool(self.flags & DamageFlags.NO_LEAVE_BODY),
                "ignore_accessory_2": bool(self.flags & DamageFlags.BYPASSES_SHIELD),
                "not_reduce": bool(self.flags & DamageFlags.DAMAGE_HITS_SHIELD_AND_BODY),
                "no_flash": bool(self.flags & DamageFlags.NO_FLASH),
                "slow_effect": bool(self.flags & DamageFlags.DAMAGE_FREEZE),
                "spike": bool(self.flags & DamageFlags.SPIKE),
            },
            "time_since_created": self.time_since_created,
            "countdown": self.countdown,
            "last_torchwood_col": self.last_torchwood_col,
            "cannon_x": self.cannon_x,
            "cannon_row": self.cannon_row,
            "target": self.target if self.target != -1 else None,
            "is_visible": self.is_visible,
            "is_disappeared": self.is_disappeared,
        }
