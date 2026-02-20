import unittest

from pvzemu2.enums import (
    SceneType, PlantType, ZombieType, ZombieStatus
)
from pvzemu2.systems.util import zombie_init_y
from pvzemu2.world import World


class TestFumeShroom(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def _setup_fume_shroom(self, row, col):
        if self.scene.is_water_grid(row, col):
            self.world.plant_factory.create(PlantType.LILY_PAD, row, col)

        self.world.plant(PlantType.FUMESHROOM, row, col)
        p = self.scene.plant_map[row][col]['content']
        if p:
            p.countdown.generate = 0
            p.is_sleeping = False
        return p

    def _spawn_zombie_at(self, z_type, row, x):
        """辅助函数：安全地生成僵尸并强制同步所有物理坐标"""
        z = self.world.zombie_factory.create(z_type)

        # 移除原有的(可能越界或错误行的)索引
        for r_set in self.scene.zombies_by_row:
            r_set.discard(z.id)

        z.x = float(x)
        z.int_x = int(x)  # 核心修复：更新整数坐标供判定框使用
        z.row = row
        z.y = zombie_init_y(self.scene.type, z, row)
        z.int_y = int(z.y)  # 核心修复：同步 Y 轴整数坐标

        self.scene.zombies_by_row[row].add(z.id)
        return z

    def test_basic_damage_and_kill_conehead(self):
        """测试1：单体伤害与路障僵尸击杀"""
        self.world = World(SceneType.NIGHT)
        self.scene = self.world.scene
        self._setup_fume_shroom(2, 0)  # X 约 40

        z = self._spawn_zombie_at(ZombieType.CONE_HEAD, 2, 200)

        initial_total_hp = z.hp + z.accessory_1_hp

        for _ in range(60):
            self.world.update()

        self.assertEqual(z.hp + z.accessory_1_hp, initial_total_hp - 20)

    def test_multi_penetration(self):
        """测试2：群体穿透多个普通僵尸"""
        self.world = World(SceneType.NIGHT)
        self.scene = self.world.scene

        p = self._setup_fume_shroom(2, 0)
        p.countdown.generate = 0

        # 生成 3 个僵尸排成一列
        zs = [self._spawn_zombie_at(ZombieType.ZOMBIE, 2, 200 + i * 20) for i in range(3)]

        for _ in range(100):
            self.world.update()

        for z in zs:
            self.assertEqual(z.hp, 250, f"僵尸 {z.id} 应该受到 20 点伤害，当前 HP 为 {z.hp}")

    def test_screen_door_bypass_and_aoe(self):
        """测试3：穿透铁栅门并群体击杀"""
        self.world = World(SceneType.NIGHT)
        self.scene = self.world.scene

        p = self._setup_fume_shroom(1, 0)

        z1 = self._spawn_zombie_at(ZombieType.SCREEN_DOOR, 1, 200)
        z2 = self._spawn_zombie_at(ZombieType.SCREEN_DOOR, 1, 250)

        initial_hp_1 = z1.hp
        initial_acc_1 = z1.accessory_2_hp
        initial_hp_2 = z2.hp
        initial_acc_2 = z2.accessory_2_hp

        for _ in range(60):
            self.world.update()

        self.assertEqual(z1.hp, initial_hp_1 - 20, "僵尸1本体应受伤")
        self.assertEqual(z1.accessory_2_hp, initial_acc_1 - 20, "僵尸1门也应受伤")

        self.assertEqual(z2.hp, initial_hp_2 - 20, "僵尸2本体应同样受穿透伤")
        self.assertEqual(z2.accessory_2_hp, initial_acc_2 - 20, "僵尸2门也应受穿透伤")

    def test_snorkel_submerged_hit(self):
        """测试4：水路潜水僵尸击杀测试"""
        self.world = World(SceneType.FOG)
        self.scene = self.world.scene

        self._setup_fume_shroom(2, 0)

        z = self._spawn_zombie_at(ZombieType.SNORKEL, 2, 200)
        z.status = ZombieStatus.SNORKEL_SWIM
        z.is_in_water = True

        for _ in range(60):
            self.world.update()

        self.assertEqual(z.hp, 270, "大喷菇无法击中潜水中的僵尸")

        z.status = ZombieStatus.SNORKEL_UP_TO_EAT
        for _ in range(60):
            self.world.update()

        self.assertEqual(z.hp, 270, "大喷菇能击中浮起的僵尸")

    def test_day_sleep_behavior(self):
        """测试5：白昼睡眠场景测试"""
        self.world = World(SceneType.DAY)
        self.scene = self.world.scene
        self.world.plant(PlantType.FUMESHROOM, 2, 2)

        p = self.scene.plant_map[2][2]['content']
        self.assertTrue(p.is_sleeping, "白天大喷菇应该在睡觉")

        z = self._spawn_zombie_at(ZombieType.ZOMBIE, 2, 250)

        for _ in range(100):
            self.world.update()

        self.assertEqual(z.hp, 270, "睡觉的大喷菇不应造成伤害")


if __name__ == '__main__':
    unittest.main()
