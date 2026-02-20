import unittest

from pvzemu2.enums import PlantType, PlantStatus, ZombieType, ZombieStatus, SceneType
from pvzemu2.scene import Scene
from pvzemu2.systems.damage import DamageSystem
from pvzemu2.systems.plant_factory import PlantFactory
from pvzemu2.systems.plant_system import PlantSystem
from pvzemu2.systems.projectile_factory import ProjectileFactory
from pvzemu2.systems.util import zombie_init_y
from pvzemu2.systems.zombie_factory import ZombieFactory


class TestChomper(unittest.TestCase):
    def setUp(self):
        self.scene = Scene(SceneType.DAY)
        self.plant_factory = PlantFactory(self.scene)
        self.zombie_factory = ZombieFactory(self.scene)
        self.damage_system = DamageSystem(self.scene)
        self.projectile_factory = ProjectileFactory(self.scene)
        self.plant_system = PlantSystem(self.scene, self.projectile_factory, self.damage_system, self.plant_factory)

    def _move_zombie_to_row(self, zombie, row):
        """Helper to properly move a zombie to a row and update spatial cache"""
        if 0 <= zombie.row < len(self.scene.zombies_by_row):
            self.scene.zombies_by_row[zombie.row].discard(zombie.id)
        zombie.row = row
        zombie.y = zombie_init_y(self.scene.type, zombie, row)
        zombie.int_y = int(zombie.y)

        self.scene.zombies_by_row[row].add(zombie.id)
        self.scene.zombies_by_row[row].add(zombie.id)

    def test_chomper_initial_state(self):
        """测试大嘴花创建后的初始状态"""
        chomper = self.plant_factory.create(PlantType.CHOMPER, 2, 2)
        self.assertEqual(chomper.type, PlantType.CHOMPER)
        self.assertEqual(chomper.status, PlantStatus.WAIT)

    def test_chomper_finds_target_and_starts_bite(self):
        """测试大嘴花发现目标并开始咬合"""
        chomper = self.plant_factory.create(PlantType.CHOMPER, 2, 2)

        # 创建僵尸在攻击范围内 (同位置同列偏前一点)
        zombie = self.zombie_factory.create(ZombieType.ZOMBIE)
        self._move_zombie_to_row(zombie, 2)
        zombie.x = chomper.x + 59
        zombie.int_x = int(zombie.x)

        self.plant_system.update()

        self.assertEqual(chomper.status, PlantStatus.CHOMPER_BITE_BEGIN)
        # countdown 已经被减去 1 -> 69
        self.assertEqual(chomper.countdown.status, 70)

    def test_chomper_bite_begin_countdown_decrements(self):
        """测试咬合开始倒计时递减并在无目标时失败"""
        chomper = self.plant_factory.create(PlantType.CHOMPER, 2, 2)
        chomper.status = PlantStatus.CHOMPER_BITE_BEGIN
        chomper.countdown.status = 70

        for i in range(70):
            self.plant_system.update()

        # 倒计时归零后触发咬合，状态转为 FAIL（无目标）
        self.assertEqual(chomper.status, PlantStatus.CHOMPER_BITE_FAIL)

    def test_chomper_successful_bite_eats_zombie(self):
        """测试成功咬合并直接销毁僵尸"""
        chomper = self.plant_factory.create(PlantType.CHOMPER, 2, 2)
        zombie = self.zombie_factory.create(ZombieType.ZOMBIE)
        self._move_zombie_to_row(zombie, 2)
        zombie.x = chomper.x + 80
        zombie.int_x = int(zombie.x)

        chomper.status = PlantStatus.CHOMPER_BITE_BEGIN
        chomper.countdown.status = 0

        self.plant_system.update()

        # 大嘴花应该进入 BITE_SUCCESS 状态
        self.assertEqual(chomper.status, PlantStatus.CHOMPER_BITE_SUCCESS)
        # 僵尸因为直接销毁所以会在列表中被标记或被清除
        self.assertTrue(zombie.is_dead or zombie not in self.scene.zombies)

    def test_chomper_cannot_eat_gargantuar(self):
        """测试大嘴花咬巨人只会造成40伤害而不是致死"""
        chomper = self.plant_factory.create(PlantType.CHOMPER, 2, 2)

        gargantuar = self.zombie_factory.create(ZombieType.GARGANTUAR)
        self._move_zombie_to_row(gargantuar, 2)
        gargantuar.x = chomper.x + 80
        gargantuar.int_x = int(gargantuar.x)

        chomper.status = PlantStatus.CHOMPER_BITE_BEGIN
        chomper.countdown.status = 0

        initial_hp = gargantuar.hp
        self.plant_system.update()

        self.assertEqual(chomper.status, PlantStatus.CHOMPER_BITE_FAIL)
        # 巨人僵尸受到 40 点常规伤害
        self.assertEqual(gargantuar.hp, initial_hp - 40)

    def test_chomper_cannot_eat_jumping_zombie(self):
        """测试大嘴花不能吞噬跳跃中的僵尸，返回MISS判定"""
        chomper = self.plant_factory.create(PlantType.CHOMPER, 2, 2)

        pole_zombie = self.zombie_factory.create(ZombieType.POLE_VAULTING)
        self._move_zombie_to_row(pole_zombie, 2)
        pole_zombie.x = chomper.x + 80
        pole_zombie.int_x = int(pole_zombie.x)
        pole_zombie.status = ZombieStatus.POLE_VALUTING_JUMPING

        chomper.status = PlantStatus.CHOMPER_BITE_BEGIN
        chomper.countdown.status = 0

        self.plant_system.update()
        self.assertEqual(chomper.status, PlantStatus.CHOMPER_BITE_FAIL)

    def test_chomper_chew_and_swallow_sequence(self):
        """测试咀嚼和吞咽序列状态轮转"""
        chomper = self.plant_factory.create(PlantType.CHOMPER, 2, 2)

        chomper.status = PlantStatus.CHOMPER_BITE_SUCCESS
        chomper.reanimate.n_repeated = 1

        self.plant_system.update()
        self.assertEqual(chomper.status, PlantStatus.CHOMPER_CHEW)
        self.assertEqual(chomper.countdown.status, 4000)

        chomper.countdown.status = 0
        self.plant_system.update()

        self.assertEqual(chomper.status, PlantStatus.CHOMPER_SWALLOW)

        chomper.reanimate.n_repeated = 1
        self.plant_system.update()

        self.assertEqual(chomper.status, PlantStatus.WAIT)

    def test_chomper_target_out_of_range(self):
        """测试僵尸在攻击范围外时不被攻击"""
        chomper = self.plant_factory.create(PlantType.CHOMPER, 2, 2)

        zombie = self.zombie_factory.create(ZombieType.ZOMBIE)
        self._move_zombie_to_row(zombie, 2)
        # 距离大嘴花 200 像素，远在攻击框 (最大 120 像素以外) 外
        zombie.x = chomper.x + 200
        zombie.int_x = int(zombie.x)

        self.plant_system.update()

        # 超出范围，不应攻击，应保持 WAIT 状态
        self.assertEqual(chomper.status, PlantStatus.WAIT)

    def test_chomper_target_behind_plant(self):
        """测试僵尸在植物后方时不被攻击"""
        chomper = self.plant_factory.create(PlantType.CHOMPER, 2, 2)

        zombie = self.zombie_factory.create(ZombieType.ZOMBIE)
        self._move_zombie_to_row(zombie, 2)
        # 距离大嘴花 -50 像素（在后方）
        zombie.x = chomper.x - 50
        zombie.int_x = int(zombie.x)

        self.plant_system.update()

        # 在后方，不应攻击，应保持 WAIT 状态
        self.assertEqual(chomper.status, PlantStatus.WAIT)


if __name__ == '__main__':
    unittest.main()
