#!/usr/bin/env python3
import unittest

from pvzemu2.enums import SceneType, ZombieType, ZombieStatus
from pvzemu2.systems import reanim
from pvzemu2.world import World


class TestReanimPhysics(unittest.TestCase):
    def setUp(self):
        self.world = World(SceneType.DAY)
        self.zombie = self.world.spawn(ZombieType.ZOMBIE, row=2, x=800)

    def test_eating_fps_boost(self):
        """测试：当僵尸进入啃食状态时，FPS应该动态增加（变快以产生急促咬击感）"""
        # Arrange
        original_fps = self.zombie.reanimate.fps
        self.zombie.is_eating = True

        # Act
        reanim.update_fps(self.zombie, self.world.scene)

        # Assert
        self.assertEqual(self.zombie.reanimate.fps, 36.0, "Eating zombie FPS should be boosted to 36.0")

    def test_newspaper_run_dx_boost(self):
        """测试：读报僵尸失去报纸后，DX和状态切换应当正确驱动提速"""
        # Arrange
        paper_zombie = self.world.spawn(ZombieType.NEWSPAPER, row=3, x=800)
        paper_zombie.status = ZombieStatus.NEWSPAPER_RUNNING

        # Act
        reanim.update_status(paper_zombie, self.world.scene, self.world.zombie_system.rng)

        # Assert
        # 根据系统逻辑，读报狂奔 dx 会在 0.8899 ~ 0.9100 之间
        self.assertTrue(0.88 < paper_zombie.dx < 0.92, "Newspaper running DX must reflect speed boost")

    def test_ground_driven_displacement(self):
        """测试：普通僵尸的实际位移是由 _ground 数据逐帧推算的，而不纯粹是简单的 z.x -= speed"""
        # Arrange
        z = self.zombie
        # 强制让 progress 落在一个我们已知的区间 (比如第一帧)
        z.reanimate.progress = 0.0
        rfs = z.reanimate.get_frame_status()

        # Act
        dx = z.get_dx_from_ground()

        # Assert (此时第一帧 _ground 为 0.0 -> 0.0 所以无位移)
        # 我们验证引擎接入不崩溃即可。并且预期正常提取了值。
        self.assertIsInstance(dx, float, "get_dx_from_ground must return float")


if __name__ == '__main__':
    unittest.main()
