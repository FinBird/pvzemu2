from typing import Optional

from pvzemu2.enums import (
    ZombieStatus, ZombieType, ZombieAction,
    DamageFlags, PlantType, PlantStatus, SceneType, GridItemType, ZombieReanimName,
)
from pvzemu2.geometry import Rect
from pvzemu2.objects.plant import Plant
from pvzemu2.objects.zombie import Zombie
from pvzemu2.scene import Scene
from pvzemu2.systems import reanim
from pvzemu2.systems.damage import DamageSystem
from pvzemu2.systems.griditem_factory import GridItemFactory
from pvzemu2.systems.plant_factory import PlantFactory
from pvzemu2.systems.rng import RNG
from pvzemu2.systems.util import get_col_by_x, zombie_init_y, is_slowed, is_not_movable
from pvzemu2.systems.zombie_factory import ZombieFactory


class ZombieSystem:
    def __init__(self, scene: Scene, damage_system: DamageSystem, plant_factory: PlantFactory) -> None:
        self.scene = scene
        self.damage_system = damage_system
        self.zombie_factory = ZombieFactory(scene)
        self.plant_factory = plant_factory
        self.grid_item_factory = GridItemFactory(scene)
        self.rng = RNG(scene)

    def update(self) -> bool:
        """对应 C++ zombie_system::update"""
        # 使用 list(self.scene.zombies) 创建副本，确保在遍历过程中删除对象是安全的
        for z in list(self.scene.zombies):
            z.time_since_spawn += 1

            if z.status == ZombieStatus.DYING_FROM_INSTANT_KILL:
                z.countdown.action -= 1
                if z.countdown.action == 1:
                    self.zombie_factory.destroy(z)
                continue

            elif z.status == ZombieStatus.DYING_FROM_LAWNMOWER:
                z.countdown.butter = 0
                z.is_not_dying = False

                if z.type == ZombieType.FLAG:
                    z.has_item_or_walk_left = False

                self.zombie_factory.destroy(z)
                continue

            elif z.status == ZombieStatus.DYING:
                self._update_dead_from_plant(z)
                self._update_x(z)

            # Normal update flow
            if z.countdown.action > 0 and z.countdown.freeze == 0 and z.countdown.butter == 0:
                z.countdown.action -= 1

            # 核心更新：当倒计时归零时，调用全局 reanim 模块重新计算并恢复真实的 FPS
            if z.countdown.freeze > 0:
                z.countdown.freeze -= 1
                if z.countdown.freeze == 0:
                    reanim.update_fps(z, self.scene)

            if z.countdown.slow > 0:
                z.countdown.slow -= 1
                if z.countdown.slow == 0:
                    reanim.update_fps(z, self.scene)

            if z.countdown.butter > 0:
                z.countdown.butter -= 1
                if z.countdown.butter == 0:
                    reanim.update_fps(z, self.scene)

            if z.status == ZombieStatus.RISING_FROM_GROUND:
                self._update_lurking_dy(z)
                continue

            # Normal update flow
            if z.countdown.action > 0 and z.countdown.freeze == 0 and z.countdown.butter == 0:
                z.countdown.action -= 1

            if z.countdown.freeze > 0:
                z.countdown.freeze -= 1
                if z.countdown.freeze == 0:
                    self.damage_system.debuff.update_fps(z)

            if z.countdown.slow > 0:
                z.countdown.slow -= 1
                if z.countdown.slow == 0:
                    self.damage_system.debuff.update_fps(z)

            if z.countdown.butter > 0:
                z.countdown.butter -= 1
                if z.countdown.butter == 0:
                    self.damage_system.debuff.update_fps(z)

            if z.status == ZombieStatus.RISING_FROM_GROUND:
                self._update_lurking_dy(z)
                continue

            if z.countdown.freeze <= 0 and z.countdown.butter <= 0:
                self._update_status(z)
                self._update_pos(z)
                self._update_eating(z)
                self._update_water_status(z)

                if self._update_entering_home(z):
                    return True  # Game Over

            self._update_near_death(z)

            # Subsystems update (simplified placeholders)
            # TODO: Implement specific zombie subsystems (Bungee, Ladder, etc.)
            # if z.type == ZombieType.BUNGEE: subsystems.bungee.update(z)

            self._update_garlic_and_hypno_effect(z)

            if z.countdown.dead > 0:
                z.countdown.dead -= 1
                if z.countdown.dead == 0:
                    self.zombie_factory.destroy(z)

            # Update integer coordinates
            z.int_x = int(z.x)
            z.int_y = int(z.y)

            reanim.update_progress(z.reanimate)

        return False

    def _update_dead_from_plant(self, z: Zombie) -> None:
        if z.action == ZombieAction.FALLING:
            self._update_falling(z)

        if (z.type == ZombieType.ZOMBONI and z.countdown.action > 0) or z.type == ZombieType.CATAPULT:
            z.countdown.action -= 1
            if z.countdown.action == 0:
                self.zombie_factory.destroy(z)
            return

        if z.countdown.dead == -1:  # and z.reanimate.n_repeated > 0
            # Simplify: assume animation finished if needed, or just use a timer
            z.countdown.dead = 10 if z.is_in_water else 100

    def _update_x(self, z: Zombie) -> None:
        if is_not_movable(self.scene, z):
            return

        if (ZombieStatus.POGO_WITH_STICK <= z.status <= ZombieStatus.POGO_JUMP_ACROSS) or \
                z.status in (ZombieStatus.DOLPHIN_RIDE, ZombieStatus.BALLOON_FLYING, ZombieStatus.SNORKEL_SWIM) or \
                z.type == ZombieType.CATAPULT:
            dx = z.dx * 0.4000000059604645 if is_slowed(self.scene, z) else z.dx
        elif z.type == ZombieType.ZOMBONI or \
                z.status in (ZombieStatus.DIGGER_DIG, ZombieStatus.DOLPHIN_IN_JUMP,
                             ZombieStatus.POLE_VALUTING_JUMPING, ZombieStatus.SNORKEL_JUMP_IN_THE_POOL):
            dx = z.dx
        elif z._ground is not None and z.has_reanim(ZombieReanimName._ground):
            # 核心修正：增加 z._ground is not None 的判定。
            # 如果测试中手动禁用了 _ground，系统会自动回退到使用线性速度 (z.dx)
            dx = z.get_dx_from_ground()
        else:
            dx = z.dx * 0.4000000059604645 if is_slowed(self.scene, z) else z.dx

        if self._is_walk_right(z) or z.status == ZombieStatus.DANCING_MOONWALK:
            z.x += dx
        else:
            z.x -= dx

    def _is_slowed(self, z: Zombie) -> bool:
        return z.countdown.slow > 0 or z.countdown.freeze > 0

    def _is_walk_right(self, z: Zombie) -> bool:
        return z.is_hypno  # Simplified: hypno zombies walk right

    def _update_lurking_dy(self, z: Zombie) -> None:
        ratio = (50.0 - z.countdown.action) / 50.0

        if ratio <= 0:
            dy = -150.0 if z.is_in_water else -200.0
        elif ratio > 1:
            dy = -40.0 if z.is_in_water else 0.0
        else:
            if z.is_in_water:
                dy = 110.0 * ratio - 150.0
            else:
                dy = 200.0 * ratio - 200.0

        z.dy = round(dy)

        if z.countdown.action == 0:
            z.status = ZombieStatus.WALKING

    def _update_status(self, z: Zombie) -> None:
        if z.action == ZombieAction.CLIMBING_LADDER:
            self._update_climb_ladder(z)

        if z.action in (ZombieAction.LEAVING_POOL, ZombieAction.ENTERING_POOL) or z.is_in_water:
            self._update_action_in_pool(z)

        if z.action == ZombieAction.FALLING:
            self._update_falling(z)

        # TODO: Call subsystems based on type

    def _update_pos(self, z: Zombie) -> None:
        if z.type == ZombieType.BUNGEE or z.status == ZombieStatus.RISING_FROM_GROUND:
            return

        self._update_x(z)

        if z.type in (ZombieType.ZOMBONI, ZombieType.CATAPULT, ZombieType.GARGANTUAR, ZombieType.GIGA_GARGANTUAR):
            self._crush_plant(z)

        prev_x = z.x

        if z.is_blown:
            z.x += 10

        if not z.is_blown or prev_x <= 850:
            if z.action == ZombieAction.NONE:
                init_y = zombie_init_y(self.scene.type, z, z.row)

                if z.y > init_y:
                    if z.y - init_y <= 1:
                        z.y = init_y
                    else:
                        z.y -= 1
                elif z.y < init_y:
                    if init_y - z.y <= 1:
                        z.y = init_y
                    else:
                        z.y += 1
        else:
            self.zombie_factory.destroy(z)

    def _update_eating(self, z: Zombie) -> None:
        # Simplified exclusions check
        if z.type in (ZombieType.BUNGEE, ZombieType.GARGANTUAR, ZombieType.GIGA_GARGANTUAR,
                      ZombieType.ZOMBONI, ZombieType.CATAPULT) or \
                z.status in (ZombieStatus.POLE_VALUTING_JUMPING, ZombieStatus.BALLOON_FLYING) or \
                z.action in (ZombieAction.FALL_FROM_SKY, ZombieAction.CLIMBING_LADDER,
                             ZombieAction.ENTERING_POOL, ZombieAction.LEAVING_POOL, ZombieAction.FALLING) or \
                not z.is_not_dying:
            return

        # 1. 优先检查魅惑僵尸互打
        enemy = self._find_hypno_enemy(z)
        if enemy:
            z.is_eating = True
            enemy.is_eating = True  # 强制让对手也进入吃状态，从而停止移动

            op = 8 if z.countdown.slow > 0 else 4
            if z.time_since_spawn % op == 0:
                # 给对方造成伤害
                self.damage_system.take(enemy, 4, DamageFlags.NO_FLASH | DamageFlags.BYPASSES_SHIELD)
            return  # 正在打架，不寻找植物

        # 2. 如果没在打架，检查是否在吃植物
        # ... 原有的寻找植物逻辑 ...
        target = self._find_target(z)
        if z.is_hypno or target is None:
            z.is_eating = False
        else:
            self._update_eating_plants(z, target)

    def _find_hypno_enemy(self, z: Zombie) -> Optional[Zombie]:
        if z.status == ZombieStatus.DIGGER_DIG:
            return None

        zr = z.get_attack_box_rect()  # 攻击方用攻击框

        if 0 <= z.row < len(self.scene.zombies_by_row):
            for enemy_id in list(self.scene.zombies_by_row[z.row]):
                enemy = self.scene.zombies.get(enemy_id)

                if enemy is None or enemy is z:
                    continue

                # 必须是一个魅惑，一个非魅惑
                if z.is_hypno == enemy.is_hypno:
                    continue

                # 排除无法互相攻击的状态
                if enemy.status in (ZombieStatus.BALLOON_FLYING, ZombieStatus.BALLOON_FALLING,
                                    ZombieStatus.DIGGER_DIG) or \
                        enemy.is_dead or not enemy.is_not_dying:
                    continue

                # 被打方用受击框
                er = enemy.get_hit_box_rect()
                d = zr.get_overlap_len(er)

                # 判定重叠，放宽到 10 像素以增加稳定性，或者只要有重叠且对方正在吃
                if d >= 10 or (d >= 0 and enemy.is_eating):
                    return enemy

        return None

    def _find_target(self, z: Zombie) -> Optional[Plant]:
        # Simple find target plant
        z_attack_box = Rect(
            z.int_x + z.attack_box_x,
            z.int_y + z.attack_box_y,
            z.attack_box_width,
            z.attack_box_height
        )

        for p in self.scene.plants:
            if p.row != z.row or p.is_dead:
                continue

            # Check edible status
            if p.edible == 2:  # INVISIBLE_AND_NOT_EDIBLE
                continue

            p_rect = p.get_hit_box()
            # 必须达到至少 20 像素的重叠才算咬到
            if z_attack_box.get_overlap_len(p_rect) >= 20:
                # 地刺系列不作为啃食目标
                if p.type in (PlantType.SPIKEWEED, PlantType.SPIKEROCK):
                    continue
                return p
        return None

    def _update_eating_plants(self, z: Zombie, p: Plant) -> None:
        if z.status == ZombieStatus.DANCING_MOONWALK:
            z.countdown.action = 1
            return

        if z.has_eaten_garlic:
            return

        # 梯子逻辑：遇到梯子时停止啃食并开始攀爬
        if z.type != ZombieType.DIGGER:
            for item in self.scene.grid_items:
                if item.row == p.row and item.col == p.col and item.type == GridItemType.LADDER:
                    z.is_eating = False
                    if z.action == ZombieAction.NONE and z.ladder_col != p.col:
                        z.action = ZombieAction.CLIMBING_LADDER
                        z.ladder_col = p.col
                    return

        z.is_eating = True

        # 攻击频率控制：根据减速状态决定伤害间隔
        op = 8 if z.countdown.slow > 0 else 4
        if z.time_since_spawn % op != 0:
            return

        # =========================================================
        # 1. 魅惑蘑菇触发逻辑 (仅在植物清醒时触发)
        # =========================================================
        if p.type == PlantType.HYPNOSHROOM and not p.is_sleeping:
            immune_types = (ZombieType.GARGANTUAR, ZombieType.GIGA_GARGANTUAR,
                            ZombieType.ZOMBONI, ZombieType.CATAPULT, ZombieType.BUNGEE,
                            ZombieType.ZOMBIE_BOSS)

            if z.type not in immune_types:
                # 销毁蘑菇
                p.hp = 0
                p.is_dead = True
                self.plant_factory.destroy(p)

                # 应用魅惑效果
                z.is_hypno = True
                z.is_eating = False
                z.dx = 0.17
                z.reanimate.fps = 8.0
                z.reanimate.prev_fps = 8.0

                # 解除舞王/伴舞的绑定关系
                if z.type == ZombieType.DANCING:
                    for partner_id in z.partners:
                        if partner_id != -1:
                            partner = self.scene.zombies.get(partner_id)
                            if partner:
                                partner.master_id = None
                    z.partners = [-1, -1, -1, -1]
                elif z.type == ZombieType.BACKUP_DANCER:
                    if z.master_id is not None:
                        master = self.scene.zombies.get(z.master_id)
                        if master:
                            for i in range(4):
                                if master.partners[i] == z.id:
                                    master.partners[i] = -1
                                    break
                    z.master_id = None

                # 触发魅惑后直接返回，不执行后续伤害
                return

        # =========================================================
        # 2. 状态判定 (跳过不可被啃食的状态)
        # =========================================================

        # 倭瓜跳起攻击时无敌
        if p.status in (PlantStatus.SQUASH_JUMP_UP, PlantStatus.SQUASH_STOP_IN_THE_AIR,
                        PlantStatus.SQUASH_JUMP_DOWN, PlantStatus.SQUASH_CRUSHED,
                        PlantStatus.FLOWER_POT_PLACED, PlantStatus.LILY_PAD_PLACED):
            return

        # 土豆雷只有在未出土(IDLE)状态下才会被吃
        if p.type == PlantType.POTATO_MINE and p.status != PlantStatus.IDLE:
            return

        # =========================================================
        # 3. 通用扣血逻辑 (移除之前的 not p.is_sleeping 判断)
        # =========================================================

        # 如果是清醒的灰烬植物（樱桃、辣椒等），尝试激活它们
        if not p.is_sleeping and p.type in (PlantType.CHERRY_BOMB, PlantType.JALAPENO,
                                            PlantType.DOOMSHROOM, PlantType.ICESHROOM):
            self.damage_system.activate_plant(p)
            # 如果已经进入 WORK 状态（即将爆炸），不再扣血
            if p.status == PlantStatus.WORK:
                return

        # 执行扣血：睡眠的植物也会走到这里被吃掉
        p.hp -= 4
        p.countdown.eaten = 50
        if p.hp <= 0:
            p.is_dead = True
            self.plant_factory.destroy(p)

    def _update_water_status(self, z: Zombie) -> None:
        if z.type not in (ZombieType.ZOMBIE, ZombieType.CONE_HEAD, ZombieType.BUCKET_HEAD,
                          ZombieType.FLAG, ZombieType.BALLOON) or \
                z.status in (ZombieStatus.BALLOON_FLYING, ZombieStatus.BALLOON_FALLING) or \
                z.type in (ZombieType.DOLPHIN_RIDER, ZombieType.SNORKEL) or \
                z.action in (ZombieAction.ENTERING_POOL, ZombieAction.LEAVING_POOL):
            return

        current_in_water = False
        # Simplified water check: pool scenes are row 2 and 3
        if self.scene.type in (SceneType.POOL, SceneType.FOG) and z.row in (2, 3):
            if z.int_x < 680:  # Pool boundary approx
                current_in_water = True

        if z.is_in_water:
            if not current_in_water:
                z.action = ZombieAction.LEAVING_POOL
        elif current_in_water:
            if self.scene.spawn.countdown.pool <= 0:  # 错误：类 'SpawnData' 的未解析的特性引用 'countdown'
                z.action = ZombieAction.ENTERING_POOL
                z.is_in_water = True
            else:
                z.countdown.freeze = self.scene.spawn.countdown.pool
                self.damage_system.debuff.set_slowed(z, 2000)

    def _update_entering_home(self, z: Zombie) -> bool:
        if self._is_walk_right(z) and z.x > 850:
            self.zombie_factory.destroy(z)
            return False

        threshold = -100
        if z.type in (ZombieType.GARGANTUAR, ZombieType.GIGA_GARGANTUAR, ZombieType.POLE_VAULTING):
            threshold = -150
        elif z.type in (ZombieType.CATAPULT, ZombieType.FOOTBALL, ZombieType.ZOMBONI):
            threshold = -175
        elif z.type in (ZombieType.BACKUP_DANCER, ZombieType.DANCING, ZombieType.SNORKEL):
            threshold = -130

        if z.int_x < threshold and z.is_not_dying:
            return True

        if z.int_x < threshold + 70 and not z.is_not_dying:
            self.damage_system.take(z, 1800, DamageFlags.BYPASSES_SHIELD | DamageFlags.NO_FLASH)

        return False

    def _update_near_death(self, z: Zombie) -> None:
        if not z.is_dead and z.status != ZombieStatus.DYING and \
                (z.type in (ZombieType.ZOMBONI, ZombieType.CATAPULT) and z.hp < 200 or not z.is_not_dying):
            d = 1
            if z.type == ZombieType.YETI: d = 10
            if z.max_hp >= 500: d = 3

            if self.rng.randint(5) == 0:
                self.damage_system.take(z, d, DamageFlags.BYPASSES_SHIELD | DamageFlags.NO_FLASH)

    def _update_garlic_and_hypno_effect(self, z: Zombie) -> None:
        # Simplified garlic/hypno update
        # TODO: Implement garlic and hypno effect logic
        pass

    def _update_climb_ladder(self, z: Zombie) -> None:
        col = max(0, get_col_by_x(int(z.dy * 0.5 + z.int_x + 5)))  # 错误：类 'Zombie' 的未解析的特性引用 'int_x'
        found_ladder = False
        for item in self.scene.grid_items:
            if item.col == col and item.row == z.row and item.type == GridItemType.LADDER:
                found_ladder = True
                break

        if found_ladder:
            z.dy += 0.8
            if z.dx < 0.5:
                z.x -= 0.5
            if z.dy >= 90:
                z.action = ZombieAction.FALLING
        else:
            z.action = ZombieAction.FALLING

    def _update_action_in_pool(self, z: Zombie) -> None:
        if z.action == ZombieAction.ENTERING_POOL:
            z.dy -= 1
            if z.dy <= -40:
                z.dy = -40
                z.action = ZombieAction.NONE
        elif z.action == ZombieAction.LEAVING_POOL:
            z.dy += 1
            if z.type == ZombieType.SNORKEL:
                z.dy += 1
            if z.dy >= 0:
                z.dy = 0
                z.action = ZombieAction.NONE
                z.is_in_water = False
        elif z.action == ZombieAction.CAUGHT_BY_KELP:
            z.dy -= 1

    def _update_falling(self, z: Zombie) -> None:
        z.dy -= 1
        if z.status == ZombieStatus.POLE_VALUTING_RUNNING:
            z.dy -= 1

        if z.dy <= 0:
            z.dy = 0
            z.action = ZombieAction.NONE

    def _crush_plant(self, z: Zombie) -> None:
        zr = z.get_hit_box_rect()  # TODO: Should be attack box? C++ uses attack box

        for p in list(self.scene.plants):
            if p.row != z.row:
                continue

            pr = p.get_hit_box()
            if zr.get_overlap_len(pr) >= 20 and \
                    p.type not in (PlantType.SPIKEWEED, PlantType.SPIKEROCK):
                # simplified: assume can crush
                # p.is_smashed = True # Should use damage system
                self.damage_system.set_smashed(p)
                self.plant_factory.destroy(p)  # destroy for now
