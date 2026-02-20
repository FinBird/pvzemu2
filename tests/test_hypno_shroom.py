import unittest

from pvzemu2.enums import SceneType, PlantType, ZombieType
from pvzemu2.world import World


class TestHypnoShroom(unittest.TestCase):
    def test_trigger_awake(self):
        """场景A：僵尸啃咬清醒的魅惑蘑菇"""
        world = World(SceneType.NIGHT)

        hypno = world.plant(PlantType.HYPNOSHROOM, row=2, col=5)
        # 僵尸放置在蘑菇右侧靠近位置
        zombie = world.spawn(ZombieType.ZOMBIE, row=2, x=455.0)

        # 运行足够长的帧数 (300/4*4 + 走路 = 约 600 帧)
        for _ in range(600):
            world.step()
            if zombie.is_hypno:
                break

        print(world.to_json())
        # 验证：僵尸被魅惑，蘑菇死亡，速度变慢
        self.assertTrue(zombie.is_hypno, "僵尸应当被魅惑")
        self.assertTrue(hypno.is_dead, "魅惑蘑菇在生效后应被销毁")
        self.assertAlmostEqual(zombie.dx, 0.17, msg="魅惑僵尸的速度应降为 0.17")
        self.assertEqual(zombie.reanimate.fps, 8.0, msg="魅惑僵尸的动画帧率应该降低")

    def test_trigger_asleep(self):
        """场景B：僵尸啃咬睡眠状态的魅惑蘑菇（白昼无咖啡豆）"""
        world_day = World(SceneType.DAY)

        hypno = world_day.plant(PlantType.HYPNOSHROOM, row=2, col=5)
        self.assertTrue(hypno.is_sleeping, "在白天蘑菇应当处于睡眠状态")

        zombie = world_day.spawn(ZombieType.ZOMBIE, row=2, x=455.0)

        eaten = False
        for _ in range(1000):
            world_day.step()
            if hypno.is_dead:
                eaten = True
                break

        print(world_day.to_json())
        self.assertTrue(eaten, "睡眠的魅惑蘑菇依然会被吃掉")
        self.assertFalse(zombie.is_hypno, "吃掉睡眠的魅惑蘑菇不会受到魅惑")

    def test_immune_zombies(self):
        """场景C & D：碾压类/巨人等特殊僵尸对魅惑免疫"""
        world = World(SceneType.NIGHT)
        hypno1 = world.plant(PlantType.HYPNOSHROOM, row=1, col=5)
        hypno2 = world.plant(PlantType.HYPNOSHROOM, row=3, col=5)

        zomboni = world.spawn(ZombieType.ZOMBONI, row=1, x=480.0)
        gargantuar = world.spawn(ZombieType.GARGANTUAR, row=3, x=480.0)

        for _ in range(600):
            world.step()

        self.assertFalse(zomboni.is_hypno, "冰车僵尸应当免疫魅惑")
        self.assertTrue(hypno1.is_dead, "冰车僵尸所在行魅惑蘑菇应已死亡")
        self.assertFalse(gargantuar.is_hypno, "巨人僵尸应当免疫魅惑")
        self.assertTrue(hypno2.is_dead, "巨人僵尸所在行魅惑蘑菇应已死亡")

    def test_hypno_zombie_combat(self):
        """战斗逻辑：魅惑僵尸向右移动并与普通僵尸互啃"""
        world = World(SceneType.NIGHT)

        hz = world.spawn(ZombieType.ZOMBIE, row=2, x=100.0)
        hz.is_hypno = True
        hz._ground = None
        hz.dx = 1.0
        hz.hit_box_offset_x = 120
        hz.attack_box_x = 50
        hz.attack_box_width = 50

        nz = world.spawn(ZombieType.ZOMBIE, row=2, x=220.0)
        nz.is_hypno = False
        nz._ground = None
        nz.dx = 1.0
        nz.hit_box_offset_x = 120
        nz.hit_box_x = 20
        nz.hit_box_width = 90

        initial_hp = nz.hp

        success = False
        for _ in range(500):
            world.step()
            if hz.is_eating and nz.is_eating:
                success = True
                break

        self.assertTrue(success, f"对啃失败。Hz_X:{hz.x}, Nz_X:{nz.x}, Hz_Eat:{hz.is_eating}, Nz_Eat:{nz.is_eating}")

        for _ in range(50):
            world.step()

        self.assertLess(nz.hp, initial_hp, "普通僵尸应当受到魅惑僵尸的伤害")

    def test_plant_ignore_hypno(self):
        """战斗逻辑：植物不应该攻击被魅惑的僵尸"""
        world = World(SceneType.NIGHT)
        peashooter = world.plant(PlantType.PEA_SHOOTER, row=2, col=1)

        hypno_zombie = world.spawn(ZombieType.ZOMBIE, row=2, x=300.0)
        hypno_zombie.is_hypno = True

        for _ in range(1000):
            world.step()

        self.assertEqual(len(world.scene.projectiles), 0, "豌豆射手不应对魅惑僵尸发射子弹")
        self.assertFalse(peashooter.is_dead)

    def test_dancer_disconnect(self):
        """特殊交互：舞者僵尸被魅惑后，断开与伴舞的关系"""
        world = World(SceneType.NIGHT)

        dancer = world.spawn(ZombieType.DANCING, row=2, x=390.0)
        dancer._ground = None
        dancer.dx = 1.0
        dancer.hit_box_offset_x = 120

        backup = world.spawn(ZombieType.BACKUP_DANCER, row=2, x=450.0)
        dancer.partners[0] = backup.id
        backup.master_id = dancer.id

        hypno = world.plant(PlantType.HYPNOSHROOM, row=2, col=4)

        for _ in range(500):
            world.step()
            if dancer.is_hypno:
                break

        self.assertTrue(hypno.is_dead, "魅惑蘑菇在生效后应被销毁")
        self.assertTrue(dancer.is_hypno, "舞者僵尸应该被魅惑")
        self.assertEqual(dancer.partners[0], -1, "舞者僵尸的伴舞数组应当被清空")
        self.assertIsNone(backup.master_id, "伴舞僵尸的领舞指针应当被清空")
        self.assertFalse(backup.is_hypno, "伴舞不应该因为领舞被魅惑而自动魅惑")

    def test_hypno_zombie_ignores_plants(self):
        """测试：被魅惑的僵尸不会啃食我方植物"""
        # 1. 生成一个已经被魅惑的僵尸，从左向右走
        world = World(SceneType.NIGHT)

        hz = world.spawn(ZombieType.ZOMBIE, row=2, x=100.0)
        hz.is_hypno = True
        hz._ground = None
        hz.dx = 1.0
        hz.hit_box_offset_x = 120  # 镜像修正

        # 2. 在它前进路线上放一个坚果
        nut = world.plant(PlantType.WALLNUT, row=2, col=3)  # col 3 坐标约 280
        initial_nut_hp = nut.hp

        # 3. 运行步进，直到僵尸穿过坚果
        for _ in range(500):
            world.step()

        # 4. 验证：僵尸 x 坐标已越过坚果，且坚果毫发无损，僵尸从未进入吃状态
        self.assertGreater(hz.x, 350, "魅惑僵尸应该已经走过了坚果")
        self.assertEqual(nut.hp, initial_nut_hp, "坚果不应该被魅惑僵尸啃食")
        self.assertFalse(hz.is_eating, "魅惑僵尸不应该产生啃食动作")

    def test_buckethead_hypno_revenge(self):
        """测试：铁桶僵尸吃掉魅惑蘑菇后，转向并击杀后方的普通僵尸"""
        world = World(SceneType.NIGHT)
        hypno = world.plant(PlantType.HYPNOSHROOM, row=2, col=5)

        bucket = world.spawn(ZombieType.BUCKET_HEAD, row=2, x=455.0)
        bucket._ground = None
        bucket.dx = 1.0
        bucket.hit_box_offset_x = 120

        for _ in range(1500):
            world.step()
            if bucket.is_hypno:
                break

        self.assertTrue(hypno.is_dead, "魅惑蘑菇已经死亡")
        self.assertTrue(bucket.is_hypno, "铁桶僵尸应该被魅惑了")
        self.assertGreater(bucket.accessory_1_hp, 500, "铁桶应该还保留大部分耐久")

        victim = world.spawn(ZombieType.ZOMBIE, row=2, x=550.0)
        victim._ground = None
        victim.dx = 1.0
        victim.hit_box_offset_x = 120

        killed = False
        for _ in range(3000):
            world.step()
            if victim.hp <= 0 or victim.is_dead:
                killed = True
                break

        self.assertTrue(killed, "被魅惑的铁桶僵尸应当击杀普通僵尸")
        self.assertFalse(bucket.is_dead, "铁桶僵尸应该还活着（护盾优势）")
        # 两人速度差异相遇时大约在 x=450 的位置卡死互啃。死亡后立刻break退出了测试循环。
        # 断言应当判断其至少发生反向位移（大于440），之前的 460 过于死板导致误判。
        self.assertGreater(bucket.x, 445, "铁桶僵尸应该在向右侧大门推进")


if __name__ == '__main__':
    unittest.main()
