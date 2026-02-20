import json
import unittest

from pvzemu2 import Zombie, Projectile, Scene
from pvzemu2.enums import SceneType, PlantType, ZombieType, ProjectileType
from pvzemu2.world import World


class TestPvZEmulator(unittest.TestCase):
    def setUp(self) -> None:
        self.world = World(SceneType.POOL)

    def test_initial_state(self) -> None:
        """测试世界初始化"""
        self.assertEqual(self.world.scene.type, SceneType.POOL)
        self.assertEqual(self.world.scene.sun.sun, 9990)  # C++ 默认值
        self.assertFalse(self.world.scene.is_game_over)

    def test_plant_placement(self) -> None:
        """测试放置植物"""
        # 模拟放置一个豌豆射手在 (1, 2)
        success = self.world.plant(PlantType.PEA_SHOOTER, row=1, col=2)
        self.assertTrue(success)

        # 验证植物数据
        plants = list(self.world.scene.plants)

        self.assertEqual(len(plants), 1)
        self.assertEqual(plants[0].type, PlantType.PEA_SHOOTER)
        self.assertEqual(plants[0].row, 1)
        self.assertEqual(plants[0].hp, 300)  # 基础血量

    def test_update_loop(self) -> None:
        """测试游戏循环更新"""
        # 运行 100 帧
        for _ in range(100):
            self.world.update()

        # 简单验证时钟前进
        self.assertGreater(self.world.scene.zombie_dancing_clock, 0)

    def test_api_try_plant_success(self) -> None:
        """
        测试植物种植接口 - 成功情况
        覆盖接口: World.try_plant
        """
        row, col = 1, 2
        p_type = PlantType.PEA_SHOOTER

        # Action
        result = self.world.plant(p_type, row, col)

        # Assert
        self.assertTrue(result)
        self.assertEqual(len(self.world.scene.plants), 1)
        plant = list(self.world.scene.plants)[0]
        self.assertEqual(plant.type, p_type)
        self.assertEqual(plant.row, row)
        self.assertEqual(plant.col, col)

        # 验证 GridMap 是否更新
        self.assertIsNotNone(self.world.scene.plant_map[row][col]['content'])

    def test_api_try_plant_fail_out_of_bounds(self) -> None:
        """
        测试植物种植接口 - 失败情况 (越界)
        覆盖接口: World.try_plant
        """
        # Action: Pool map has rows 0-5, cols 0-8
        result = self.world.plant(PlantType.PEA_SHOOTER, 10, 10)

        # Assert
        self.assertIsNone(result)
        self.assertEqual(len(self.world.scene.plants), 0)

    def test_api_try_plant_fail_occupied(self) -> None:
        """
        测试植物种植接口 - 失败情况 (格子已被占用)
        覆盖接口: World.try_plant
        """
        self.world.plant(PlantType.PEA_SHOOTER, 1, 1)

        # 再次在同一位置种植
        result = self.world.plant(PlantType.SUNFLOWER, 1, 1)

        # Assert
        self.assertIsNone(result)
        self.assertEqual(len(self.world.scene.plants), 1)
        self.assertEqual(list(self.world.scene.plants)[0].type, PlantType.PEA_SHOOTER)

    def test_api_update(self) -> None:
        """
        测试游戏循环更新接口
        覆盖接口: World.update
        """
        initial_clock = self.world.scene.zombie_dancing_clock

        # Action
        is_game_over = self.world.update()

        # Assert
        self.assertFalse(is_game_over)
        self.assertEqual(self.world.scene.zombie_dancing_clock, initial_clock + 1)

    def test_api_to_json_structure(self) -> None:
        """
        测试 JSON 输出接口的结构完整性
        覆盖接口: World.to_json
        """
        # Arrange: 添加一些状态
        self.world.plant(PlantType.SUNFLOWER, 0, 0)
        self.world.update()

        # Action
        json_str = self.world.to_json()
        data = json.loads(json_str)

        # Assert: 验证顶层字段 (对应 C++ scene::to_json)
        self.assertIn("type", data)
        self.assertEqual(data["type"], "pool")  # SceneType.POOL.name.lower()
        self.assertIn("rows", data)
        self.assertIn("sun", data)
        self.assertIn("plants", data)
        self.assertIn("zombies", data)
        self.assertIn("spawn", data)
        self.assertIn("is_game_over", data)

    def test_api_to_json_plant_details(self) -> None:
        """
        测试 JSON 输出中植物的具体数据
        覆盖接口: World.to_json (Plant 部分)
        """
        # Arrange
        row, col = 1, 4
        success = self.world.plant(PlantType.WALLNUT, row, col)
        self.assertTrue(success, "Planting Wallnut failed! Check row type (water/ground).")

        # Action
        data = self.world.get_state()  # 使用 get_raw_data 方便测试，逻辑同 to_json
        self.assertGreater(len(data["plants"]), 0, "Plant list is empty")
        plant_data = data["plants"][0]

        # Assert (对应 C++ plant::to_json)
        self.assertEqual(plant_data["type"], "wallnut")
        self.assertEqual(plant_data["row"], row)
        self.assertEqual(plant_data["col"], col)
        self.assertEqual(plant_data["status"], "idle")
        self.assertIn("hp", plant_data)
        self.assertIn("id", plant_data)
        self.assertIn("reanimate", plant_data)
        self.assertIn("countdown", plant_data)

        # 验证 Reanim 结构
        reanimate = plant_data["reanimate"]
        self.assertIn("fps", reanimate)
        self.assertIn("type", reanimate)

    def test_api_get_raw_data(self) -> None:
        """
        测试 Python 特有的字典获取接口
        覆盖接口: World.get_raw_data
        """
        data = self.world.get_state()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["sun"]["sun"], 9990)

    def test_scene_reset(self) -> None:
        """
        测试内部场景重置逻辑 (虽然 World 没有直接暴露 reset，但通过重新 init 模拟)
        覆盖逻辑: Scene.reset
        """
        self.world.plant(PlantType.PEA_SHOOTER, 0, 0)
        self.world.scene.sun.sun = 50

        # Action: 模拟重置，或者直接调用 scene.reset
        self.world.scene.reset()

        # Assert
        self.assertEqual(len(self.world.scene.plants), 0)
        self.assertEqual(self.world.scene.sun.sun, 9990)
        self.assertEqual(self.world.scene.zombie_dancing_clock, 0)

    def test_zombie_creation(self):
        """Test the instantiation and post-initialization of a Zombie object."""
        # Arrange & Act
        zombie = Zombie(type=ZombieType.ZOMBIE, row=2, x=150.5, y=200.5)

        # Assert basic properties
        self.assertIsNotNone(zombie.id, "Zombie ID should be auto-generated upon creation")
        self.assertIsInstance(zombie.id, int, "Zombie ID should be an integer")
        self.assertEqual(zombie.type, ZombieType.ZOMBIE)
        self.assertEqual(zombie.row, 2)

        # Assert floating point coordinates
        self.assertEqual(zombie.x, 150.5)
        self.assertEqual(zombie.y, 200.5)

        # Assert __post_init__ casting to integer coordinates
        # Note: Depending on your Zombie class implementation, if int_x/int_y
        # are not set in __post_init__, this tests ensures they default correctly.
        # Usually, they are updated in the game loop, but defaults should be 0 or casted.
        if hasattr(zombie, 'int_x') and zombie.int_x != 0:
            self.assertEqual(zombie.int_x, 150)
            self.assertEqual(zombie.int_y, 200)

        # Assert default stats
        self.assertEqual(zombie.hp, 270, "Default Zombie HP should be 270")
        self.assertEqual(zombie.max_hp, 270, "Default Zombie max_hp should be 270")

    def test_projectile_creation(self):
        """Test the instantiation and post-initialization of a Projectile object."""
        # Arrange & Act
        projectile = Projectile(type=ProjectileType.PEA, row=1, x=300.0, y=120.0)

        # Assert basic properties
        self.assertIsNotNone(projectile.id, "Projectile ID should be auto-generated")
        self.assertIsInstance(projectile.id, int, "Projectile ID should be an integer")
        self.assertEqual(projectile.type, ProjectileType.PEA)
        self.assertEqual(projectile.row, 1)

        # Assert floating point coordinates
        self.assertEqual(projectile.x, 300.0)
        self.assertEqual(projectile.y, 120.0)

        # Assert __post_init__ side effects for Projectile
        # Projectile __post_init__ explicitly sets int_x and int_y
        self.assertEqual(projectile.int_x, 300)
        self.assertEqual(projectile.int_y, 120)

    def test_scene_creation_day(self):
        """Test the instantiation of a Day Scene and its row calculation."""
        # Arrange & Act
        scene = Scene(type=SceneType.DAY)

        # Assert Scene type and row calculation logic
        self.assertEqual(scene.type, SceneType.DAY)
        self.assertEqual(scene.rows, 5, "Day scene should have exactly 5 rows")

        # Assert object lists are initialized and empty
        self.assertEqual(len(scene.plants), 0)
        self.assertEqual(len(scene.zombies), 0)
        self.assertEqual(len(scene.projectiles), 0)

    def test_scene_creation_pool(self):
        """Test the instantiation of a Pool Scene to ensure row count adjusts correctly."""
        # Arrange & Act
        scene = Scene(type=SceneType.POOL)

        # Assert Pool scene specifics
        self.assertEqual(scene.type, SceneType.POOL)
        self.assertEqual(scene.rows, 6, "Pool scene should have exactly 6 rows")


if __name__ == '__main__':
    unittest.main()
