from typing import Optional, Dict, Any, TYPE_CHECKING

from pvzemu2.enums import SceneType, PlantType, ZombieType
if TYPE_CHECKING:
    from pvzemu2.objects.plant import Plant
    from pvzemu2.objects.zombie import Zombie

from pvzemu2.scene import Scene
from pvzemu2.systems.damage import DamageSystem
from pvzemu2.systems.griditem import GridItemSystem
from pvzemu2.systems.griditem_factory import GridItemFactory
from pvzemu2.systems.ice_path import IcePathSystem
from pvzemu2.systems.plant_factory import PlantFactory
from pvzemu2.systems.plant_system import PlantSystem
from pvzemu2.systems.projectile_factory import ProjectileFactory
from pvzemu2.systems.projectile_system import ProjectileSystem
from pvzemu2.systems.spawn import SpawnSystem
from pvzemu2.systems.sun import SunSystem
from pvzemu2.systems.util import get_y_by_row_and_col
from pvzemu2.systems.zombie_factory import ZombieFactory
from pvzemu2.systems.zombie_system import ZombieSystem


class World:
    """
    PvZ Emulator 2 统一入口类。
    整合了所有子系统，提供高性能的步进模拟与简洁的交互接口。
    """
    __slots__ = (
        'scene', 'plant_factory', 'zombie_factory', 'damage_system',
        'projectile_factory', 'plant_system', 'projectile_system',
        'griditem_factory', 'zombie_system', 'sun_system',
        'griditem_system', 'ice_path_system', 'spawn_system'
    )

    def __init__(self, scene_type: SceneType = SceneType.DAY) -> None:
        # 1. 核心状态存储
        self.scene = Scene(type=scene_type)

        # 2. 基础工厂初始化
        self.plant_factory = PlantFactory(self.scene)
        self.zombie_factory = ZombieFactory(self.scene)
        self.griditem_factory = GridItemFactory(self.scene)
        self.projectile_factory = ProjectileFactory(self.scene)

        # 3. 核心逻辑系统
        self.damage_system = DamageSystem(self.scene)
        self.plant_system = PlantSystem(self.scene, self.projectile_factory, self.damage_system, self.plant_factory)
        self.projectile_system = ProjectileSystem(self.scene, self.damage_system, self.projectile_factory)
        self.zombie_system = ZombieSystem(self.scene, self.damage_system, self.plant_factory)

        # 4. 生态与关卡系统
        self.sun_system = SunSystem(self.scene)
        self.griditem_system = GridItemSystem(self.scene, self.griditem_factory)
        self.ice_path_system = IcePathSystem(self.scene)
        self.spawn_system = SpawnSystem(self.scene, self.zombie_factory)

    # --- 核心控制接口 ---

    def update(self) -> bool:
        """
        执行单帧物理步进。
        :return: bool, 如果游戏结束返回 True。
        """
        if self.scene.is_game_over:
            return True

        self.scene.zombie_dancing_clock += 1

        # 逻辑流水线
        self.griditem_system.update()
        self.plant_system.update()

        # 僵尸更新包含进家判定，返回 True 表示 Game Over
        if self.zombie_system.update():
            self.scene.is_game_over = True
            return True

        self.projectile_system.update()

        # 辅助系统更新
        self._update_cards()
        self.sun_system.update()
        if not self.scene.stop_spawn:
            self.spawn_system.update()

        self.ice_path_system.update()
        if self.scene.spawn.countdown_pool > 0:
            self.scene.spawn.countdown_pool -= 1

        # 清理垃圾对象
        self._clean_dead_objects()

        return False

    def step(self, frames: int = 1) -> bool:
        """
        向前模拟指定帧数。通常用于强化学习或快速跳过动画。
        """
        for _ in range(frames):
            if self.update():
                return True
        return False

    # --- 交互操作接口 (Actions) ---

    def plant(self, plant_type: PlantType, row: int, col: int) -> Optional['Plant']:
        """
        在指定网格种植植物。会自动校验位置与条件。
        :return: 种植成功的 Plant 对象，若失败返回 None。
        """
        if self.plant_factory.can_plant(row, col, plant_type):
            return self.plant_factory.create(plant_type, row, col)
        return None

    def spawn(self, zombie_type: ZombieType, row: int, x: float = 800.0) -> 'Zombie':
        """
        强制生成僵尸。会自动处理空间索引（zombies_by_row）与坐标同步。
        """
        z = self.zombie_factory.create(zombie_type)

        # 修正行索引同步逻辑
        if z.row != row:
            self.scene.zombies_by_row[z.row].discard(z.id)
            z.row = row
            self.scene.zombies_by_row[row].add(z.id)

        z.x = x
        z.int_x = int(x)
        # 修正 Y 轴偏移
        z.y = float(get_y_by_row_and_col(self.scene.type, row, 9) - 30)
        z.int_y = int(z.y)
        return z

    def remove_plant(self, row: int, col: int) -> bool:
        """铲除特定格子的植物（按 南瓜头 -> 内容物 -> 底座 顺序）。"""
        cell = self.scene.plant_map[row][col]
        target = cell['pumpkin'] or cell['content'] or cell['base'] or cell['coffee_bean']
        if target:
            self.plant_factory.destroy(target)
            return True
        return False

    # --- 数据观测接口 (Observation) ---

    def get_state(self) -> Dict[str, Any]:
        """获取当前场景的原始数据字典（Snapshot）。"""
        return self.scene.to_dict()

    def to_json(self) -> str:
        """导出当前状态为 JSON 字符串。"""
        return self.scene.to_json()

    # --- 内部辅助逻辑 ---

    def _update_cards(self) -> None:
        """更新种子卡片冷却。"""
        for card in self.scene.cards:
            if card.cold_down > 0:
                card.cold_down -= 1

    def _clean_dead_objects(self) -> None:
        """
        清理所有系统中标记为已销毁的对象，释放内存。
        此步骤确保 ObjList 中的 ID 被回收且空间缓存不包含死对象。
        """
        # 1. 清理僵尸 (必须同时从 zombies 和 zombies_by_row 移除)
        for zid in [z.id for z in self.scene.zombies if z.is_dead]:
            z = self.scene.zombies.get(zid)
            if z and 0 <= z.row < len(self.scene.zombies_by_row):
                self.scene.zombies_by_row[z.row].discard(zid)
            self.scene.zombies.remove(zid)

        # 2. 清理植物、子弹、地形物品 (ObjList 已实现 ID 复用)
        for pid in [p.id for p in self.scene.plants if p.is_dead]:
            self.scene.plants.remove(pid)

        for pid in [p.id for p in self.scene.projectiles if p.is_disappeared]:
            self.scene.projectiles.remove(pid)

        for iid in [i.id for i in self.scene.grid_items if i.is_disappeared]:
            self.scene.grid_items.remove(iid)

    def reset(self, scene_type: Optional[SceneType] = None) -> None:
        """重置世界状态。"""
        st = scene_type or self.scene.type
        self.scene = Scene(type=st)
        # 重新绑定所有系统的 scene 引用
        self.__init__(st)
