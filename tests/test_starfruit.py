import unittest
from unittest.mock import MagicMock

from pvzemu2.enums import ZombieType, PlantType
from pvzemu2.objects.plant import Plant
from pvzemu2.objects.zombie import Zombie
from pvzemu2.scene import Scene
from pvzemu2.systems.damage import DamageSystem
from pvzemu2.systems.plant_subsystems.starfruit import StarfruitSubsystem
from pvzemu2.systems.projectile_factory import ProjectileFactory
from pvzemu2.systems.rng import RNG


class TestStarfruit(unittest.TestCase):
    def setUp(self):
        self.scene = Scene()
        self.damage_system = MagicMock(spec=DamageSystem)
        self.rng = MagicMock(spec=RNG)
        self.projectile_factory = MagicMock(spec=ProjectileFactory)

        # Mock damage system to always say yes to can_be_attacked
        self.damage_system.can_be_attacked.return_value = True
        self.damage_system._get_plant_attack_flags.return_value = 0

        self.starfruit = StarfruitSubsystem(self.scene, self.damage_system, self.rng, self.projectile_factory)

        # Create a Starfruit plant at (100, 100)
        self.plant = Plant(PlantType.STARFRUIT, 2, 2, 100, 100, 100, 100)
        # Center is at 100+40, 100+40 = 140, 140

    def create_zombie(self, row, x, y, width=50, height=100, dx=0.0):
        z = Zombie(ZombieType.ZOMBIE, row, x, y, 100)
        z.dx = dx
        # 设置僵尸的 hit box 属性
        z.int_x = int(x)  # 修复：初始化 int_x
        z.int_y = int(y)
        z.hit_box_x = 0
        z.hit_box_y = 0
        z.hit_box_width = width
        z.hit_box_height = height
        z.hit_box_offset_x = 0
        z.hit_box_offset_y = 0

        # 设置 attack box 属性
        z.attack_box_x = 0
        z.attack_box_y = 0
        z.attack_box_width = width
        z.attack_box_height = height

        self.scene.zombies.add(z)
        # 注意：StarfruitSubsystem 使用 scene.zombies 全量遍历，不需要 zombies_by_row
        return z

    def test_same_row_behind(self):
        # Plant Center X = 140
        # Zombie at x=50. Width=50. Right edge = 100.
        # 100 < 140. Should fire.
        self.create_zombie(2, 50, 100)
        self.assertTrue(self.starfruit.has_target(self.plant))

    def test_same_row_ahead(self):
        # Plant Center X = 140
        # Zombie at x=200. Left edge = 200.
        # 200 > 140. Not behind.
        self.create_zombie(2, 200, 100)
        self.assertFalse(self.starfruit.has_target(self.plant))

    def test_vertical_hit(self):
        # Zombie at x=116. Width=50. Center=141.
        # Plant Center X=140.
        # Vertical range [116, 166]. 140 is inside.
        self.create_zombie(0, 116, 0)
        self.assertTrue(self.starfruit.has_target(self.plant))

    def test_diagonal_near_row(self):
        # Row diff 1.
        # Target angle ~30 deg.
        z = self.create_zombie(3, 215, 148)
        self.assertTrue(self.starfruit.has_target(self.plant))

    def test_diagonal_near_row_miss(self):
        # Angle ~0 deg (Directly right).
        # Should miss (needs > 20 deg).
        z = self.create_zombie(3, 1000, 150)
        self.assertFalse(self.starfruit.has_target(self.plant))

    def test_diagonal_far_row(self):
        # Row diff >= 2.
        # Target angle ~30 deg.
        z = self.create_zombie(4, 479, 300)
        self.assertTrue(self.starfruit.has_target(self.plant))


if __name__ == '__main__':
    unittest.main()
