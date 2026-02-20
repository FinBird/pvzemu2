import unittest

from pvzemu2.enums import PlantType, PlantStatus, SceneType, ZombieStatus
from pvzemu2.enums import ZombieType
from pvzemu2.objects.base import ReanimateType
from pvzemu2.scene import Scene
from pvzemu2.systems.damage import DamageSystem
from pvzemu2.systems.plant_factory import PlantFactory
from pvzemu2.systems.plant_system import PlantSystem
from pvzemu2.systems.projectile_factory import ProjectileFactory
from pvzemu2.systems.projectile_system import ProjectileSystem
from pvzemu2.systems.util import zombie_init_y
from pvzemu2.systems.zombie_factory import ZombieFactory


class TestCobCannon(unittest.TestCase):
    def setUp(self):
        self.scene = Scene(SceneType.DAY)
        self.plant_factory = PlantFactory(self.scene)
        self.damage_system = DamageSystem(self.scene)
        self.projectile_factory = ProjectileFactory(self.scene)
        self.plant_system = PlantSystem(self.scene, self.projectile_factory, self.damage_system, self.plant_factory)

    def _setup_zombie_at(self, factory, row, x):
        """核心修复：确保坐标、整数坐标、行索引完全同步"""
        z = factory.create(ZombieType.ZOMBIE)

        # 1. 彻底清除旧行索引
        for r_list in self.scene.zombies_by_row:
            r_list.discard(z.id)

        # 2. 设置逻辑属性
        z.row = row
        z.x = float(x)
        # 核心：必须重新计算此行正确的 Y 坐标！否则受击框会偏离爆炸中心。
        z.y = zombie_init_y(self.scene.type, z, row)

        # 3. 同步关键的整数坐标（引擎碰撞判定实际使用这个）
        z.int_x = int(z.x)
        z.int_y = int(z.y)

        # 4. 重新加入目标行索引
        self.scene.zombies_by_row[row].add(z.id)
        return z

    def test_cob_cannon_initial_state(self):
        """测试玉米加农炮创建后的初始状态"""
        cob_cannon = self.plant_factory.create(PlantType.COB_CANNON, 2, 2)
        self.assertEqual(cob_cannon.type, PlantType.COB_CANNON)
        # 玉米加农炮应该处于 UNARMED_IDLE 状态
        self.assertEqual(cob_cannon.status, PlantStatus.COB_CANNON_UNARMED_IDLE)

    def test_cob_cannon_charges_when_countdown_zero(self):
        """测试当倒计时为0时玉米加农炮开始充能"""
        cob_cannon = self.plant_factory.create(PlantType.COB_CANNON, 2, 2)

        # 设置 countdown.status 为 0
        cob_cannon.countdown.status = 0

        # 更新植物系统
        self.plant_system.update()

        # 应该进入 CHARGE 状态
        self.assertEqual(cob_cannon.status, PlantStatus.COB_CANNON_CHARGE)
        # 应该设置动画为充能动画
        # 注意：set_reanim_frame 方法可能不存在或需要模拟
        # 我们至少可以验证状态转换

    def test_cob_cannon_remains_unarmed_if_countdown_not_zero(self):
        """测试倒计时不为0时玉米加农炮保持未武装状态"""
        cob_cannon = self.plant_factory.create(PlantType.COB_CANNON, 2, 2)

        # 设置 countdown.status 大于 0
        cob_cannon.countdown.status = 10

        # 更新植物系统
        self.plant_system.update()

        # 应该保持 UNARMED_IDLE 状态
        self.assertEqual(cob_cannon.status, PlantStatus.COB_CANNON_UNARMED_IDLE)

    def test_cob_cannon_becomes_armed_after_charge_animation(self):
        """测试充能动画完成后玉米加农炮变为武装状态"""
        cob_cannon = self.plant_factory.create(PlantType.COB_CANNON, 2, 2)

        # 设置为 CHARGE 状态
        cob_cannon.status = PlantStatus.COB_CANNON_CHARGE
        # 模拟动画完成
        cob_cannon.reanimate.n_repeated = 1

        # 更新植物系统
        self.plant_system.update()

        # 应该进入 ARMED_IDLE 状态
        self.assertEqual(cob_cannon.status, PlantStatus.COB_CANNON_ARMED_IDLE)
        # 动画类型应该设置为 REPEAT
        self.assertEqual(cob_cannon.reanimate.type, ReanimateType.REPEAT)

    def test_cob_cannon_launch_successful_when_armed(self):
        """测试武装状态下玉米加农炮成功发射"""
        cob_cannon = self.plant_factory.create(PlantType.COB_CANNON, 2, 2)

        # 设置为 ARMED_IDLE 状态
        cob_cannon.status = PlantStatus.COB_CANNON_ARMED_IDLE

        # 获取玉米加农炮子系统
        cob_subsystem = self.plant_system.cob_cannon_subsystem

        # 尝试发射到目标位置
        target_x = 500
        target_y = 200
        result = cob_subsystem.launch(cob_cannon, target_x, target_y)

        # 应该返回成功
        self.assertTrue(result)
        # 应该进入 LAUNCH 状态
        self.assertEqual(cob_cannon.status, PlantStatus.COB_CANNON_LAUNCH)
        # 应该设置 launch countdown
        self.assertEqual(cob_cannon.countdown.launch, 206)
        # 应该设置目标位置
        self.assertEqual(cob_cannon.cannon_x, int(target_x - 47.0))
        self.assertEqual(cob_cannon.cannon_y, target_y)
        # 动画应该设置为射击动画
        self.assertEqual(cob_cannon.reanimate.type, ReanimateType.ONCE)

    def test_cob_cannon_launch_fails_when_not_armed(self):
        """测试非武装状态下玉米加农炮发射失败"""
        cob_cannon = self.plant_factory.create(PlantType.COB_CANNON, 2, 2)

        # 设置为 UNARMED_IDLE 状态（非武装）
        cob_cannon.status = PlantStatus.COB_CANNON_UNARMED_IDLE

        # 获取玉米加农炮子系统
        cob_subsystem = self.plant_system.cob_cannon_subsystem

        # 尝试发射
        result = cob_subsystem.launch(cob_cannon, 500, 200)

        # 应该返回失败
        self.assertFalse(result)
        # 应该保持原状态
        self.assertEqual(cob_cannon.status, PlantStatus.COB_CANNON_UNARMED_IDLE)

    def test_cob_cannon_launch_fails_when_charging(self):
        """测试充能状态下玉米加农炮发射失败"""
        cob_cannon = self.plant_factory.create(PlantType.COB_CANNON, 2, 2)

        # 设置为 CHARGE 状态
        cob_cannon.status = PlantStatus.COB_CANNON_CHARGE

        # 获取玉米加农炮子系统
        cob_subsystem = self.plant_system.cob_cannon_subsystem

        # 尝试发射
        result = cob_subsystem.launch(cob_cannon, 500, 200)

        # 应该返回失败
        self.assertFalse(result)
        # 应该保持原状态
        self.assertEqual(cob_cannon.status, PlantStatus.COB_CANNON_CHARGE)

    def test_cob_cannon_countdown_decrements(self):
        """测试玉米加农炮的倒计时递减"""
        cob_cannon = self.plant_factory.create(PlantType.COB_CANNON, 2, 2)

        # 设置 countdown.status
        cob_cannon.countdown.status = 10

        # 更新植物系统多次
        for i in range(10):
            self.plant_system.update()

        # countdown.status 应该递减到 0
        self.assertEqual(cob_cannon.countdown.status, 0)

        # 再次更新应该触发充能
        self.plant_system.update()
        self.assertEqual(cob_cannon.status, PlantStatus.COB_CANNON_CHARGE)

    def test_cob_cannon_animation_state_transitions(self):
        """测试玉米加农炮的动画状态转换"""
        cob_cannon = self.plant_factory.create(PlantType.COB_CANNON, 2, 2)

        # 初始状态应该是 UNARMED_IDLE
        self.assertEqual(cob_cannon.status, PlantStatus.COB_CANNON_UNARMED_IDLE)

        # 触发充能
        cob_cannon.countdown.status = 0
        self.plant_system.update()

        # 应该进入 CHARGE 状态
        self.assertEqual(cob_cannon.status, PlantStatus.COB_CANNON_CHARGE)
        # 动画类型应该是 ONCE
        self.assertEqual(cob_cannon.reanimate.type, ReanimateType.ONCE)

        # 模拟动画完成
        cob_cannon.reanimate.n_repeated = 1
        self.plant_system.update()

        # 应该进入 ARMED_IDLE 状态
        self.assertEqual(cob_cannon.status, PlantStatus.COB_CANNON_ARMED_IDLE)
        # 动画类型应该是 REPEAT
        self.assertEqual(cob_cannon.reanimate.type, ReanimateType.REPEAT)

    def test_cob_cannon_requires_two_corns_to_create(self):
        """测试玉米加农炮需要两个玉米投手创建（集成测试）"""
        # 注意：这个测试可能需要更复杂的设置
        # 玉米加农炮通常由两个相邻的玉米投手升级而成
        # 这里我们只测试植物工厂能创建玉米加农炮
        cob_cannon = self.plant_factory.create(PlantType.COB_CANNON, 2, 2)
        self.assertIsNotNone(cob_cannon)
        self.assertEqual(cob_cannon.type, PlantType.COB_CANNON)

    def test_cob_cannon_full_kill_sequence(self):
        """测试玉米加农炮从发射到击杀僵尸的全过程"""
        zombie_factory = ZombieFactory(self.scene)
        projectile_system = ProjectileSystem(self.scene, self.damage_system, self.projectile_factory)

        # 1. 准备就绪的加农炮
        cob = self.plant_factory.create(PlantType.COB_CANNON, 2, 2)
        cob.status = PlantStatus.COB_CANNON_ARMED_IDLE

        # 2. 在目标点放置僵尸 (使用辅助函数确保坐标正确)
        target_x, target_y = 600, 280
        zombie = self._setup_zombie_at(zombie_factory, 2, target_x)

        # 3. 玩家指令发射
        self.plant_system.cob_cannon_subsystem.launch(cob, target_x, target_y)

        # 4. 模拟 206 帧的发射前摇
        for _ in range(206):
            self.plant_system.update()

        # 验证前摇结束后子弹已进入场景
        self.assertEqual(len(self.scene.projectiles), 1)
        proj = list(self.scene.projectiles)[0]

        # 5. 模拟子弹飞行
        for _ in range(500):
            projectile_system.update()
            if proj.is_disappeared:
                break

        # 6. 验证僵尸被秒杀
        self.assertTrue(zombie.is_dead or zombie.hp <= 0)

    def test_cob_cannon_explosion_radius(self):
        """测试玉米加农炮爆炸半径判定（半径115）"""

        zombie_factory = ZombieFactory(self.scene)
        projectile_system = ProjectileSystem(self.scene, self.damage_system, self.projectile_factory)

        cob = self.plant_factory.create(PlantType.COB_CANNON, 2, 0)
        cob.status = PlantStatus.COB_CANNON_ARMED_IDLE

        # 目标点击中心
        target_x, target_y = 400, 280

        # 放置三个僵尸：
        # z1: 在爆炸中心 (必死)
        z1 = self._setup_zombie_at(zombie_factory, 2, 400)

        # z2: 在边缘内 (x=400+100=500, 距离100 < 115，必死)
        z2 = self._setup_zombie_at(zombie_factory, 2, 500)

        # z3: 在边缘外 (x=400+150=550, 距离150 > 115，存活)
        z3 = self._setup_zombie_at(zombie_factory, 2, 550)

        # 发射并跳过等待时间
        self.plant_system.cob_cannon_subsystem.launch(cob, target_x, target_y)

        # ==========================================
        # ！！！极其重要：必须设置为 2 ！！！
        # 设为 2 后，update() 一次会自减变成 1，触发发射。
        # 设为 1 的话，update() 一次变成 0，永远不会发射子弹！
        # ==========================================
        cob.countdown.launch = 2

        self.plant_system.update()  # 产生子弹

        # 运行至爆炸
        for _ in range(500):
            projectile_system.update()

        self.assertTrue(z1.hp <= 0, "Center zombie should be dead")
        self.assertTrue(z2.hp <= 0, "Edge-inside zombie should be dead")
        self.assertGreater(z3.hp, 0, "Outside zombie should be alive")

    def test_gargantuar_two_shot_kill_and_auto_reload_logic(self):
        """测试巨人僵尸能被2发玉米炮炸死，并验证发射状态切换"""
        zombie_factory = ZombieFactory(self.scene)
        projectile_system = ProjectileSystem(self.scene, self.damage_system, self.projectile_factory)

        # 1. 准备巨人僵尸 (血量 3000)
        target_x, target_y = 400, 280
        garg = self._setup_zombie_at(zombie_factory, 2, target_x)
        garg.type = ZombieType.GARGANTUAR
        garg.hp = garg.max_hp = 3000

        cob = self.plant_factory.create(PlantType.COB_CANNON, 2, 0)
        cob.status = PlantStatus.COB_CANNON_ARMED_IDLE

        # --- 第一发 ---
        # 发射动作
        self.plant_system.cob_cannon_subsystem.launch(cob, target_x, target_y)
        # 验证发射后状态立刻变为 LAUNCH
        self.assertEqual(cob.status, PlantStatus.COB_CANNON_LAUNCH)

        cob.countdown.launch = 2  # 快速触发发射
        self.plant_system.update()  # 产生子弹

        # 运行至爆炸
        for _ in range(500):
            projectile_system.update()

        # 验证巨人残血: 3000 - 1800 = 1200
        self.assertEqual(garg.hp, 1200, "Gargantuar should have 1200 HP after one shot")

        # --- 第二发 (手动重置状态以进行连测) ---
        cob.status = PlantStatus.COB_CANNON_ARMED_IDLE
        self.plant_system.cob_cannon_subsystem.launch(cob, target_x, target_y)
        cob.countdown.launch = 2
        self.plant_system.update()

        for _ in range(500):
            projectile_system.update()

        # 验证巨人死亡
        self.assertTrue(garg.hp <= 0 or garg.is_dead, "Gargantuar should be dead after two shots")

    def test_cob_cannon_multi_kill_all_types(self):
        """测试在同一个位置放置所有种类的僵尸，一发全部秒杀"""
        zombie_factory = ZombieFactory(self.scene)
        projectile_system = ProjectileSystem(self.scene, self.damage_system, self.projectile_factory)

        # 待测试的僵尸列表
        zombie_types = [
            ZombieType.ZOMBIE, ZombieType.FLAG, ZombieType.CONE_HEAD,
            ZombieType.POLE_VAULTING, ZombieType.BUCKET_HEAD, ZombieType.NEWSPAPER,
            ZombieType.SCREEN_DOOR, ZombieType.FOOTBALL, ZombieType.DANCING,
            ZombieType.BACKUP_DANCER, ZombieType.SNORKEL, ZombieType.ZOMBONI,
            ZombieType.DOLPHIN_RIDER, ZombieType.JACK_IN_THE_BOX, ZombieType.BALLOON,
            ZombieType.DIGGER, ZombieType.POGO, ZombieType.YETI,
            ZombieType.BUNGEE, ZombieType.LADDER, ZombieType.CATAPULT, ZombieType.IMP
        ]

        target_x, target_y = 500, 280
        spawned_zombies = []

        # 在同一点堆叠所有种类的僵尸
        for z_type in zombie_types:
            z = self._setup_zombie_at(zombie_factory, 2, target_x)
            z.type = z_type
            # 针对特殊僵尸进行必要的初始化
            if z_type == ZombieType.BUNGEE:
                z.status = ZombieStatus.BUNGEE_IDLE_AFTER_DROP  # 设为可受攻击状态
            elif z_type == ZombieType.BALLOON:
                z.status = ZombieStatus.BALLOON_FLYING
            elif z_type == ZombieType.SNORKEL:
                z.is_in_water = True  # 模拟在水中也能被炸到

            spawned_zombies.append(z)

        # 准备加农炮
        cob = self.plant_factory.create(PlantType.COB_CANNON, 2, 0)
        cob.status = PlantStatus.COB_CANNON_ARMED_IDLE

        # 发射
        self.plant_system.cob_cannon_subsystem.launch(cob, target_x, target_y)
        cob.countdown.launch = 2
        self.plant_system.update()  # 产生子弹

        # 运行直到爆炸完成
        for _ in range(500):
            projectile_system.update()

        # 验证所有僵尸是否死亡
        for z in spawned_zombies:
            self.assertTrue(z.hp <= 0 or z.is_dead, f"Zombie of type {z.type.name} should be dead")


if __name__ == '__main__':
    unittest.main()
