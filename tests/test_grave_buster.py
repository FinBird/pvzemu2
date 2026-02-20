import unittest

from pvzemu2.enums import PlantType, PlantStatus, SceneType, GridItemType
from pvzemu2.objects.base import ReanimateType
from pvzemu2.scene import Scene
from pvzemu2.systems.damage import DamageSystem
from pvzemu2.systems.griditem_factory import GridItemFactory
from pvzemu2.systems.plant_factory import PlantFactory
from pvzemu2.systems.plant_system import PlantSystem
from pvzemu2.systems.projectile_factory import ProjectileFactory


class TestGraveBuster(unittest.TestCase):
    def setUp(self):
        self.scene = Scene(SceneType.NIGHT)  # 墓碑通常在夜晚场景
        self.plant_factory = PlantFactory(self.scene)
        self.damage_system = DamageSystem(self.scene)
        self.projectile_factory = ProjectileFactory(self.scene)
        self.plant_system = PlantSystem(self.scene, self.projectile_factory, self.damage_system, self.plant_factory)
        self.griditem_factory = GridItemFactory(self.scene)

    def test_grave_buster_initial_state(self):
        """测试墓碑吞噬者创建后的初始状态"""
        grave_buster = self.plant_factory.create(PlantType.GRAVE_BUSTER, 2, 2)
        self.assertEqual(grave_buster.type, PlantType.GRAVE_BUSTER)
        # 墓碑吞噬者应该处于 LAND 状态
        self.assertEqual(grave_buster.status, PlantStatus.GRAVE_BUSTER_LAND)

    def test_grave_buster_transitions_to_idle_after_landing_animation(self):
        """测试着陆动画完成后墓碑吞噬者转换为空闲状态"""
        grave_buster = self.plant_factory.create(PlantType.GRAVE_BUSTER, 2, 2)

        # 模拟动画完成
        grave_buster.reanimate.n_repeated = 1

        # 更新植物系统
        self.plant_system.update()

        # 应该进入 IDLE 状态
        self.assertEqual(grave_buster.status, PlantStatus.GRAVE_BUSTER_IDLE)
        # 应该设置 countdown.status
        self.assertEqual(grave_buster.countdown.status, 400)
        # 动画类型应该设置为 REPEAT
        self.assertEqual(grave_buster.reanimate.type, ReanimateType.REPEAT)

    def test_grave_buster_remains_in_land_state_if_animation_not_complete(self):
        """测试动画未完成时墓碑吞噬者保持 LAND 状态"""
        grave_buster = self.plant_factory.create(PlantType.GRAVE_BUSTER, 2, 2)

        # 动画未完成
        grave_buster.reanimate.n_repeated = 0

        # 更新植物系统
        self.plant_system.update()

        # 应该保持 LAND 状态
        self.assertEqual(grave_buster.status, PlantStatus.GRAVE_BUSTER_LAND)

    def test_grave_buster_destroys_grave_when_countdown_zero(self):
        """测试倒计时为0时墓碑吞噬者摧毁墓碑"""
        # 创建墓碑
        grave = self.griditem_factory.create(GridItemType.GRAVE, 2, 2)

        # 创建墓碑吞噬者在同一位置
        grave_buster = self.plant_factory.create(PlantType.GRAVE_BUSTER, 2, 2)

        # 设置为 IDLE 状态，countdown 为 0
        grave_buster.status = PlantStatus.GRAVE_BUSTER_IDLE
        grave_buster.countdown.status = 0

        # 保存初始墓碑数量
        initial_grave_count = len([item for item in self.scene.grid_items if item.type == GridItemType.GRAVE])

        # 更新植物系统
        self.plant_system.update()

        # 墓碑应该被摧毁
        final_grave_count = len([item for item in self.scene.grid_items if item.type == GridItemType.GRAVE])
        self.assertEqual(final_grave_count, initial_grave_count - 1)

        # 墓碑吞噬者应该被摧毁
        self.assertTrue(grave_buster.is_dead)

    def test_grave_buster_does_nothing_when_no_grave(self):
        """测试没有墓碑时墓碑吞噬者不执行任何操作"""
        # 创建墓碑吞噬者，但不在墓碑上
        grave_buster = self.plant_factory.create(PlantType.GRAVE_BUSTER, 2, 2)

        # 设置为 IDLE 状态，countdown 为 0
        grave_buster.status = PlantStatus.GRAVE_BUSTER_IDLE
        grave_buster.countdown.status = 0

        # 保存初始植物数量
        initial_plant_count = len(self.scene.plants)

        # 更新植物系统
        self.plant_system.update()

        # 墓碑吞噬者应该被摧毁（即使没有墓碑）
        # 根据代码逻辑，即使没有找到墓碑，也会调用 plant_factory.destroy(plant)
        final_plant_count = len(self.scene.plants)
        self.assertEqual(final_plant_count, initial_plant_count - 1)

    def test_grave_buster_countdown_decrements(self):
        """测试墓碑吞噬者的倒计时递减"""
        grave_buster = self.plant_factory.create(PlantType.GRAVE_BUSTER, 2, 2)

        # 设置为 IDLE 状态，设置 countdown
        grave_buster.status = PlantStatus.GRAVE_BUSTER_IDLE
        grave_buster.countdown.status = 10

        # 更新植物系统多次
        for i in range(10):
            self.plant_system.update()

        # countdown.status 应该递减到 0
        self.assertEqual(grave_buster.countdown.status, 0)

        # 再次更新应该触发墓碑摧毁逻辑
        self.plant_system.update()
        # 墓碑吞噬者应该被摧毁
        self.assertTrue(grave_buster.is_dead)

    def test_grave_buster_only_destroys_grave_in_same_cell(self):
        """测试墓碑吞噬者只摧毁同一单元格的墓碑"""
        # 在 (2,2) 创建墓碑
        grave1 = self.griditem_factory.create(GridItemType.GRAVE, 2, 2)
        # 在 (2,3) 创建另一个墓碑
        grave2 = self.griditem_factory.create(GridItemType.GRAVE, 2, 3)

        # 在 (2,2) 创建墓碑吞噬者
        grave_buster = self.plant_factory.create(PlantType.GRAVE_BUSTER, 2, 2)

        # 设置为 IDLE 状态，countdown 为 0
        grave_buster.status = PlantStatus.GRAVE_BUSTER_IDLE
        grave_buster.countdown.status = 0

        # 保存初始墓碑数量
        initial_grave_count = len([item for item in self.scene.grid_items if item.type == GridItemType.GRAVE])

        # 更新植物系统
        self.plant_system.update()

        # 应该只摧毁一个墓碑
        final_grave_count = len([item for item in self.scene.grid_items if item.type == GridItemType.GRAVE])
        self.assertEqual(final_grave_count, initial_grave_count - 1)

        # 检查 (2,3) 的墓碑是否仍然存在
        grave2_still_exists = any(
            item for item in self.scene.grid_items
            if item.type == GridItemType.GRAVE and item.row == 2 and item.col == 3
        )
        self.assertTrue(grave2_still_exists)

    def test_grave_buster_animation_settings(self):
        """测试墓碑吞噬者的动画设置"""
        grave_buster = self.plant_factory.create(PlantType.GRAVE_BUSTER, 2, 2)

        # 初始状态为 LAND
        self.assertEqual(grave_buster.status, PlantStatus.GRAVE_BUSTER_LAND)

        # 模拟动画完成
        grave_buster.reanimate.n_repeated = 1
        self.plant_system.update()

        # 应该进入 IDLE 状态
        self.assertEqual(grave_buster.status, PlantStatus.GRAVE_BUSTER_IDLE)
        # 动画应该设置为空闲动画
        # 注意：set_reanim_frame 方法可能不存在或需要模拟
        # 我们至少可以验证状态转换和动画类型
        self.assertEqual(grave_buster.reanimate.type, ReanimateType.REPEAT)

    def test_grave_buster_on_grave_vs_empty_cell(self):
        """测试墓碑吞噬者在墓碑上 vs 空单元格的行为"""
        # 测试场景1：有墓碑
        grave = self.griditem_factory.create(GridItemType.GRAVE, 3, 3)
        grave_buster1 = self.plant_factory.create(PlantType.GRAVE_BUSTER, 3, 3)
        grave_buster1.status = PlantStatus.GRAVE_BUSTER_IDLE
        grave_buster1.countdown.status = 0

        initial_grave_count = len([item for item in self.scene.grid_items if item.type == GridItemType.GRAVE])
        self.plant_system.update()

        # 墓碑应该被摧毁
        final_grave_count = len([item for item in self.scene.grid_items if item.type == GridItemType.GRAVE])
        self.assertEqual(final_grave_count, initial_grave_count - 1)

        # 测试场景2：无墓碑
        grave_buster2 = self.plant_factory.create(PlantType.GRAVE_BUSTER, 4, 4)
        grave_buster2.status = PlantStatus.GRAVE_BUSTER_IDLE
        grave_buster2.countdown.status = 0

        initial_plant_count = len(self.scene.plants)
        self.plant_system.update()

        # 墓碑吞噬者应该被摧毁
        final_plant_count = len(self.scene.plants)
        self.assertEqual(final_plant_count, initial_plant_count - 1)


if __name__ == '__main__':
    unittest.main()
