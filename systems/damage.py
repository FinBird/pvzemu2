from pvzemu2.enums import (
    AttackFlags, ZombieStatus, ZombieType, ZombieAction,
    DamageFlags, ZombieAccessoriesType2,
    GridItemType, PlantType, PlantStatus, ZombieAccessoriesType1,
    ZombieReanimName, PlantReanimName
)
from pvzemu2.objects.base import ReanimateType
from pvzemu2.objects.plant import Plant
from pvzemu2.objects.zombie import Zombie
from pvzemu2.scene import Scene
from pvzemu2.systems import reanim
from pvzemu2.systems.griditem_factory import GridItemFactory
from pvzemu2.systems.plant_factory import PlantFactory
from pvzemu2.systems.rng import RNG
from pvzemu2.systems.util import get_col_by_x, get_row_by_x_and_y
from pvzemu2.systems.zombie_factory import ZombieFactory


class DebuffSystem:
    def __init__(self, scene: Scene) -> None:
        self.scene = scene

    def set_slowed(self, z: Zombie, countdown: int) -> None:
        if z.countdown.slow > 0:
            z.countdown.slow = max(z.countdown.slow, countdown)
            return

        z.countdown.slow = countdown
        self.update_fps(z)

    def set_butter(self, z: Zombie) -> None:
        if z.countdown.butter > 0:
            z.countdown.butter = 400
            return

        z.countdown.butter = 400
        self.update_fps(z)

    def remove_freeze(self, z: Zombie) -> None:
        if z.countdown.freeze > 0:
            z.countdown.freeze = 0
            self.update_fps(z)

    def remove_slow(self, z: Zombie) -> None:
        if z.countdown.slow > 0:
            z.countdown.slow = 0
            self.update_fps(z)

    def update_fps(self, z: Zombie) -> None:
        reanim.update_fps(z, self.scene)


class DamageSystem:
    def __init__(self, scene: Scene) -> None:
        self.scene = scene
        self.zombie_factory = ZombieFactory(scene)
        self.grid_item_factory = GridItemFactory(scene)
        self.plant_factory = PlantFactory(scene)
        self.rng = RNG(scene)
        self.debuff = DebuffSystem(self.scene)

    def can_be_attacked(self, z: Zombie, flags: int) -> bool:
        """对应 C++ damage::can_be_attacked"""
        if not (flags & AttackFlags.DYING_ZOMBIES) and (z.is_dead or self._has_death_status(z)):
            return False

        if flags & AttackFlags.HYPNO_ZOMBIES:
            if not z.is_hypno:
                return False
        elif z.is_hypno:
            return False

        if (z.type == ZombieType.BUNGEE and
                z.status != ZombieStatus.BUNGEE_IDLE_AFTER_DROP and
                z.status != ZombieStatus.BUNGEE_GRAB):
            return False

        if z.action == ZombieAction.FALL_FROM_SKY:
            return False

        is_animating = (
                z.status == ZombieStatus.POLE_VALUTING_JUMPING or
                z.status == ZombieStatus.IMP_FLYING or
                z.status == ZombieStatus.DIGGER_DRILL or
                z.status == ZombieStatus.DIGGER_LOST_DIG or
                z.status == ZombieStatus.DIGGER_LANDING or
                z.status == ZombieStatus.DOLPHIN_JUMP_IN_POOL or
                z.status == ZombieStatus.DOLPHIN_IN_JUMP or
                z.status == ZombieStatus.SNORKEL_JUMP_IN_THE_POOL or
                z.status == ZombieStatus.BALLOON_FALLING or
                z.status == ZombieStatus.RISING_FROM_GROUND or
                z.status == ZombieStatus.DANCING_DANCER_SPAWNING
        )

        if is_animating:
            return bool(flags & AttackFlags.ANIMATING_ZOMBIES)

        rect = z.get_hit_box_rect()
        if rect.x > 800:
            return False

        is_lurking_snorkel = (z.type == ZombieType.SNORKEL and not z.is_eating and z.is_in_water)

        if (flags & AttackFlags.LURKING_SNORKEL) and is_lurking_snorkel:
            return True

        if (flags & AttackFlags.DIGGING_DIGGER) and z.status == ZombieStatus.DIGGER_DIG:
            return True

        is_flying_or_falling = self._is_flying_or_falling(z)

        if (flags & AttackFlags.FLYING_BALLOON) and is_flying_or_falling:
            return True

        if (flags & AttackFlags.GROUND) and (
                not is_flying_or_falling and
                not is_lurking_snorkel and
                z.status != ZombieStatus.DIGGER_DIG
        ):
            return True

        return False

    def take(self, z: Zombie, damage: int, flags: int) -> None:
        """对应 C++ damage::take"""
        if self._has_death_status(z) or z.status == ZombieStatus.JACKBOX_POP or z.is_dead:
            return

        d = damage

        if flags & DamageFlags.BYPASSES_SHIELD:
            self.take_body(z, d, flags)
            return

        if z.status == ZombieStatus.BALLOON_FLYING or \
                (z.status == ZombieStatus.BALLOON_FALLING and z.type == ZombieType.BALLOON):

            if d >= 20:
                d -= 20

                if not (flags & DamageFlags.NO_LEAVE_BODY) and z.status == ZombieStatus.BALLOON_FLYING:
                    z.status = ZombieStatus.BALLOON_FALLING
                    # 模拟气球破裂动画
                    z.reanimate.type = ReanimateType.ONCE
                    z.reanimate.fps = 24.0  # 假设值
                    z.reanimate.n_repeated = 0

                if self.scene.type in (2, 3) and (z.row == 2 or z.row == 3):
                    # 水上直接死亡
                    self.zombie_factory.destroy(z)
                else:
                    z.action = ZombieAction.FALLING

        # 处理 Accessory 2 (门、梯子、报纸)
        if d > 0 and z.accessory_2_type != ZombieAccessoriesType2.NONE and not (flags & DamageFlags.BYPASSES_SHIELD):
            taken = min(z.accessory_2_hp, d)
            if not (flags & DamageFlags.DAMAGE_HITS_SHIELD_AND_BODY):
                d -= taken

            z.accessory_2_hp -= taken

            if z.accessory_2_hp == 0:
                self.destroy_accessory_2(z)

        # 处理 Accessory 1 (桶、路障、橄榄球帽、矿工帽)
        # 注意: 假设 Zombie 类有 accessory_1_type 和 accessory_1_hp 字段
        # 如果 flags 没有忽略 Accessory 1 (通常普通攻击都打帽子)
        if d > 0 and hasattr(z, 'accessory_1_type') and z.accessory_1_type != ZombieAccessoriesType1.NONE:
            # 大部分普通伤害会先打帽子，除非特殊指定(如磁力菇直接移除，但那是逻辑处理不是伤害)
            # C++中并没有 IGNORE_ACCESSORY_1 这个flag，通常直接扣除
            taken = min(z.accessory_1_hp, d)
            # 帽子通常吸收所有伤害，直到损坏
            d -= taken
            z.accessory_1_hp -= taken

            if z.accessory_1_hp <= 0:
                self.destroy_accessory_1(z)

        if d > 0:
            self.take_body(z, d, flags)

    def destroy_accessory_1(self, z: Zombie) -> None:
        z.accessory_1_type = ZombieAccessoriesType1.NONE
        z.accessory_1_hp = 0

    def take_body(self, z: Zombie, damage: int, flags: int) -> None:
        if flags & DamageFlags.DAMAGE_FREEZE:
            self.debuff.set_slowed(z, 1000)

        z.hp -= damage

        if z.type == ZombieType.ZOMBONI:
            if flags & DamageFlags.SPIKE:
                # 冰车被地刺扎爆轮胎
                z.status = ZombieStatus.DYING
                z.dx = 0.0
                z.countdown.action = 280  # 模拟死亡动画时长
                # 模拟随机播放两种爆胎动画之一
                if self.rng.randint(4) == 0 or z.x >= 600:
                    z.reanimate.type = ReanimateType.ONCE
                    z.reanimate.fps = 12.0
                else:
                    z.reanimate.type = ReanimateType.ONCE
                    z.reanimate.fps = 10.0
            elif z.hp < 0:
                self.zombie_factory.destroy(z)

        elif z.type == ZombieType.CATAPULT:
            if flags & DamageFlags.SPIKE:
                # 投石车被地刺攻击
                z.status = ZombieStatus.DYING
                z.dx = 0.0
                z.countdown.action = 280
                z.reanimate.type = ReanimateType.ONCE
                z.reanimate.fps = 12.0
            elif z.hp < 0:
                self.zombie_factory.destroy(z)

        if z.hp <= 0:
            z.hp = 0
            self.set_death_state(z, flags)

    def set_death_state(self, z: Zombie, flags: int) -> None:
        if self._has_death_status(z):
            return

        if not z.has_reanim(ZombieReanimName.anim_death):
            self.zombie_factory.destroy(z)
            return

        z.countdown.freeze = 0
        z.countdown.butter = 0
        z.has_eaten_garlic = False
        z.time_since_ate_garlic = 0

        if (flags & DamageFlags.NO_LEAVE_BODY) and z.type not in (ZombieType.GARGANTUAR, ZombieType.GIGA_GARGANTUAR):
            self.zombie_factory.destroy(z)
            return

        if z.type == ZombieType.POGO:
            z.dy = 0.0

        self.unset_is_eating(z)

        if z.accessory_2_type != ZombieAccessoriesType2.NONE:
            self.destroy_accessory_2(z)

        z.dx = 0.0
        z.status = ZombieStatus.DYING

        if z.action == ZombieAction.CLIMBING_LADDER:
            z.action = ZombieAction.FALLING

        fps = 0.0
        if z.type == ZombieType.FOOTBALL:
            fps = 24.0
        elif z.type in (ZombieType.GARGANTUAR, ZombieType.GIGA_GARGANTUAR, ZombieType.SNORKEL, ZombieType.YETI):
            fps = 14.0
        elif z.type == ZombieType.DIGGER:
            fps = 18.0
        else:
            fps = self.rng.randfloat(24.0, 30.0)

        anim_name = ZombieReanimName.anim_death

        if z.is_in_water and z.has_reanim(ZombieReanimName.anim_waterdeath):
            anim_name = ZombieReanimName.anim_waterdeath
        elif self.rng.randint(10) == 0 and z.has_reanim(ZombieReanimName.anim_death2):
            anim_name = ZombieReanimName.anim_death2
        elif self.rng.randint(10) == 0 and z.has_reanim(ZombieReanimName.anim_superlongdeath):
            anim_name = ZombieReanimName.anim_superlongdeath

        z.set_reanim_frame(anim_name)
        z.reanimate.type = ReanimateType.ONCE
        z.reanimate.n_repeated = 0

        if z.reanimate:
            z.reanimate.fps = fps

        # We set a default countdown since reanim completion isn't fully hooked up to destroy zombie in python version yet
        z.countdown.dead = 100

    def set_is_eating(self, z: Zombie) -> None:
        if z.is_eating:
            return

        z.is_eating = True

        if z.status == ZombieStatus.DIGGER_DIG:
            return

        anim_name = ZombieReanimName.anim_eat
        if z.status == ZombieStatus.LADDER_WALKING:
            anim_name = ZombieReanimName.anim_laddereat
        elif z.status == ZombieStatus.NEWSPAPER_RUNNING:
            anim_name = ZombieReanimName.anim_eat_nopaper
        elif z.status == ZombieStatus.POLE_VALUTING_RUNNING:
            return

        z.set_reanim_frame(anim_name)
        z.reanimate.type = ReanimateType.REPEAT
        z.reanimate.n_repeated = 0

    def unset_is_eating(self, z: Zombie) -> None:
        if z.is_eating:
            z.is_eating = False

            if z.status != ZombieStatus.DIGGER_DIG:
                if z.type != ZombieType.SNORKEL:
                    anim_name = ZombieReanimName.anim_walk
                    if z.status == ZombieStatus.LADDER_WALKING:
                        anim_name = ZombieReanimName.anim_ladderwalk
                    elif z.status == ZombieStatus.NEWSPAPER_RUNNING:
                        anim_name = ZombieReanimName.anim_walk_nopaper
                    elif z.is_in_water and z.has_reanim(ZombieReanimName.anim_swim):
                        anim_name = ZombieReanimName.anim_swim
                    elif z.type == ZombieType.POLE_VAULTING and z.status == ZombieStatus.POLE_VALUTING_RUNNING:
                        anim_name = ZombieReanimName.anim_run

                    z.set_reanim_frame(anim_name)
                    z.reanimate.type = ReanimateType.REPEAT
                    z.reanimate.n_repeated = 0

                self.debuff.update_fps(z)

    def destroy_accessory_2(self, z: Zombie) -> None:
        if z.accessory_2_type == ZombieAccessoriesType2.NONE:
            return

        z.accessory_2_hp = 0

        if z.accessory_2_type == ZombieAccessoriesType2.NEWSPAPER:
            self.unset_is_eating(z)

            if z.has_eaten_garlic:
                z.has_eaten_garlic = False
                z.time_since_ate_garlic = 0

            z.status = ZombieStatus.NEWSPAPER_DESTROYED
            z.set_reanim_frame(ZombieReanimName.anim_gasp)
            z.reanimate.type = ReanimateType.ONCE
            z.reanimate.fps = 8.0  # Override FPS for this animation
            z.reanimate.n_repeated = 0

        elif z.accessory_2_type == ZombieAccessoriesType2.LADDER:
            z.status = ZombieStatus.WALKING
            if z.is_eating:
                z.set_reanim_frame(ZombieReanimName.anim_eat)
                z.reanimate.type = ReanimateType.REPEAT
                z.reanimate.n_repeated = 0
            else:
                z.set_reanim_frame(ZombieReanimName.anim_walk)
                z.reanimate.type = ReanimateType.REPEAT
                z.reanimate.n_repeated = 0

        z.accessory_2_type = ZombieAccessoriesType2.NONE

    def take_instant_kill(self, row: int, x: int, y: int, radius: int, grid_radius: int, is_ash_attack: bool,
                          flags: int) -> None:
        # Spatial optimization: iterate only relevant rows
        start_row = max(0, row - grid_radius)
        end_row = min(len(self.scene.zombies_by_row), row + grid_radius + 1)
        # print(f"[Debug] Explosion at Row:{row}, X:{x}, Y:{y}, Radius:{radius}")
        candidates = []
        for r in range(start_row, end_row):
            candidates.extend(self.scene.zombies_by_row[r])

        # Collect zombies to process first to avoid modification during iteration issues if we were iterating scene.zombies directly,
        # but here we iterate over a list of IDs, so it's safeish, but looking up object and destroying might affect zombies_by_row if we are not careful?
        # Actually, self.scene.zombies.get(id) is safe. Destroying removes from zombies_by_row.
        # Since we collected IDs into 'candidates' list (copy), iterating candidates is safe.

        for z_id in candidates:
            z = self.scene.zombies.get(z_id)
            if z is None:
                continue

            if not self.can_be_attacked(z, flags):
                # print(f"  [Zombie {z.id}] Skipped: cannot be attacked (Status:{z.status.name})")
                continue

            rect = z.get_hit_box_rect()
            # dist_check = rect.is_overlap_with_circle(x, y, radius)
            # row_check = abs(z.row - row) <= grid_radius

            # print(f"  [Zombie {z.id}] RowCheck:{row_check}, DistCheck:{dist_check}, Rect:{rect}")

            # Double check row diff in case grid_radius logic needs it (it's already handled by loop range, but keeping check is fine or remove it)
            if abs(z.row - row) <= grid_radius and rect.is_overlap_with_circle(x, y, radius):
                if is_ash_attack:
                    self.take_ash_attack(z)
                else:
                    self.take(z, 1800, DamageFlags.NO_LEAVE_BODY | DamageFlags.DAMAGE_HITS_SHIELD_AND_BODY)

        col = max(0, get_col_by_x(x))
        source_row = max(0, get_row_by_x_and_y(self.scene.type, max(40, x), y))

        for item in self.scene.grid_items:
            if item.type == GridItemType.LADDER:
                if abs(item.col - col) <= grid_radius and abs(item.row - source_row) <= grid_radius:
                    self.grid_item_factory.destroy(item)

    def take_ash_attack(self, z: Zombie) -> None:
        if z.status == ZombieStatus.DYING_FROM_INSTANT_KILL:
            return

        # 1. HP 判定：血量极高的僵尸（如巨人）仅扣除灰烬伤害数值
        if z.hp >= 1800:
            self.take(z, 1800, DamageFlags.NO_LEAVE_BODY | DamageFlags.DAMAGE_HITS_SHIELD_AND_BODY)
            return

        # 2. HP 低于 1800：强制归零并移除负面状态
        z.hp = 0

        if z.countdown.freeze > 0:
            self.debuff.remove_freeze(z)

        if z.countdown.butter > 0:
            z.countdown.butter = 0
            self.debuff.update_fps(z)

        # 3. 灰烬化动画触发判定
        # 逻辑：只有当僵尸处于“标准地面状态”（非死亡、非跳跃、非入水等）时，
        # 特定类型的僵尸才会留下“黑灰”尸体并存在一段时间（300帧）。
        is_standard_ground = not (
                z.status == ZombieStatus.DYING or
                z.status == ZombieStatus.DYING_FROM_LAWNMOWER or
                z.status == ZombieStatus.POLE_VALUTING_JUMPING or
                z.status == ZombieStatus.IMP_FLYING or
                z.status == ZombieStatus.RISING_FROM_GROUND or
                z.status == ZombieStatus.DANCING_DANCER_SPAWNING or
                z.status == ZombieStatus.DOLPHIN_JUMP_IN_POOL or
                z.status == ZombieStatus.DOLPHIN_IN_JUMP or
                z.status == ZombieStatus.DOLPHIN_RIDE or
                z.status == ZombieStatus.SNORKEL_JUMP_IN_THE_POOL or
                z.status == ZombieStatus.DIGGER_DIG or
                z.status == ZombieStatus.DIGGER_LOST_DIG or
                z.status == ZombieStatus.DIGGER_DRILL or
                z.status == ZombieStatus.DIGGER_LANDING or
                z.is_in_water
        )

        if is_standard_ground:
            if z.type in (ZombieType.BUNGEE, ZombieType.YETI) or \
                    z.is_flying_or_falling() or \
                    not z.is_not_dying:

                if z.reanimate:
                    z.reanimate.prev_fps = 0.0
                    z.reanimate.fps = 0.0

                z.status = ZombieStatus.DYING_FROM_INSTANT_KILL
                z.countdown.action = 300
                return

        self.zombie_factory.destroy(z)

    def check_collision(self, plant: Plant, zombie: Zombie) -> bool:
        """简单的植物-僵尸碰撞检测"""
        p_rect = plant.get_hit_box()
        z_rect = zombie.get_hit_box_rect()
        return p_rect.get_overlap_len(z_rect) > 0

    def activate_plant(self, p: Plant) -> None:
        flags = self._get_plant_attack_flags(p)

        x = p.attack_box.width // 2 + p.x
        y = p.attack_box.height // 2 + p.y

        if p.type == PlantType.BLOVER:
            if p.status != PlantStatus.WORK:
                p.status = PlantStatus.WORK
                self.activate_blover()

        elif p.type == PlantType.CHERRY_BOMB:
            self.take_instant_kill(p.row, x, y, 115, 1, True, flags)
            self.plant_factory.destroy(p)

        elif p.type == PlantType.DOOMSHROOM:
            self.take_instant_kill(p.row, x, y, 250, 3, True, flags)

            to_destroy = []
            for other in self.scene.plants:
                if other.row == p.row and other.col == p.col:
                    to_destroy.append(other)
            for other in to_destroy:
                self.plant_factory.destroy(other)

            self.grid_item_factory.create(GridItemType.CRATER, p.row, p.col)

        elif p.type == PlantType.JALAPENO:
            # Spatial optimization: only current row
            candidates = []
            if 0 <= p.row < len(self.scene.zombies_by_row):
                candidates = list(self.scene.zombies_by_row[p.row])

            for z_id in candidates:
                z = self.scene.zombies.get(z_id)
                if z is None: continue

                if not self.can_be_attacked(z, flags):
                    continue

                self.debuff.remove_freeze(z)

                if z.countdown.slow > 0:
                    self.debuff.remove_slow(z)

                self.take_ash_attack(z)

            for item in self.scene.grid_items:
                if item.row == p.row and item.type == GridItemType.LADDER:
                    self.grid_item_factory.destroy(item)

            self.plant_factory.destroy(p)

        elif p.type == PlantType.UMBRELLA_LEAF:
            if p.status not in (PlantStatus.UMBRELLA_LEAF_BLOCK, PlantStatus.UMBRELLA_LEAF_SHRINK):
                p.status = PlantStatus.UMBRELLA_LEAF_BLOCK
                p.countdown.status = 5

                p.set_reanim_frame(PlantReanimName.anim_block)
                p.reanimate.type = ReanimateType.ONCE
                p.reanimate.fps = 22.0
                p.reanimate.n_repeated = 0

        elif p.type == PlantType.ICESHROOM:
            # Global effect, iterate all zombies (safe copy)
            for z in list(self.scene.zombies):
                has_freezed_or_slowed = z.countdown.slow > 0 or z.countdown.freeze > 0

                self.debuff.set_slowed(z, 2000)

                if self._can_be_freezed(z):
                    if z.is_in_water:
                        z.countdown.freeze = 300
                    elif has_freezed_or_slowed:
                        z.countdown.freeze = self.rng.randint(101) + 300
                    else:
                        z.countdown.freeze = self.rng.randint(201) + 400

                    self.take(z, 20, DamageFlags.BYPASSES_SHIELD)
                    self.debuff.update_fps(z)

            self.scene.spawn.countdown_pool = 300
            self.plant_factory.destroy(p)

        elif p.type == PlantType.POTATO_MINE:
            self.take_instant_kill(p.row, x, y, 60, 0, False, flags)
            self.plant_factory.destroy(p)

        elif p.type == PlantType.COFFEE_BEAN:
            target = None
            for other in self.scene.plants:
                if other.row == p.row and other.col == p.col and other != p:
                    if other.is_sleeping:
                        target = other
                        break

            if target:
                target.countdown.awake = 100

            p.status = PlantStatus.WORK

            p.set_reanim_frame(PlantReanimName.anim_crumble)
            p.reanimate.type = ReanimateType.ONCE
            p.reanimate.fps = 22.0
            p.reanimate.n_repeated = 0

            p.countdown.dead = 50  # Simulate animation duration

    def activate_blover(self) -> None:
        for z in self.scene.zombies:
            if not z.is_dead and z.status == ZombieStatus.BALLOON_FLYING:
                z.is_blown = True

    def set_smashed(self, p: Plant) -> None:
        if self._is_squash_attacking(p) or p.is_dead or p.is_smashed:
            return

        if p.is_sleeping or \
                p.type not in (PlantType.CHERRY_BOMB, PlantType.JALAPENO, PlantType.DOOMSHROOM,
                               PlantType.ICESHROOM) and \
                (p.type != PlantType.POTATO_MINE or p.status == PlantStatus.IDLE):

            if p.type != PlantType.SQUASH or p.status == PlantStatus.IDLE:
                p.is_smashed = True
                p.countdown.dead = 500

                for item in self.scene.grid_items:
                    if item.col == p.col and item.row == p.row and item.type == GridItemType.LADDER:
                        self.grid_item_factory.destroy(item)
                        break
        else:
            self.activate_plant(p)

    def range_attack(self, p: Plant, flags: int) -> None:
        pr_abs = p.get_attack_box()
        plant_flags = self._get_plant_attack_flags(p, False)

        start_row = max(0, p.row - 1)
        end_row = min(len(self.scene.zombies_by_row), p.row + 2)

        candidates = []
        for r in range(start_row, end_row):
            candidates.extend(self.scene.zombies_by_row[r])

        for z_id in candidates:
            z = self.scene.zombies.get(z_id)
            if z is None: continue

            diff = abs(z.row - p.row)
            if (p.type != PlantType.GLOOMSHROOM and diff != 0):
                continue

            if not self.can_be_attacked(z, plant_flags):
                continue

            zr = z.get_hit_box_rect()

            if pr_abs.get_overlap_len(zr) >= 0:
                d = 20
                if (z.type in (ZombieType.ZOMBONI, ZombieType.CATAPULT)) and (flags & DamageFlags.SPIKE):
                    d = 1800
                    if p.type == PlantType.SPIKEROCK:
                        # TODO: spikerock.reduce_life(p)
                        if p.status != PlantStatus.SPIKE_ATTACK:
                            p.status = PlantStatus.SPIKE_ATTACK
                            p.countdown.status = 100

                        p.hp -= 50
                        if p.hp <= 0:
                            self.plant_factory.destroy(p)
                    else:
                        self.plant_factory.destroy(p)

                self.take(z, d, flags)

    def _has_death_status(self, z: Zombie) -> bool:
        return z.status in (ZombieStatus.DYING,
                            ZombieStatus.DYING_FROM_INSTANT_KILL,
                            ZombieStatus.DYING_FROM_LAWNMOWER)

    def _is_flying_or_falling(self, z: Zombie) -> bool:
        return z.type == ZombieType.BALLOON and z.status in (ZombieStatus.BALLOON_FLYING, ZombieStatus.BALLOON_FALLING)

    def _can_be_freezed(self, z: Zombie) -> bool:
        if z.type in (ZombieType.ZOMBONI, ZombieType.CATAPULT, ZombieType.BUNGEE) or \
                self._is_flying_or_falling(z) or \
                z.status in (ZombieStatus.POLE_VALUTING_JUMPING, ZombieStatus.DOLPHIN_JUMP_IN_POOL,
                             ZombieStatus.DOLPHIN_IN_JUMP, ZombieStatus.DOLPHIN_RIDE,
                             ZombieStatus.SNORKEL_JUMP_IN_THE_POOL):
            return False
        return True

    def _get_plant_attack_flags(self, p: Plant, is_range_attack: bool = True) -> int:
        flags = 0
        if p.type in (PlantType.CHERRY_BOMB, PlantType.JALAPENO, PlantType.DOOMSHROOM,
                      PlantType.POTATO_MINE, PlantType.SQUASH, PlantType.TANGLE_KELP,
                      PlantType.COB_CANNON):
            flags |= AttackFlags.DYING_ZOMBIES | AttackFlags.GROUND | AttackFlags.DIGGING_DIGGER | \
                     AttackFlags.LURKING_SNORKEL | AttackFlags.ANIMATING_ZOMBIES

            if p.type in (PlantType.CHERRY_BOMB, PlantType.JALAPENO, PlantType.DOOMSHROOM, PlantType.COB_CANNON):
                flags |= AttackFlags.FLYING_BALLOON

        elif p.type in (PlantType.CABBAGEPULT, PlantType.KERNELPULT, PlantType.MELONPULT,
                        PlantType.WINTER_MELON, PlantType.CATTAIL):
            flags |= AttackFlags.GROUND | AttackFlags.LURKING_SNORKEL | AttackFlags.ANIMATING_ZOMBIES
            if p.type == PlantType.CATTAIL:
                flags |= AttackFlags.FLYING_BALLOON

        elif p.type == PlantType.SPIKEWEED or p.type == PlantType.SPIKEROCK:
            flags |= AttackFlags.GROUND | AttackFlags.DIGGING_DIGGER | AttackFlags.ANIMATING_ZOMBIES

        elif p.type == PlantType.CACTUS or p.type == PlantType.BLOVER:
            flags |= AttackFlags.FLYING_BALLOON | AttackFlags.GROUND | AttackFlags.ANIMATING_ZOMBIES

        elif p.type == PlantType.STARFRUIT or p.type == PlantType.THREEPEATER:
            flags |= AttackFlags.GROUND | AttackFlags.ANIMATING_ZOMBIES

        elif p.type == PlantType.ICESHROOM:
            flags |= AttackFlags.GROUND | AttackFlags.LURKING_SNORKEL | AttackFlags.ANIMATING_ZOMBIES | \
                     AttackFlags.FLYING_BALLOON | AttackFlags.DIGGING_DIGGER

        else:
            flags |= AttackFlags.GROUND | AttackFlags.ANIMATING_ZOMBIES

        return flags

    def _is_squash_attacking(self, p: Plant) -> bool:
        return p.type == PlantType.SQUASH and p.status != PlantStatus.IDLE
