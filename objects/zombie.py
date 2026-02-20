from dataclasses import dataclass, field
from typing import Any

from pvzemu2.enums import ZombieType, ZombieStatus, ZombieAction, ZombieAccessoriesType2, ZombieAccessoriesType1, \
    ZombieReanimName
from pvzemu2.geometry import Rect
from pvzemu2.objects.base import Reanimate, get_uuid
from pvzemu2.objects.zombie_reanim_data import COMMON_ZOMBIE_GROUND
from pvzemu2.objects.zombie_reanim_data import get_zombie_reanim_data, get_reanim_frame_data, has_reanim


@dataclass(slots=True)
class ZombieCountdown:
    butter: int = 0
    freeze: int = 0
    slow: int = 0
    action: int = 0
    dead: int = 0

    def to_dict(self) -> dict[str, int]:
        return {
            'butter': self.butter,
            'freeze': self.freeze,
            'slow': self.slow,
            'action': self.action,
            'dead': self.dead

        }


@dataclass(slots=True)
class ZombieGarlicTick:
    a: int = 0
    b: int = 0
    c: int = 0


@dataclass(slots=True)
class Zombie:
    type: ZombieType
    row: int

    x: float
    y: float

    id: int = field(init=False)

    int_x: int = 0
    int_y: int = 0
    dx: float = 0.0
    dy: float = 0.0
    d2y: float = 0.0

    hp: int = 270
    max_hp: int = 270

    status: ZombieStatus = ZombieStatus.WALKING
    reanimate: Reanimate = field(default_factory=Reanimate)
    countdown: ZombieCountdown = field(default_factory=ZombieCountdown)

    # Hit box structure matching C++
    hit_box_x: int = 0
    hit_box_y: int = 0
    hit_box_width: int = 0
    hit_box_height: int = 0
    hit_box_offset_x: int = 0
    hit_box_offset_y: int = 0

    # Attack box structure matching C++
    attack_box_x: int = 0
    attack_box_y: int = 0
    attack_box_width: int = 0
    attack_box_height: int = 0

    is_eating: bool = False
    is_dead: bool = False
    is_hypno: bool = False
    master_id: int | None = None
    partners: list[int] = field(default_factory=lambda: [-1, -1, -1, -1])  # Match C++ std::array<int, 4>

    time_since_spawn: int = 0
    time_since_ate_garlic: int = 0
    has_eaten_garlic: bool = False
    garlic_tick: ZombieGarlicTick = field(default_factory=ZombieGarlicTick)

    action: ZombieAction = ZombieAction.NONE
    is_in_water: bool = False
    is_blown: bool = False
    is_not_dying: bool = True
    ladder_col: int = -1

    accessory_1_type: ZombieAccessoriesType1 = ZombieAccessoriesType1.NONE
    accessory_1_hp: int = 0
    accessory_1_max_hp: int = 0

    accessory_2_type: ZombieAccessoriesType2 = ZombieAccessoriesType2.NONE
    accessory_2_hp: int = 0
    accessory_2_max_hp: int = 0

    has_item_or_walk_left: bool = False
    has_balloon: bool = False
    spawn_wave: int = 0
    bungee_col: int = -1
    bungee_target: int = -1

    # Union field for catapult or dancing zombie
    catapult_or_jackson: int = 0

    # Ground animation data pointer (simulated as None in Python)
    _ground: Any = None

    # Speed caching for slowdown effects
    _original_dx: float | None = None

    def __post_init__(self) -> None:
        self.id = get_uuid()
        self.init_reanim()

    def init_reanim(self) -> None:
        self.reanimate.prev_progress = -1
        n_frames, fps = get_zombie_reanim_data(self.type)
        if n_frames > 0:
            self.reanimate.n_frames = n_frames
            self.reanimate.fps = fps
        # 将 _ground 数组绑定给对应的僵尸，以便实现精准的像素级位移
        if self.type in (ZombieType.ZOMBIE, ZombieType.CONE_HEAD, ZombieType.BUCKET_HEAD,
                         ZombieType.SCREEN_DOOR, ZombieType.FLAG, ZombieType.DUCKY_TUBE):
            self._ground = COMMON_ZOMBIE_GROUND
        else:
            self._ground = COMMON_ZOMBIE_GROUND  # 作为替补数据防止崩溃

    def set_reanim_frame(self, name: ZombieReanimName) -> None:
        begin_frame, n_frames = get_reanim_frame_data(self.type, name)
        if n_frames > 0:
            self.reanimate.begin_frame = begin_frame
            self.reanimate.n_frames = n_frames

    def has_reanim(self, name: ZombieReanimName) -> bool:
        return has_reanim(self.type, name)

    def is_flying_or_falling(self) -> bool:
        return self.status in (ZombieStatus.BALLOON_FLYING, ZombieStatus.BALLOON_FALLING)

    def is_walk_right(self) -> bool:
        if self.is_hypno:
            return True

        if self.type == ZombieType.DIGGER:
            if self.status in (ZombieStatus.DIGGER_DRILL, ZombieStatus.DIGGER_DIZZY, ZombieStatus.DIGGER_WALK_RIGHT):
                return True
            if self.has_death_status():
                return self.has_item_or_walk_left
            return False

        return self.type == ZombieType.YETI and not self.has_item_or_walk_left

    def has_death_status(self) -> bool:
        return self.status in (
            ZombieStatus.DYING,
            ZombieStatus.DYING_FROM_INSTANT_KILL,
            ZombieStatus.DYING_FROM_LAWNMOWER
        )

    def has_pogo_status(self) -> bool:
        return ZombieStatus.POGO_WITH_STICK <= self.status <= 28

    def can_be_slowed(self) -> bool:
        if self.type == ZombieType.ZOMBONI or self.is_dead:
            return False

        return (not self.has_death_status() and
                self.status not in (
                    ZombieStatus.DIGGER_DIG,
                    ZombieStatus.DIGGER_DRILL,
                    ZombieStatus.DIGGER_LOST_DIG,
                    ZombieStatus.DIGGER_LANDING,
                    ZombieStatus.RISING_FROM_GROUND,
                    ZombieStatus.DANCING_DANCER_SPAWNING
                ) and not self.is_hypno)

    def can_be_freezed(self) -> bool:
        if not self.can_be_slowed():
            return False

        return (self.status not in (
            ZombieStatus.POLE_VALUTING_JUMPING,
            ZombieStatus.DOLPHIN_JUMP_IN_POOL,
            ZombieStatus.DOLPHIN_IN_JUMP,
            ZombieStatus.SNORKEL_JUMP_IN_THE_POOL,
            ZombieStatus.IMP_FLYING,
            ZombieStatus.IMP_LANDING
        ) and not self.is_flying_or_falling() and
                int(self.status) != 19 and
                not (ZombieStatus.POGO_WITH_STICK <= self.status <= ZombieStatus.POGO_JUMP_ACROSS) and
                (self.type != ZombieType.BUNGEE or self.status == ZombieStatus.BUNGEE_IDLE_AFTER_DROP))

    def get_height_bias(self) -> float:
        if self.status == ZombieStatus.RISING_FROM_GROUND:
            if self.is_in_water:
                return -self.dy
            else:
                return -self.dy + min(self.countdown.action, 40)

        if self.type == ZombieType.DOLPHIN_RIDER:
            match self.status:
                case ZombieStatus.DOLPHIN_JUMP_IN_POOL:
                    if 0.56 <= self.reanimate.progress <= 0.64999998:
                        return 0.0
                    elif self.reanimate.progress >= 0.75:
                        return -self.dy - 10
                    else:
                        return -200.0
                case ZombieStatus.DOLPHIN_RIDE:
                    if self.action == ZombieAction.CAUGHT_BY_KELP:
                        return -self.dy - 15
                    else:
                        return -self.dy - 10
                case ZombieStatus.DOLPHIN_IN_JUMP:
                    if self.reanimate.progress <= 0.05999999865889549:
                        return -self.dy - 10
                    elif 0.5 <= self.reanimate.progress <= 0.75999999:
                        return -13.0
                    else:
                        return -200.0
                case ZombieStatus.DYING:
                    return 44 - self.dy
                case ZombieStatus.DOLPHIN_WALK_IN_POOL:
                    if self.action == ZombieAction.CAUGHT_BY_KELP:
                        return 36 - self.dy
                    else:
                        return -200.0
                case ZombieStatus.DOLPHIN_WALK_WITH_DOLPHIN | ZombieStatus.DOLPHIN_WALK_WITHOUT_DOLPHIN:
                    if self.action == ZombieAction.LEAVING_POOL:
                        return -self.dy
                    else:
                        return -200.0
                case _:
                    return -200.0

        if self.type == ZombieType.SNORKEL:
            if self.status == ZombieStatus.SNORKEL_JUMP_IN_THE_POOL and self.reanimate.progress >= 0.800000011920929:
                return -10.0
            elif self.is_in_water:
                return -self.dy - 5
            else:
                return -200.0
        elif self.is_in_water:
            if self.is_eating:
                return -self.dy
            else:
                return -self.dy - 7

        if self.status == ZombieStatus.DANCING_DANCER_SPAWNING:
            return -self.dy

        if (self.status in (ZombieStatus.DIGGER_DRILL, ZombieStatus.DIGGER_LANDING) and
                self.countdown.action > 20):
            return -self.dy

        return -200.0

    def get_hit_box_rect(self) -> Rect:
        # Start with hit box values
        rect_x = self.hit_box_x
        rect_y = self.hit_box_y
        rect_width = self.hit_box_width
        rect_height = self.hit_box_height

        # Apply mirroring for walk-right zombies
        if self.is_walk_right():
            rect_x = self.hit_box_offset_x - rect_width - self.hit_box_x

        # Convert to absolute coordinates
        rect_x += self.int_x
        rect_y += int(self.int_y - self.dy)

        # Apply height bias
        bias = self.get_height_bias()
        if bias > -100:
            rect_height -= int(bias)

        return Rect(rect_x, rect_y, rect_width, rect_height)

    def get_attack_box_rect(self) -> Rect:
        # Start with attack box values
        rect_x = self.attack_box_x
        rect_y = self.attack_box_y
        rect_width = self.attack_box_width
        rect_height = self.attack_box_height

        # Special cases for jumping zombies
        if self.status in (ZombieStatus.POLE_VALUTING_JUMPING, ZombieStatus.DOLPHIN_IN_JUMP):
            rect_x = -40
            rect_y = 0
            rect_width = 100
            rect_height = 115

        # Apply mirroring for walk-right zombies
        if self.is_walk_right():
            rect_x = self.hit_box_offset_x - rect_width - rect_x

        # Convert to absolute coordinates
        rect_x += self.int_x
        rect_y += int(self.int_y - self.dy)

        # Apply height bias
        bias = self.get_height_bias()
        if bias > -100:
            rect_height -= int(bias)

        return Rect(rect_x, rect_y, rect_width, rect_height)

    def get_dx_from_ground(self) -> float:
        """依据动画帧读取数组，计算精准的基础像素位移 dx"""
        if not self._ground or not self.has_reanim(ZombieReanimName._ground):
            return 0.0

        rfs = self.reanimate.get_frame_status()
        if rfs.frame >= len(self._ground) or rfs.next_frame >= len(self._ground):
            return 0.0

        return (self._ground[rfs.next_frame] - self._ground[rfs.frame]) * 0.01 * self.reanimate.fps

    def to_dict(self) -> dict[str, Any]:
        hit_box_dict = {
            "x": self.hit_box_x,
            "y": self.hit_box_y,
            "width": self.hit_box_width,
            "height": self.hit_box_height,
            "offset_x": self.hit_box_offset_x,
            "offset_y": self.hit_box_offset_y
        }

        attack_box_dict = {
            "x": self.attack_box_x,
            "y": self.attack_box_y,
            "width": self.attack_box_width,
            "height": self.attack_box_height
        }

        accessory_1_dict = {
            "type": self.accessory_1_type.name.lower(),
            "hp": self.accessory_1_hp,
            "max_hp": self.accessory_1_max_hp
        }

        accessory_2_dict = {
            "type": self.accessory_2_type.name.lower(),
            "hp": self.accessory_2_hp,
            "max_hp": self.accessory_2_max_hp
        }

        garlic_tick_dict = {
            "a": self.garlic_tick.a,
            "b": self.garlic_tick.b,
            "c": self.garlic_tick.c
        }

        result = {
            "id": self.id,
            "type": self.type.name.lower(),
            "status": self.status.name.lower(),
            "x": self.x,
            "y": self.y,
            "dx": self.dx,
            "dy": self.dy,
            "d2y": self.d2y,
            "int_x": self.int_x,
            "int_y": self.int_y,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "row": self.row,
            "reanimate": self.reanimate.to_dict(),
            "countdown": self.countdown.to_dict(),
            "hit_box": hit_box_dict,
            "attack_box": attack_box_dict,
            "abs_hit_box": self.get_hit_box_rect().to_dict(),
            "abs_attack_box": self.get_attack_box_rect().to_dict(),
            "is_eating": self.is_eating,
            "is_dead": self.is_dead,
            "is_hypno": self.is_hypno,
            "is_blown": self.is_blown,
            "is_not_dying": self.is_not_dying,
            "is_in_water": self.is_in_water,
            "has_balloon": self.has_balloon,
            "has_eaten_garlic": self.has_eaten_garlic,
            "has_item_or_walk_left": self.has_item_or_walk_left,
            "master_id": self.master_id,
            "partners": self.partners,
            "accessory_1": accessory_1_dict,
            "accessory_2": accessory_2_dict,
            "action": self.action.name.lower(),
            "ladder_col": self.ladder_col,
            "bungee_col": self.bungee_col,
            "bungee_target": self.bungee_target if self.bungee_target != -1 else None,
            "spawn_wave": self.spawn_wave,
            "time_since_spawn": self.time_since_spawn,
            "time_since_ate_garlic": self.time_since_ate_garlic,
            "garlic_tick": garlic_tick_dict,
        }

        # Add type-specific fields
        if self.type == ZombieType.CATAPULT:
            result["n_basketballs"] = self.catapult_or_jackson
        elif self.type == ZombieType.DANCING:
            result["summon_countdown"] = self.catapult_or_jackson

        return result
