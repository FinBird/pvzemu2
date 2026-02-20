import json
from dataclasses import dataclass, field
from random import Random
from typing import Any, List

from pvzemu2.enums import SceneType, PlantType
from pvzemu2.obj_list import ObjList
from pvzemu2.objects.griditem import GridItem
from pvzemu2.objects.plant import Plant
from pvzemu2.objects.projectile import Projectile
from pvzemu2.objects.zombie import Zombie


@dataclass(slots=True)
class SunData:
    sun: int = 9990
    natural_sun_generated: int = 0
    natural_sun_countdown: int = 0

    def to_dict(self) -> dict[str, int]:
        return {
            "sun": self.sun,
            "natural_sun_generated": self.natural_sun_generated,
            "natural_sun_countdown": self.natural_sun_countdown
        }


@dataclass(slots=True)
class RowRandomData:
    b: float = 0.0
    c: float = 0.0
    d: float = 0.0

    def to_dict(self) -> dict[str, float]:
        return {"b": self.b, "c": self.c, "d": self.d}


@dataclass(slots=True)
class SpawnCountdown:
    pool: int = 0

    def to_dict(self) -> dict[str, int]:
        return {"pool": self.pool}


@dataclass(slots=True)
class IcePathData:
    # 对应 C++: std::array<unsigned int, 6> countdown;
    # 对应 C++: std::array<int, 6> x;
    countdown: List[int] = field(default_factory=lambda: [0] * 6)
    x: List[int] = field(default_factory=lambda: [800] * 6)

    def to_dict(self) -> dict[str, Any]:
        return {
            "countdown": self.countdown,
            "x": self.x
        }


@dataclass(slots=True)
class CardData:
    type: PlantType = PlantType.NONE
    imitater_type: PlantType = PlantType.NONE
    cold_down: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type.name.lower(),
            "imitater_type": self.imitater_type.name.lower(),
            "cold_down": self.cold_down
        }


@dataclass(slots=True)
class SpawnData:
    wave: int = 0
    total_flags: int = 1000
    next_wave_countdown: int = 600
    next_wave_initial: int = 600

    # 模拟 C++ row_random[6]
    row_random: list[RowRandomData] = field(default_factory=lambda: [RowRandomData() for _ in range(6)])

    # 完整的 countdown 结构
    countdown_next_wave: int = 600
    countdown_next_wave_initial: int = 600
    countdown_lurking_squad: int = 0
    countdown_hugewave_fade: int = 0
    countdown_endgame: int = 0
    countdown_pool: int = 0

    # HP 结构
    hp_initial: int = 0
    hp_threshold: int = 0

    # 其他字段
    spawn_flags: list[bool] = field(default_factory=lambda: [False] * 33)
    is_hugewave_shown: bool = False
    # spawn_list 简化处理
    spawn_list: list[list[Any]] = field(default_factory=lambda: [[0] * 50 for _ in range(20)])

    def to_dict(self) -> dict[str, Any]:
        return {
            "wave": self.wave,
            "total_flags": self.total_flags,
            "next_wave_countdown": self.next_wave_countdown,
            "next_wave_initial": self.next_wave_initial,
            "row_random": [r.to_dict() for r in self.row_random],
            "countdown": {
                "next_wave": self.countdown_next_wave,
                "next_wave_initial": self.countdown_next_wave_initial,
                "lurking_squad": self.countdown_lurking_squad,
                "hugewave_fade": self.countdown_hugewave_fade,
                "endgame": self.countdown_endgame,
                "pool": self.countdown_pool
            },
            "hp": {
                "initial": self.hp_initial,
                "threshold": self.hp_threshold
            },
            "is_hugewave_shown": self.is_hugewave_shown
        }


@dataclass(slots=True)
class Scene:
    type: SceneType = SceneType.DAY
    rows: int = 5

    # 对象池，使用 ObjList (dict-based)
    # 启用 use_recycle=True 以复用 ID，模拟 C++ 数组下标行为
    zombies: ObjList[Zombie] = field(default_factory=lambda: ObjList(use_recycle=True))
    plants: ObjList[Plant] = field(default_factory=lambda: ObjList(use_recycle=True))
    projectiles: ObjList[Projectile] = field(default_factory=lambda: ObjList(use_recycle=True))
    grid_items: ObjList[GridItem] = field(default_factory=lambda: ObjList(use_recycle=True))
    ice_path: IcePathData = field(default_factory=IcePathData)

    # 空间索引优化：按行存储僵尸 ID
    zombies_by_row: list[set[int]] = field(init=False)

    # Plant Map Grid (6 rows, 9 cols)
    # 简单模拟 C++ grid_plant_status, 这里存 Plant 的引用或 None
    plant_map: list[list[dict[str, Plant | None]]] = field(init=False)

    sun: SunData = field(default_factory=SunData)
    spawn: SpawnData = field(default_factory=SpawnData)

    # 卡片系统 (10个卡片)
    cards: list[CardData] = field(default_factory=lambda: [CardData() for _ in range(10)])

    # 缺失的标志字段
    is_zombie_dance: bool = False
    is_future_enabled: bool = False
    stop_spawn: bool = False
    enable_split_pea_bug: bool = True

    zombie_dancing_clock: int = 0
    is_game_over: bool = False
    rng: Random = field(default_factory=Random)

    def __post_init__(self) -> None:
        self.rows = 6 if self.type in (SceneType.POOL, SceneType.FOG) else 5

        # 初始化僵尸行索引
        self.zombies_by_row = [set() for _ in range(6)]

        # 初始化 Grid，包含 coffee_bean 字段
        self.plant_map = [
            [
                {'content': None, 'pumpkin': None, 'base': None, 'coffee_bean': None}
                for _ in range(9)
            ]
            for _ in range(6)
        ]

        # 初始化 zombie_dancing_clock
        self.zombie_dancing_clock = self.rng.randint(0, 9999)

    def reset(self) -> None:
        self.zombies.clear()
        self.plants.clear()
        self.projectiles.clear()
        self.grid_items.clear()
        for s in self.zombies_by_row:
            s.clear()

        self.sun.sun = 9990
        self.zombie_dancing_clock = 0  # 重置为0，而不是随机值
        self.is_game_over = False
        self.is_zombie_dance = False
        self.stop_spawn = False
        # 重置 spawn 数据
        self.spawn = SpawnData()
        # 重置 plant_map
        for row in range(6):
            for col in range(9):
                self.plant_map[row][col] = {'content': None, 'pumpkin': None, 'base': None, 'coffee_bean': None}
        # ... 其他重置逻辑

    def is_water_grid(self, row: int, col: int) -> bool:
        """检查是否为水池格子"""
        if self.type not in (SceneType.POOL, SceneType.FOG):
            return False

        return (row == 2 or row == 3) and (0 <= col <= 8)

    def get_max_row(self) -> int:
        """获取最大行数"""
        return 6 if self.type in (SceneType.POOL, SceneType.FOG) else 5

    def to_dict(self) -> dict[str, Any]:
        cards_dict = [card.to_dict() for card in self.cards]

        return {
            "type": self.type.name.lower(),
            "rows": self.rows,
            "is_game_over": self.is_game_over,
            "is_zombie_dance": self.is_zombie_dance,
            "is_future_enabled": self.is_future_enabled,
            "stop_spawn": self.stop_spawn,
            "enable_split_pea_bug": self.enable_split_pea_bug,
            "zombie_dancing_clock": self.zombie_dancing_clock,
            "sun": self.sun.to_dict(),
            "spawn": self.spawn.to_dict(),
            "cards": cards_dict,
            "plants": [p.to_dict() for p in self.plants],
            "zombies": [z.to_dict() for z in self.zombies],
            "grid_items": [i.to_dict() for i in self.grid_items],  # 假设 GridItem 有 to_dict
            "projectiles": [p.to_dict() for p in self.projectiles],
            "ice_path": self.ice_path.to_dict(),
        }

    def to_json(self) -> str:
        """对外暴露的 JSON 字符串生成接口"""
        return json.dumps(self.to_dict())
