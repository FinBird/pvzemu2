from typing import Optional

from pvzemu2.enums import ZombieType, SceneType, ZombieStatus, ZombieAction, ZombieAccessoriesType1, \
    ZombieAccessoriesType2
from pvzemu2.objects.zombie import Zombie
from pvzemu2.scene import Scene
from pvzemu2.systems.rng import RNG
from pvzemu2.systems.util import get_y_by_row_and_col


class ZombieFactory:
    def __init__(self, scene: Scene) -> None:
        self.scene = scene
        self.rng = RNG(scene)

    def create(self, zombie_type: ZombieType, spawn_wave: Optional[int] = None) -> Zombie:
        row = self._get_spawn_row(zombie_type)
        if spawn_wave is None:
            spawn_wave = self.scene.spawn.wave

        zombie = Zombie(
            type=zombie_type,
            row=row,
            x=800 + self.rng.randint(40),
            y=0.0
        )

        # 基础属性初始化
        zombie.hp = 270
        zombie.max_hp = 270
        zombie.dx = 0.23

        # 初始化判定框 (默认值，适用于普通/路障/铁桶等标准体型僵尸)
        # 宽80 高100 确保能被子弹击中且能吃到植物
        # 注意：Zombie 类使用单独的属性而不是 Rect 对象
        zombie.hit_box_x = 20
        zombie.hit_box_y = 0
        zombie.hit_box_width = 90
        zombie.hit_box_height = 100
        zombie.hit_box_offset_x = 0  # 默认值
        zombie.hit_box_offset_y = 0  # 默认值

        zombie.attack_box_x = 50
        zombie.attack_box_y = 0
        zombie.attack_box_width = 50
        zombie.attack_box_height = 100

        # 初始化特定属性
        if zombie_type == ZombieType.CONE_HEAD:
            zombie.accessory_1_type = ZombieAccessoriesType1.ROADCONE
            zombie.accessory_1_hp = 370
            zombie.accessory_1_max_hp = 370
        elif zombie_type == ZombieType.BUCKET_HEAD:
            zombie.accessory_1_type = ZombieAccessoriesType1.BUCKET
            zombie.accessory_1_hp = 1100
            zombie.accessory_1_max_hp = 1100
        elif zombie_type == ZombieType.SCREEN_DOOR:
            zombie.accessory_2_type = ZombieAccessoriesType2.SCREEN_DOOR
            zombie.accessory_2_hp = 1100
            zombie.accessory_2_max_hp = 1100
        elif zombie_type == ZombieType.LADDER:
            zombie.accessory_2_type = ZombieAccessoriesType2.LADDER
            zombie.accessory_2_hp = 500
            zombie.accessory_2_max_hp = 500
            zombie.hp = 500
            zombie.max_hp = 500
        elif zombie_type == ZombieType.FOOTBALL:
            zombie.accessory_1_type = ZombieAccessoriesType1.FOOTBALL_CAP
            zombie.accessory_1_hp = 1400
            zombie.accessory_1_max_hp = 1400
            zombie.dx = 0.47
        elif zombie_type == ZombieType.POLE_VAULTING:
            zombie.hp = 500
            zombie.max_hp = 500
            zombie.dx = 0.37
            zombie.status = ZombieStatus.POLE_VALUTING_RUNNING
        elif zombie_type == ZombieType.FOOTBALL:
            zombie.hp = 1670
            zombie.max_hp = 1670
            zombie.dx = 0.47
        elif zombie_type == ZombieType.NEWSPAPER:
            zombie.hp = 420
            zombie.max_hp = 420
            zombie.status = ZombieStatus.NEWSPAPER_WALKING
        elif zombie_type == ZombieType.SCREEN_DOOR:
            zombie.hp = 1370
            zombie.max_hp = 1370
        elif zombie_type == ZombieType.GARGANTUAR:
            zombie.hp = 3000
            zombie.max_hp = 3000
            zombie.hit_box_width = 150
            zombie.hit_box_height = 150
            zombie.attack_box_width = 100
            zombie.attack_box_height = 150
        elif zombie_type == ZombieType.IMP:
            zombie.hp = 50
            zombie.max_hp = 50
            zombie.dx = 0.4
            zombie.hit_box_x = 10
            zombie.hit_box_width = 50
            zombie.hit_box_height = 60
            zombie.attack_box_x = 10
            zombie.attack_box_width = 30
            zombie.attack_box_height = 60

        # 坐标修正
        zombie.y = float(get_y_by_row_and_col(self.scene.type, row, 9) - 30)
        zombie.int_x, zombie.int_y = int(zombie.x), int(zombie.y)

        # 水路修正
        if self.scene.type in (SceneType.POOL, SceneType.FOG) and (row == 2 or row == 3):
            zombie.y += 20
            # TODO: 如果是普通僵尸在水路，应该变身 ducky_tube

        self.scene.zombies.add(zombie)
        if 0 <= row < len(self.scene.zombies_by_row):
            self.scene.zombies_by_row[row].add(zombie.id)

        return zombie

    def create_lurking(self, zombie_type: ZombieType, row: int, col: int) -> None:
        if self.scene.type in (SceneType.POOL, SceneType.FOG, SceneType.NIGHT):
            self._create_pool_or_night_lurking(zombie_type, row, col)
        elif self.scene.type in (SceneType.ROOF, SceneType.MOON_NIGHT):
            self._create_roof_lurking(zombie_type, row, col)

    def _create_pool_or_night_lurking(self, zombie_type: ZombieType, row: int, col: int) -> None:
        zombie = self.create(zombie_type)
        zombie.row = row
        zombie.x = float(80 * col + 15)
        zombie.y = float(get_y_by_row_and_col(self.scene.type, row, col))

        if self.scene.type == SceneType.NIGHT:
            zombie.dy = -200.0
            zombie.countdown.action = 150
        else:
            zombie.dy = -150.0
            zombie.countdown.action = 50
            zombie.action = ZombieAction.NONE

        zombie.int_x = int(zombie.x)
        zombie.int_y = int(zombie.y)
        zombie.status = ZombieStatus.RISING_FROM_GROUND

    def _create_roof_lurking(self, zombie_type: ZombieType, row: int, col: int) -> None:
        bungee = self.create(ZombieType.BUNGEE)
        target = self.create(zombie_type)

        bungee.row = row
        bungee.x = float(80 * col + 40)
        bungee.y = -100.0

        # 绑定关系 (暂时简化，因为 Zombie 类可能缺少 bungee_col 等字段)
        bungee.master_id = target.id
        target.master_id = bungee.id  # 可选双向绑定

        target.x = bungee.x - 15
        target.row = row
        target.action = ZombieAction.FALL_FROM_SKY

    def destroy(self, z: Zombie) -> None:
        z.is_dead = True
        self.scene.zombies.remove_obj(z)
        if 0 <= z.row < len(self.scene.zombies_by_row):
            self.scene.zombies_by_row[z.row].discard(z.id)

        # TODO: Handle Bungee logic

    def _can_spawn_at_row(self, zombie_type: ZombieType, row: int) -> bool:
        if row >= self.scene.rows:
            return False

        scene_type = self.scene.type
        wave = self.scene.spawn.wave

        if zombie_type in (
        ZombieType.ZOMBIE, ZombieType.FLAG, ZombieType.CONE_HEAD, ZombieType.BUCKET_HEAD, ZombieType.BALLOON,
        ZombieType.BUNGEE):
            if scene_type in (SceneType.POOL, SceneType.FOG):
                return row in (0, 1, 4, 5) or wave >= 5
            return True

        elif zombie_type in (
        ZombieType.POLE_VAULTING, ZombieType.NEWSPAPER, ZombieType.SCREEN_DOOR, ZombieType.FOOTBALL,
        ZombieType.JACK_IN_THE_BOX, ZombieType.BACKUP_DANCER, ZombieType.DIGGER, ZombieType.ZOMBONI,
        ZombieType.POGO, ZombieType.YETI, ZombieType.LADDER, ZombieType.CATAPULT, ZombieType.GARGANTUAR,
        ZombieType.IMP, ZombieType.GIGA_GARGANTUAR):
            if scene_type in (SceneType.POOL, SceneType.FOG):
                return row in (0, 1, 4, 5)
            return True

        elif zombie_type == ZombieType.DANCING:
            if scene_type in (SceneType.DAY, SceneType.NIGHT):
                return row in (1, 2, 3)
            elif scene_type in (SceneType.POOL, SceneType.FOG):
                return row in (0, 1, 4, 5)
            return False

        elif zombie_type in (ZombieType.DUCKY_TUBE, ZombieType.SNORKEL, ZombieType.DOLPHIN_RIDER):
            return scene_type in (SceneType.POOL, SceneType.FOG) and row in (2, 3)

        return False

    def _get_spawn_row(self, zombie_type: ZombieType) -> int:
        sigma_b = 0.0

        for i in range(6):
            if self._can_spawn_at_row(zombie_type, i):
                self.scene.spawn.row_random[i].b = 1.0
                sigma_b += 1.0
            else:
                self.scene.spawn.row_random[i].b = 0.0

        f = [0.0] * 6
        for i in range(6):
            if self.scene.spawn.row_random[i].b == 0:
                f[i] = 0.0
                continue

            weight = self.scene.spawn.row_random[i].b / sigma_b

            c = self.scene.spawn.row_random[i].c
            d = self.scene.spawn.row_random[i].d

            val = (6.0 * c * weight + 6.0 * weight - 3.0) / 4.0
            val += (d * weight + weight - 1.0) / 4.0

            f[i] = weight * min(max(val, 0.01), 100.0)

        row = self.rng.random_weighted_sample(f)

        for i in range(6):
            if self.scene.spawn.row_random[i].b > 0:
                self.scene.spawn.row_random[i].c += 1.0
                self.scene.spawn.row_random[i].d += 1.0

        self.scene.spawn.row_random[row].d = self.scene.spawn.row_random[row].c
        self.scene.spawn.row_random[row].c = 0.0

        return row
