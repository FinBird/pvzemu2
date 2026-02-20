from dataclasses import dataclass, field
from typing import Any

from pvzemu2.enums import PlantType, PlantStatus, PlantEdibleStatus, PlantDirection, AttackFlags, PlantReanimName
from pvzemu2.geometry import Rect
from pvzemu2.objects.base import Reanimate, ReanimateType, get_uuid
from pvzemu2.objects.plant_reanim_data import get_plant_reanim_data, get_reanim_frame_data, has_reanim

BOARD_WIDTH = 800  # PC: 800 - Console : 1280
BOARD_HEIGHT = 600  # PC : 600 - Console : 720

COST_TABLE = (
    100, 50, 150, 50, 25, 175, 150, 200,
    0, 25, 75, 75, 75, 25, 75, 125,
    25, 50, 325, 25, 125, 100, 175, 125,
    0, 25, 125, 100, 125, 125, 125, 100,
    100, 25, 100, 75, 50, 100, 50, 300,
    250, 150, 150, 225, 200, 50, 125, 500
)

CD_TABLE = (
    750, 750, 5000, 3000, 3000, 750, 750, 750,
    750, 750, 750, 750, 3000, 750, 5000, 5000,
    750, 3000, 750, 3000, 5000, 750, 750, 3000,
    3000, 3000, 750, 750, 750, 750, 3000, 750,
    750, 750, 750, 750, 750, 750, 3000, 750,
    5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000
)

CAN_ATTACK_TABLE = (
    True, False, False, False, False, True, False, True,
    True, False, True, False, False, True, False, False,
    False, False, True, False, False, False, False, False,
    True, False, True, False, True, True, False, False,
    True, False, True, False, False, False, False, True,
    True, False, True, True, True, False, False, False,
    False
)

EFFECT_INTERVAL_TABLE = (
    150, 2500, 0, 0, 0, 150, 0, 150,
    150, 2500, 150, 0, 0, 150, 0, 0,
    0, 0, 150, 0, 0, 0, 0, 0,
    150, 2500, 150, 0, 150, 150, 0, 0,
    300, 0, 300, 0, 0, 0, 2500, 300,
    150, 2500, 200, 150, 300, 0, 0, 600,
    0
)


@dataclass(slots=True)
class PlantCountdown:
    status: int = 0
    generate: int = 0
    launch: int = 0
    eaten: int = 0
    awake: int = 0
    effect: int = 0
    dead: int = 0

    def to_dict(self) -> dict[str, int]:
        return {
            'status': self.status,
            'generate': self.generate,
            'launch': self.launch,
            'eaten': self.eaten,
            'awake': self.awake,
            'effect': self.effect,
            'dead': self.dead
        }


@dataclass(slots=True)
class Plant:
    type: PlantType
    row: int
    col: int
    x: int
    y: int

    id: int = field(init=False)

    hp: int
    max_hp: int

    status: PlantStatus = PlantStatus.IDLE
    reanimate: Reanimate = field(default_factory=Reanimate)
    countdown: PlantCountdown = field(default_factory=PlantCountdown)

    cannon_x: int = -1
    cannon_y: int = -1

    # Default size based on C++ plant_base.cpp (80x80)
    attack_box: Rect = field(default_factory=lambda: Rect(0, 0, 80, 80))

    target_id: int = -1
    imitater_target: PlantType = PlantType.NONE
    split_pea_attack_flags: dict[str, bool] = field(default_factory=lambda: {'front': False, 'back': False})
    threepeater_time_since_first_shot: int = 0

    is_dead: bool = False
    is_smashed: bool = False
    is_sleeping: bool = False
    can_attack: bool = True

    edible: PlantEdibleStatus = PlantEdibleStatus.VISIBLE_AND_EDIBLE
    max_boot_delay: int = 0

    direction: PlantDirection = PlantDirection.RIGHT

    _NOCTURNAL_PLANTS = frozenset({
        PlantType.PUFFSHROOM, PlantType.SEASHROOM, PlantType.SUNSHROOM,
        PlantType.FUMESHROOM, PlantType.HYPNOSHROOM, PlantType.DOOMSHROOM,
        PlantType.ICESHROOM, PlantType.MAGNETSHROOM, PlantType.SCAREDYSHROOM,
        PlantType.GLOOMSHROOM
    })

    _AQUATIC_PLANTS = frozenset({
        PlantType.LILY_PAD, PlantType.TANGLE_KELP, PlantType.SEASHROOM,
        PlantType.CATTAIL
    })

    _FLYING_PLANTS = frozenset({
        PlantType.COFFEE_BEAN
    })

    _UPGRADE_PLANTS = frozenset({
        PlantType.GATLING_PEA, PlantType.WINTER_MELON, PlantType.TWIN_SUNFLOWER,
        PlantType.SPIKEROCK, PlantType.COB_CANNON, PlantType.GOLD_MAGNET,
        PlantType.GLOOMSHROOM, PlantType.CATTAIL
    })

    @staticmethod
    def is_nocturnal(type: PlantType) -> bool:
        return type in Plant._NOCTURNAL_PLANTS

    @staticmethod
    def is_aquatic(type: PlantType) -> bool:
        return type in Plant._AQUATIC_PLANTS

    @staticmethod
    def is_flying(type: PlantType) -> bool:
        return type in Plant._FLYING_PLANTS

    @staticmethod
    def is_upgrade(type: PlantType) -> bool:
        return type in Plant._UPGRADE_PLANTS

    def __post_init__(self) -> None:
        self.id = get_uuid()
        self.init_reanim()

    def init_reanim(self) -> None:
        self.reanimate.prev_progress = -1
        n_frames, fps = get_plant_reanim_data(self.type)
        if n_frames > 0:
            self.reanimate.n_frames = n_frames
            self.reanimate.fps = fps

    def set_reanim_frame(self, name: PlantReanimName) -> None:
        begin_frame, n_frames = get_reanim_frame_data(self.type, name)
        if n_frames > 0:
            self.reanimate.begin_frame = begin_frame
            self.reanimate.n_frames = n_frames

    def set_reanim(self, name: PlantReanimName, type: ReanimateType, fps: float) -> None:
        self.set_reanim_frame(name)
        self.reanimate.type = type
        self.reanimate.fps = fps
        self.reanimate.progress = 0.0

    def has_reanim(self, name: PlantReanimName) -> bool:
        return has_reanim(self.type, name)

    def is_squash_attacking(self) -> bool:
        return self.type == PlantType.SQUASH and self.status in (
            PlantStatus.SQUASH_STOP_IN_THE_AIR,
            PlantStatus.SQUASH_JUMP_DOWN,
            PlantStatus.SQUASH_CRUSHED
        )

    def is_sun_plant(self) -> bool:
        return self.type in (PlantType.SUNFLOWER, PlantType.TWIN_SUNFLOWER, PlantType.SUNSHROOM)

    def set_sleep(self, flag: bool) -> None:
        if (self.is_sleeping == flag or
                self.is_squash_attacking() or
                self.is_smashed or
                self.edible == PlantEdibleStatus.INVISIBLE_AND_NOT_EDIBLE or
                self.is_dead):
            return

        self.is_sleeping = flag

        if self.is_sleeping:
            if self.has_reanim(PlantReanimName.anim_sleep):
                self.set_reanim_frame(PlantReanimName.anim_sleep)
            else:
                self.reanimate.fps = 1.0
        else:
            if self.has_reanim(PlantReanimName.anim_idle):
                self.set_reanim_frame(PlantReanimName.anim_idle)

    def get_hit_box(self) -> Rect:
        match self.type:
            case PlantType.TALLNUT:
                return Rect(
                    x=self.x + 10,
                    y=self.y,
                    width=self.attack_box.width,
                    height=self.attack_box.height
                )
            case PlantType.PUMPKIN:
                return Rect(
                    x=self.x,
                    y=self.y,
                    width=self.attack_box.width - 20,
                    height=self.attack_box.height
                )
            case PlantType.COB_CANNON:
                return Rect(
                    x=self.x,
                    y=self.y,
                    width=140,
                    height=80
                )
            case _:
                return Rect(
                    x=self.x + 10,
                    y=self.y,
                    width=self.attack_box.width - 20,
                    height=self.attack_box.height
                )

    def get_attack_box(self, is_alt_attack: bool = False) -> Rect:
        match self.type:
            case PlantType.SPLIT_PEA if is_alt_attack:
                return Rect(
                    x=0,
                    y=self.y,
                    width=self.x + 16,
                    height=self.attack_box.height
                )
            case PlantType.SQUASH:
                return Rect(
                    x=self.x + 20,
                    y=self.y,
                    width=self.attack_box.width - 35,
                    height=self.attack_box.height
                )
            case PlantType.CHOMPER:
                return Rect(
                    x=self.x + 80,
                    y=self.y,
                    width=40,
                    height=self.attack_box.height
                )
            case PlantType.SPIKEWEED | PlantType.SPIKEROCK:
                return Rect(
                    x=self.x + 20,
                    y=self.y,
                    width=self.attack_box.width - 50,
                    height=self.attack_box.height
                )
            case PlantType.POTATO_MINE:
                return Rect(
                    x=self.x,
                    y=self.y,
                    width=self.attack_box.width - 25,
                    height=self.attack_box.height
                )
            case PlantType.TORCHWOOD:
                return Rect(
                    x=self.x + 50,
                    y=self.y,
                    width=30,
                    height=self.attack_box.height
                )
            case PlantType.PUFFSHROOM | PlantType.SEASHROOM:
                return Rect(
                    x=self.x + 60,
                    y=self.y,
                    width=230,
                    height=self.attack_box.height
                )
            case PlantType.FUMESHROOM:
                return Rect(
                    x=self.x + 60,
                    y=self.y,
                    width=340,
                    height=self.attack_box.height
                )
            case PlantType.GLOOMSHROOM:
                return Rect(
                    x=self.x - 80,
                    y=self.y - 80,
                    width=240,
                    height=240
                )
            case PlantType.TANGLE_KELP:
                return Rect(
                    x=self.x,
                    y=self.y,
                    width=self.attack_box.width,
                    height=self.attack_box.height
                )
            case PlantType.CATTAIL:
                return Rect(
                    x=-BOARD_WIDTH,
                    y=-BOARD_HEIGHT,
                    width=BOARD_WIDTH * 2,
                    height=BOARD_HEIGHT * 2
                )
            case _:
                return Rect(
                    x=self.x + 60,
                    y=self.y,
                    width=BOARD_WIDTH,
                    height=self.attack_box.height
                )

    def get_attack_flags(self, is_alt_attack: bool = False) -> int:
        if self.type == PlantType.CACTUS:
            return int(AttackFlags.GROUND) if is_alt_attack else int(AttackFlags.FLYING_BALLOON)

        elif self.type in (PlantType.COB_CANNON, PlantType.CHERRY_BOMB, PlantType.JALAPENO, PlantType.DOOMSHROOM):
            return (AttackFlags.DIGGING_DIGGER |
                    AttackFlags.DYING_ZOMBIES |
                    AttackFlags.ANIMATING_ZOMBIES |
                    AttackFlags.LURKING_SNORKEL |
                    AttackFlags.FLYING_BALLOON |
                    AttackFlags.GROUND |
                    0x8)

        elif self.type in (PlantType.SQUASH, PlantType.CABBAGEPULT, PlantType.MELONPULT,
                           PlantType.KERNELPULT, PlantType.WINTER_MELON):
            return AttackFlags.LURKING_SNORKEL | AttackFlags.GROUND | 0x8

        elif self.type == PlantType.POTATO_MINE:
            return (AttackFlags.DIGGING_DIGGER |
                    AttackFlags.LURKING_SNORKEL |
                    AttackFlags.GROUND |
                    0x8)

        elif self.type in (PlantType.PUFFSHROOM, PlantType.SCAREDYSHROOM, PlantType.FUMESHROOM,
                           PlantType.CHOMPER, PlantType.SEASHROOM):
            return int(AttackFlags.GROUND)

        elif self.type == PlantType.CATTAIL:
            return int(AttackFlags.FLYING_BALLOON | AttackFlags.GROUND)

        elif self.type == PlantType.TANGLE_KELP:
            return int(AttackFlags.LURKING_SNORKEL | AttackFlags.GROUND)

        else:
            return int(AttackFlags.ANIMATING_ZOMBIES | AttackFlags.GROUND)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.name.lower(),
            "status": self.status.name.lower(),
            "x": self.x,
            "y": self.y,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "row": self.row,
            "col": self.col,
            "cannon": {"x": self.cannon_x, "y": self.cannon_y},
            "attack_box": self.get_attack_box().to_dict(),
            # C++ uses get_attack_box(rect) here, implying default is_alt_attack=False
            "hit_box": self.get_hit_box().to_dict(),
            "countdown": self.countdown.to_dict(),
            "reanimate": self.reanimate.to_dict(),
            "is_dead": self.is_dead,
            "is_smashed": self.is_smashed,
            "is_sleeping": self.is_sleeping,
            "can_attack": self.can_attack,
            "max_boot_delay": self.max_boot_delay,
            "direction": "left" if self.direction == PlantDirection.LEFT else "right",
            "target": self.target_id if self.target_id != -1 else None,
            "imitater_target": self.imitater_target.name.lower(),
            "edible": self.edible.name.lower(),
            "threepeater_time_since_first_shot": self.threepeater_time_since_first_shot,
            "split_pea_attack_flags": self.split_pea_attack_flags
        }
