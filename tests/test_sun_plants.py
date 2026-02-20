import unittest

from pvzemu2.enums import SceneType, PlantType, PlantStatus
from pvzemu2.world import World


class TestSunPlants(unittest.TestCase):
    def test_sunshroom_growth_and_production(self):
        """测试阳光菇：夜间生产与成长 (使用 NIGHT 场景排除自然阳光干扰)"""
        world = World(SceneType.NIGHT)
        world.scene.sun.sun = 0
        world.scene.stop_spawn = True

        shroom = world.plant_factory.create(PlantType.SUNSHROOM, row=2, col=2)

        # 1. 初始状态检查
        self.assertEqual(shroom.status, PlantStatus.SUNSHROOM_SMALL)
        self.assertEqual(shroom.countdown.status, 12000)

        initial_delay = shroom.countdown.generate
        self.assertTrue(300 <= initial_delay <= 1250)

        # 2. 模拟步进到产出帧
        for _ in range(initial_delay):
            world.update()

        self.assertEqual(world.scene.sun.sun, 15, "小阳光菇产出数值错误")
        self.assertTrue(2350 <= shroom.countdown.generate <= 2500, f"频率重置错误: {shroom.countdown.generate}")

        # 4. 模拟成长：智能步进
        entered_grow = False
        for _ in range(12001):
            world.update()
            if shroom.status == PlantStatus.SUNSHROOM_GROW:
                entered_grow = True
                break

        self.assertTrue(entered_grow, "阳光菇未能进入 GROW 状态")

        # 5. 继续 update 直到进入 BIG 状态 (动画播放完毕)
        entered_big = False
        for _ in range(200):  # 动画通常只有几十帧
            world.update()
            if shroom.status == PlantStatus.SUNSHROOM_BIG:
                entered_big = True
                break

        self.assertTrue(entered_big, "阳光菇未能进入 BIG 状态")

        # 6. 验证大阳光菇的产出 (25 阳光)
        world.scene.sun.sun = 0
        target_sun = 25

        produced_big_sun = False
        for _ in range(3000):
            world.update()
            if world.scene.sun.sun >= target_sun:
                produced_big_sun = True
                break

        self.assertTrue(produced_big_sun, "大阳光菇未能产出 25 点阳光")

    def test_sunflower_production_frequency(self):
        """测试向日葵：产出频率与数值 (使用 NIGHT 场景)"""
        world = World(SceneType.NIGHT)
        world.scene.stop_spawn = True
        world.scene.sun.sun = 0

        sunflower = world.plant_factory.create(PlantType.SUNFLOWER, row=2, col=2)

        for _ in range(sunflower.countdown.generate):
            world.update()

        self.assertEqual(world.scene.sun.sun, 25, "向日葵产出数值错误")
        self.assertTrue(2350 <= sunflower.countdown.generate <= 2500, f"重置频率错误: {sunflower.countdown.generate}")

    def test_twin_sunflower_production_frequency(self):
        """测试双子向日葵：双倍产出量 (使用 NIGHT 场景)"""
        world = World(SceneType.NIGHT)
        world.scene.sun.sun = 0
        world.scene.stop_spawn = True

        twin = world.plant_factory.create(PlantType.TWIN_SUNFLOWER, row=2, col=2)

        initial_delay = twin.countdown.generate
        for _ in range(initial_delay):
            world.update()
        self.assertEqual(world.scene.sun.sun, 50, "双子向日葵产出数值错误")
        self.assertTrue(2350 <= twin.countdown.generate <= 2500, f"重置频率错误: {twin.countdown.generate}")


if __name__ == '__main__':
    unittest.main()
