import math
from typing import Optional, List, Tuple

from pvzemu2.enums import (
    ProjectileMotionType, ProjectileType, ZombieType, ZombieAccessoriesType2, ZombieStatus,
    PlantType, PlantStatus, SceneType, PlantEdibleStatus
)
from pvzemu2.objects.plant import Plant
from pvzemu2.objects.projectile import Projectile
from pvzemu2.objects.zombie import Zombie
from pvzemu2.scene import Scene
from pvzemu2.systems.damage import DamageSystem
from pvzemu2.systems.projectile_factory import ProjectileFactory
from pvzemu2.systems.util import (
    get_y_by_row_and_col, get_col_by_x, get_row_by_x_and_y,
    get_y_by_row_and_x
)


class ProjectileSystem:
    def __init__(self, scene: Scene, damage_system: DamageSystem, factory: ProjectileFactory) -> None:
        self.scene = scene
        self.damage_system = damage_system
        self.factory = factory

    def _is_water_grid(self, row: int, col: int) -> bool:
        if self.scene.type in (SceneType.POOL, SceneType.FOG):
            return row == 2 or row == 3
        return False

    def _get_star_row_by_x_and_y(self, x: int, y: int) -> int:
        return max(0, get_row_by_x_and_y(self.scene.type, max(40, x), y))

    def _is_in_torchwood(self, proj: Projectile) -> bool:
        if proj.type not in (ProjectileType.PEA, ProjectileType.SNOW_PEA):
            return False

        proj_rect = proj.get_attack_box()

        for p in self.scene.plants:
            if (p.row == proj.row and
                    p.type == PlantType.TORCHWOOD and
                    not p.is_smashed and
                    not p.is_dead and
                    proj.last_torchwood_col != p.col):

                pr = p.get_attack_box()
                if proj_rect.get_overlap_len(pr) > 10:
                    # Update projectile type to FIRE_PEA
                    proj.type = ProjectileType.FIRE_PEA
                    proj.last_torchwood_col = p.col
                    return True
        return False

    def _find_zombie_target(self, proj: Projectile) -> Optional[Zombie]:
        if self._is_in_torchwood(proj):
            return None

        proj_rect = proj.get_attack_box()
        min_x = 9999
        target: Optional[Zombie] = None

        # Optimization: Only iterate zombies in the same row
        if 0 <= proj.row < self.scene.rows:
            candidate_ids = self.scene.zombies_by_row[proj.row]
        else:
            candidate_ids = []

        for z_id in candidate_ids:
            z = self.scene.zombies.get(z_id)
            if z is None or z.is_dead:
                continue

            if (z.row == proj.row and
                    self.damage_system.can_be_attacked(z, proj.flags) and
                    (z.status != ZombieStatus.SNORKEL_SWIM or proj.dy1 > 45) and
                    (proj.type != ProjectileType.STAR or
                     proj.time_since_created >= 25 or
                     proj.dx < 0 or
                     z.type != ZombieType.DIGGER)):

                zr = z.get_hit_box_rect()

                if (proj_rect.get_overlap_len(zr) >= 0 and
                        (target is None or z.int_x < min_x)):
                    target = z
                    min_x = z.int_x

        return target

    def _find_plant_target(self, proj: Projectile) -> Optional[Plant]:
        proj_rect = proj.get_attack_box()
        target: Optional[Plant] = None

        for p in self.scene.plants:
            if (p.row == proj.row and
                    p.type not in (PlantType.PUFFSHROOM, PlantType.SUNSHROOM,
                                   PlantType.POTATO_MINE, PlantType.SPIKEWEED,
                                   PlantType.LILY_PAD)):

                pr = p.get_hit_box()
                if proj_rect.get_overlap_len(pr) > 8:
                    target = p
                    break

        if target is None:
            return None

        # In actual game, need to check if plant is on pumpkin/lilypad etc.
        # But here we simplified scene structure so we just return target.
        # If we had stacked plants, we would check top-most plant.

        return target

    def _is_covered_by_suppter(self, proj: Projectile, z: Zombie) -> bool:
        proj_rect = proj.get_attack_box()
        zr = z.get_hit_box_rect()

        if ((z.type in (ZombieType.CATAPULT, ZombieType.ZOMBONI) or
             z.accessory_2_type in (ZombieAccessoriesType2.SCREEN_DOOR, ZombieAccessoriesType2.LADDER)) and
                proj.type == ProjectileType.FIRE_PEA):
            return False

        if (proj.type == ProjectileType.FIRE_PEA and proj.row != z.row or
                abs(int(proj.row) - int(z.row)) > 1 or
                not self.damage_system.can_be_attacked(z, proj.flags)):
            return False

        return zr.get_overlap_len(proj_rect) >= 0

    def _suppter_attack(self, proj: Projectile, main_target: Optional[Zombie]) -> None:
        n = 0
        targets: List[Zombie] = []

        # Optimization: Only check adjacent rows
        rows_to_check = [proj.row - 1, proj.row, proj.row + 1]

        for r in rows_to_check:
            if 0 <= r < self.scene.rows:
                for z_id in self.scene.zombies_by_row[r]:
                    z = self.scene.zombies.get(z_id)
                    if z and not z.is_dead and self._is_covered_by_suppter(proj, z):
                        targets.append(z)
                        if z is not main_target:
                            n += 1

        damage_val = Projectile.DAMAGE[int(proj.type)]
        max_total_damage = damage_val if proj.type == ProjectileType.FIRE_PEA else 7 * damage_val

        splash_damage = damage_val // 3

        if n * splash_damage > max_total_damage:
            splash_damage = max(1, max_total_damage // n)

        for z in targets:
            flags = proj.get_flags_with_zombie(z)
            if z is main_target:
                self.damage_system.take(z, damage_val, flags)
            else:
                self.damage_system.take(z, splash_damage, flags)

    def _attack_target_zombie(self, proj: Projectile, z: Optional[Zombie]) -> None:
        # Check special conditions for Fire Pea vs Shield/Vehicle
        special_fire_pea = False
        if (proj.type == ProjectileType.FIRE_PEA and z is not None and
                (z.type in (ZombieType.CATAPULT, ZombieType.ZOMBONI) or
                 z.accessory_2_type in (ZombieAccessoriesType2.LADDER, ZombieAccessoriesType2.SCREEN_DOOR))):
            special_fire_pea = True

        if (special_fire_pea or
                proj.type not in (ProjectileType.MELON, ProjectileType.WINTERMELON, ProjectileType.FIRE_PEA)):

            if z:
                damage_val = Projectile.DAMAGE[int(proj.type)]
                self.damage_system.take(z, damage_val, proj.get_flags_with_zombie(z))
        else:
            if proj.type == ProjectileType.FIRE_PEA and z is not None:
                # Remove freeze/slow effect
                z.countdown.freeze = 0
                z.countdown.slow = 0

            self._suppter_attack(proj, z)

        if proj.type == ProjectileType.BUTTER:
            if z is not None:
                z.countdown.butter = 400
                # Also stop eating if buttered
                z.is_eating = False

        self.factory.destroy(proj)

    def _parabola_do_attack(self, proj: Projectile, z: Optional[Zombie]) -> None:
        if proj.type == ProjectileType.COB_CANNON:
            self.damage_system.take_instant_kill(
                proj.row,
                int(proj.x + 80),
                int(proj.y + 40),
                115,
                1,
                True,
                proj.flags
            )
            self._attack_target_zombie(proj, None)
        else:
            self._attack_target_zombie(proj, z)

    def _do_parabola_motion(self, proj: Projectile) -> None:
        # Cob Cannon special logic
        if proj.type == ProjectileType.COB_CANNON and proj.dy1 < -700:
            proj.ddy = 8
            proj.row = proj.cannon_row  # 切换到目标行
            proj.x = proj.cannon_x  # 切换到目标X

            col = max(0, get_col_by_x(int(proj.cannon_x)))
            proj.y = float(get_y_by_row_and_col(self.scene.type, proj.cannon_row, col))
            proj.shadow_y = proj.y + 67

        proj.ddy += proj.dddy
        proj.x += proj.dx
        proj.y += proj.dy2
        proj.dy1 += proj.ddy

        ddy_below_0 = proj.ddy < 0

        # 1. 特定投掷物上升阶段不检测碰撞
        if ddy_below_0 and proj.type in (ProjectileType.BASKETBALL, ProjectileType.COB_CANNON):
            return

        # 2. 创建 20 帧后的高度检测
        if proj.time_since_created > 20:
            if ddy_below_0:
                return

            top_dy1 = 0.0
            if proj.type == ProjectileType.BUTTER:
                top_dy1 = -32
            elif proj.type == ProjectileType.BASKETBALL:
                top_dy1 = 60
            elif proj.type in (ProjectileType.MELON, ProjectileType.WINTERMELON):
                top_dy1 = -35
            elif proj.type in (ProjectileType.CABBAGE, ProjectileType.KERNEL):
                top_dy1 = -30
            elif proj.type == ProjectileType.COB_CANNON:
                top_dy1 = -60

            if self._is_water_grid(proj.row, 0):
                top_dy1 += 40

            # 高度过高时不检测碰撞
            if proj.dy1 >= top_dy1:
                return

        plant_target: Optional[Plant] = None
        zombie_target: Optional[Zombie] = None

        if proj.type == ProjectileType.BASKETBALL:
            plant_target = self._find_plant_target(proj)
        else:
            zombie_target = self._find_zombie_target(proj)

        if zombie_target:
            self._parabola_do_attack(proj, zombie_target)
        elif plant_target:
            # Plant target found (Basketball)
            for p in self.scene.plants:
                if (p.type == PlantType.UMBRELLA_LEAF and
                        not p.is_smashed and
                        p.edible != PlantEdibleStatus.INVISIBLE_AND_NOT_EDIBLE and
                        not p.is_dead and
                        abs(int(p.col) - int(plant_target.col)) <= 1 and
                        abs(int(p.row) - int(plant_target.row)) <= 1):

                    if p.status == PlantStatus.UMBRELLA_LEAF_SHRINK:
                        self.factory.destroy(proj)
                    elif p.status != PlantStatus.UMBRELLA_LEAF_BLOCK:
                        self.damage_system.activate_plant(p)
                    return

            plant_target.hp -= Projectile.DAMAGE[int(proj.type)]
            if plant_target.hp <= 0:
                plant_target.is_dead = True

            self.factory.destroy(proj)
        else:
            # 落地判定
            threshold = -40 if proj.type == ProjectileType.COB_CANNON else 80
            if proj.dy1 > threshold:
                self._parabola_do_attack(proj, None)

    def _others_do_attack(self, proj: Projectile) -> None:
        if (proj.motion_type == ProjectileMotionType.PUFF and
                proj.time_since_created >= 75 or
                proj.x > 800 or
                proj.attack_box_width + proj.x < 0):
            self.factory.destroy(proj)
            return

        if proj.motion_type == ProjectileMotionType.CATTAIL:
            # TODO: Implement full Cattail logic (requires target ID tracking)
            # For now, simplistic implementation
            pass

        if proj.type == ProjectileType.STAR and (proj.y > 600 or proj.y < 40):
            self.factory.destroy(proj)
            return

        if (int(proj.type) > 0 and proj.type != ProjectileType.STAR or
                proj.shadow_y - proj.y <= 90):
            target = self._find_zombie_target(proj)
            if target:
                self._attack_target_zombie(proj, target)

    def _roof_set_disappear(self, proj: Projectile) -> None:
        diff = proj.shadow_y - proj.y

        if (proj.type in (ProjectileType.PEA, ProjectileType.SNOW_PEA,
                          ProjectileType.FIRE_PEA, ProjectileType.CACTUS,
                          ProjectileType.COB_CANNON) and diff < 28):
            self.factory.destroy(proj)
        elif proj.type == ProjectileType.PUFF and diff < 0:
            self.factory.destroy(proj)
        elif proj.type == ProjectileType.STAR and diff < 23:
            self.factory.destroy(proj)

    def _get_vector_cos_and_sin(self, x: float, y: float) -> Tuple[float, float]:
        d = math.sqrt(x * x + y * y)
        if d == 0:
            return x, y
        return x / d, y / d

    def _do_other_motion(self, proj: Projectile) -> None:
        if proj.motion_type == ProjectileMotionType.LEFT_STRAIGHT:
            proj.x -= 3.33

        elif proj.motion_type == ProjectileMotionType.CATTAIL:
            # Simplistic Cattail (homing) logic
            # Needs target tracking which is partially in proj.target_id
            # This is complex to port without full zombie map
            pass

        elif proj.motion_type == ProjectileMotionType.STARFRUIT:
            proj.y += proj.dy2
            proj.x += proj.dx
            proj.shadow_y += proj.dy2

            if proj.dy2 != 0:
                proj.row = self._get_star_row_by_x_and_y(int(proj.x), int(proj.y))

        else:
            proj.x += 3.33

            if proj.motion_type == ProjectileMotionType.SWITCH_WAY:
                proj.y += proj.dy2
                proj.dy2 *= 0.97
                proj.shadow_y += proj.dy2

        self._others_do_attack(proj)
        self._roof_set_disappear(proj)

    def update(self) -> None:
        """对应 C++ projectile_system::update"""
        # Iterate copy for safe removal
        for proj in list(self.scene.projectiles):
            if proj.is_disappeared:
                continue

            proj.time_since_created += 1
            if proj.countdown > 0:
                proj.countdown -= 1

            row = proj.row
            y_before = get_y_by_row_and_x(self.scene.type, proj.row, proj.x)

            if proj.motion_type == ProjectileMotionType.PARABOLA:
                self._do_parabola_motion(proj)
            else:
                self._do_other_motion(proj)

            y_after = get_y_by_row_and_x(self.scene.type, row, proj.x)
            diff = y_after - y_before

            if proj.motion_type == ProjectileMotionType.PARABOLA:
                proj.y += diff
                proj.dy1 = proj.dy1 - diff

            proj.shadow_y += diff
            proj.int_x = int(proj.x)
            proj.int_y = int(proj.dy1 + proj.y)
