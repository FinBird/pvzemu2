import math
from typing import Optional

from pvzemu2.enums import PlantType, PlantStatus, ProjectileType, AttackFlags, PlantEdibleStatus, ProjectileMotionType, \
    ZombieStatus, ZombieType
from pvzemu2.objects.plant import Plant
from pvzemu2.objects.plant_reanim_data import (
    PEA_OFFSETS_PEA_SHOOTER, PEA_OFFSETS_SNOW_PEA,
    PEA_OFFSETS_REPEATER, PEA_OFFSETS_SPLIT_PEA, PEA_OFFSETS_GATLING_PEA
)
from pvzemu2.objects.zombie import Zombie
from pvzemu2.scene import Scene
from pvzemu2.systems import reanim
from pvzemu2.systems.damage import DamageSystem
from pvzemu2.systems.plant_factory import PlantFactory
from pvzemu2.systems.plant_subsystems.blover import BloverSubsystem
from pvzemu2.systems.plant_subsystems.cactus import CactusSubsystem
from pvzemu2.systems.plant_subsystems.chomper import ChomperSubsystem
from pvzemu2.systems.plant_subsystems.cob_cannon import CobCannonSubsystem
from pvzemu2.systems.plant_subsystems.fume_shroom import FumeShroomSubsystem
from pvzemu2.systems.plant_subsystems.grave_buster import GraveBusterSubsystem
from pvzemu2.systems.plant_subsystems.imitater import ImitaterSubsystem
from pvzemu2.systems.plant_subsystems.mushroom_family import MushroomFamilySubsystem
from pvzemu2.systems.plant_subsystems.pea_family import PeaFamilySubsystem
from pvzemu2.systems.plant_subsystems.potato_mine import PotatoMineSubsystem
from pvzemu2.systems.plant_subsystems.shield_plants import ShieldPlantsSubsystem
from pvzemu2.systems.plant_subsystems.spike_family import SpikeFamilySubsystem
from pvzemu2.systems.plant_subsystems.squash import SquashSubsystem
from pvzemu2.systems.plant_subsystems.starfruit import StarfruitSubsystem
from pvzemu2.systems.plant_subsystems.sun_plants import SunPlantsSubsystem
from pvzemu2.systems.plant_subsystems.tangle_kelp import TangleKelpSubsystem
from pvzemu2.systems.plant_subsystems.torchwood import TorchwoodSubsystem
from pvzemu2.systems.plant_subsystems.umbrella_leaf import UmbrellaLeafSubsystem
from pvzemu2.systems.projectile_factory import ProjectileFactory
from pvzemu2.systems.rng import RNG
from pvzemu2.systems.util import get_row_by_x_and_y

LAUNCH_COOLDOWN_TABLE = {
    PlantType.FUMESHROOM: 50,
    PlantType.PUFFSHROOM: 29,
    PlantType.SCAREDYSHROOM: 25,
    PlantType.CABBAGEPULT: 32,
    PlantType.MELONPULT: 36,
    PlantType.WINTER_MELON: 36,
    PlantType.KERNELPULT: 30,
    PlantType.CACTUS: 35,
    PlantType.GATLING_PEA: 100,  # 连发植物基础CD
    PlantType.REPEATER: 26,
    PlantType.SPLIT_PEA: 26,
    PlantType.PEA_SHOOTER: 35,
    PlantType.SNOW_PEA: 35,
    PlantType.THREEPEATER: 35,
    PlantType.GLOOMSHROOM: 200,
    PlantType.CATTAIL: 50,
    PlantType.STARFRUIT: 40,
}


class PlantSystem:
    def __init__(self, scene: Scene, projectile_factory: ProjectileFactory, damage_system: DamageSystem,
                 plant_factory: PlantFactory) -> None:

        self.scene = scene
        self.projectile_factory = projectile_factory
        self.damage_system = damage_system
        self.plant_factory = plant_factory
        self.rng = RNG(scene)

        self.cob_cannon_subsystem = CobCannonSubsystem(scene, damage_system, self.rng)
        self.blover_subsystem = BloverSubsystem(scene, damage_system, self.rng)
        self.grave_buster_subsystem = GraveBusterSubsystem(scene, damage_system, self.rng)
        self.spike_family_subsystem = SpikeFamilySubsystem(scene, damage_system, self.rng)
        self.squash_subsystem = SquashSubsystem(scene, damage_system, self.rng)
        self.chomper_subsystem = ChomperSubsystem(scene, damage_system, self.rng)
        self.potato_mine_subsystem = PotatoMineSubsystem(scene, damage_system, self.rng)
        self.tangle_kelp_subsystem = TangleKelpSubsystem(scene, damage_system, self.rng)
        self.mushroom_family_subsystem = MushroomFamilySubsystem(scene, damage_system, self.rng)
        self.pea_family_subsystem = PeaFamilySubsystem(scene, damage_system, self.rng)
        self.shield_plants_subsystem = ShieldPlantsSubsystem(scene, damage_system, self.rng)
        self.starfruit_subsystem = StarfruitSubsystem(scene, damage_system, self.rng, projectile_factory)
        self.torchwood_subsystem = TorchwoodSubsystem(scene, damage_system, self.rng)
        self.umbrella_leaf_subsystem = UmbrellaLeafSubsystem(scene, damage_system, self.rng)
        self.cactus_subsystem = CactusSubsystem(scene, damage_system, self.rng)
        self.imitater_subsystem = ImitaterSubsystem(scene, damage_system, self.rng)
        self.sun_plants_subsystem = SunPlantsSubsystem(scene, damage_system, self.rng)
        self.fume_shroom_subsystem = FumeShroomSubsystem(scene, damage_system, self.rng)
        # self.HypnoShroomSubsystem = HypnoShroomSubsystem(scene,damage_system, self.rng)

    def update(self) -> None:
        """对应 C++ plant_system::update"""
        # Iterate over a copy to allow safe removal during iteration
        for p in list(self.scene.plants):
            if p.is_dead: continue

            self._update_countdown_and_status(p)

            if p.type == PlantType.COB_CANNON:
                self.cob_cannon_subsystem.update(p)
            elif p.type == PlantType.BLOVER:
                self.blover_subsystem.update(p)
            elif p.type == PlantType.GRAVE_BUSTER:
                self.grave_buster_subsystem.update(p)
            elif p.type in (PlantType.SPIKEWEED, PlantType.SPIKEROCK):
                self.spike_family_subsystem.update(p)
            elif p.type == PlantType.SQUASH:
                self.squash_subsystem.update(p)
            elif p.type == PlantType.CHOMPER:
                self.chomper_subsystem.update(p)
            elif p.type == PlantType.POTATO_MINE:
                self.potato_mine_subsystem.update(p)
            elif p.type == PlantType.TANGLE_KELP:
                self.tangle_kelp_subsystem.update(p)
            elif p.type in (PlantType.DOOMSHROOM, PlantType.SUNSHROOM, PlantType.ICESHROOM, PlantType.MAGNETSHROOM,
                            PlantType.SCAREDYSHROOM):
                self.mushroom_family_subsystem.update(p)
            elif p.type in (PlantType.WALLNUT, PlantType.TALLNUT, PlantType.PUMPKIN, PlantType.GARLIC):
                self.shield_plants_subsystem.update(p)
            elif p.type == PlantType.STARFRUIT:
                self.starfruit_subsystem.update(p)
            elif p.type == PlantType.TORCHWOOD:
                self.torchwood_subsystem.update(p)
            elif p.type == PlantType.UMBRELLA_LEAF:
                self.umbrella_leaf_subsystem.update(p)
            elif p.type == PlantType.CACTUS:
                self.cactus_subsystem.update(p)
            elif p.type == PlantType.IMITATER:
                self.imitater_subsystem.update(p)
            elif p.type == PlantType.FUMESHROOM:
                self.fume_shroom_subsystem.update(p)
            elif p.type == PlantType.COFFEE_BEAN:
                # TODO: Implement coffee bean logic (waking up sleeping mushrooms) - Refer to C++ coffee_bean.cpp
                pass
            elif p.type in (PlantType.PEA_SHOOTER, PlantType.REPEATER, PlantType.THREEPEATER, PlantType.SPLIT_PEA,
                            PlantType.GATLING_PEA, PlantType.SNOW_PEA):
                # TODO: Pea family general updates if any (mostly handled in base or specific logic)
                pass

            if p.can_attack or p.type in (PlantType.SUNFLOWER, PlantType.TWIN_SUNFLOWER, PlantType.SUNSHROOM):
                self._update_attack(p)

            if p.countdown.effect > 0:
                p.countdown.effect -= 1
                if p.countdown.effect == 0:
                    self.damage_system.activate_plant(p)

            if p.countdown.eaten > 0:
                p.countdown.eaten -= 1

            if p.hp < 0:
                self.plant_factory.destroy(p)

            reanim.update_progress(p.reanimate)

    def _update_countdown_and_status(self, p: Plant) -> None:
        """对应 C++ plant_system::update_countdown_and_status"""
        if p.status == PlantStatus.WORK or p.is_smashed:
            p.countdown.dead -= 1
            if p.countdown.dead < 1:
                self.plant_factory.destroy(p)
                return

        if p.countdown.awake > 0:
            p.countdown.awake -= 1
            if p.countdown.awake == 0:
                p.is_sleeping = False

        if p.is_sleeping or p.is_smashed or p.edible != PlantEdibleStatus.VISIBLE_AND_EDIBLE:
            return

        self._update_launch_countdown(p)

        if p.countdown.status > 0:
            p.countdown.status -= 1

    def _update_launch_countdown(self, p: Plant) -> None:
        if p.is_smashed or p.edible == PlantEdibleStatus.INVISIBLE_AND_NOT_EDIBLE or p.is_dead or p.countdown.launch == 0:
            return

        p.countdown.launch -= 1

        if p.type == PlantType.THREEPEATER:
            if p.countdown.launch == 1:
                self.launch(p, None, p.row)
                if p.row > 0:
                    self.launch(p, None, p.row - 1)
                if p.row < self.scene.rows - 1:
                    self.launch(p, None, p.row + 1)

        elif p.type == PlantType.SPLIT_PEA:
            if p.countdown.launch == 1:
                if p.split_pea_attack_flags['front']:
                    self.launch(p, None, p.row)
                    p.split_pea_attack_flags['front'] = False
                if p.split_pea_attack_flags['back']:
                    self.launch(p, None, p.row, is_alt_attack=True)
                    p.split_pea_attack_flags['back'] = False

        elif p.type == PlantType.REPEATER:
            if p.countdown.launch == 25 or p.countdown.launch == 1:
                target = self.find_target(p, p.row)
                self.launch(p, target, p.row)

        elif p.type == PlantType.GATLING_PEA:
            # Fire 4 times: approx 75, 50, 25, 1 if start is 100
            if p.countdown.launch in (75, 50, 25, 1):
                target = self.find_target(p, p.row)
                self.launch(p, target, p.row)

        else:
            if p.countdown.launch == 1:
                # Find target before launching
                target = self.find_target(p, p.row)
                self.launch(p, target, p.row)

    def _update_attack(self, p: Plant) -> None:
        """对应 C++ plant_system::update_attack"""
        if p.is_sleeping:
            return

        if p.countdown.generate > 0:
            p.countdown.generate -= 1

        if p.countdown.generate <= 0:
            if p.type in (PlantType.SUNFLOWER, PlantType.TWIN_SUNFLOWER):
                self.sun_plants_subsystem.update(p)
                return

            elif p.type == PlantType.SUNSHROOM:
                self.mushroom_family_subsystem.handle_sunshroom_production(p)
                return

            # Reset countdown
            p.countdown.generate = max(1, p.max_boot_delay - self.rng.randint(15))

            # Logic from plant_base::set_launch_countdown
            # We need to determine if we can attack (find target)
            # If so, set countdown.launch based on plant type/animation

            if p.type == PlantType.STARFRUIT:
                self.starfruit_subsystem.set_launch_countdown(p)
                return

            target = self.find_target(p, p.row)

            if target is None:
                # Some plants might attack without target (e.g. Cherry Bomb immediately?)
                # But mostly shooters need target.
                # If no target, we don't set launch countdown, so we don't shoot.
                return

            # If target found, set launch countdown
            # Delays based on C++ plant_base::set_launch_countdown

            if p.type in (PlantType.PEA_SHOOTER, PlantType.SNOW_PEA, PlantType.REPEATER,
                          PlantType.GATLING_PEA, PlantType.SPLIT_PEA, PlantType.THREEPEATER):
                self.pea_family_subsystem.set_launch_countdown(p, is_alt_attack=False)
                if p.type == PlantType.SPLIT_PEA:
                    self.pea_family_subsystem.set_launch_countdown(p, is_alt_attack=True)

            elif p.type == PlantType.CACTUS:
                self.cactus_subsystem.set_launch_countdown(p)

            elif p.type == PlantType.GLOOMSHROOM:
                p.countdown.launch = 200

            elif p.type == PlantType.CATTAIL:
                p.countdown.launch = 50

            elif p.type == PlantType.FUMESHROOM:
                p.countdown.launch = 50

            elif p.type == PlantType.PUFFSHROOM:
                p.countdown.launch = 29

            elif p.type == PlantType.SCAREDYSHROOM:
                p.countdown.launch = 25

            elif p.type == PlantType.CABBAGEPULT:
                p.countdown.launch = 32

            elif p.type in (PlantType.MELONPULT, PlantType.WINTER_MELON):
                p.countdown.launch = 36

            elif p.type == PlantType.KERNELPULT:
                # Random butter logic
                if self.rng.randint(4) == 0:
                    p.status = PlantStatus.KERNELPULT_LAUNCH_BUTTER
                else:
                    p.status = PlantStatus.IDLE  # Reset status if needed
                p.countdown.launch = 30

            else:
                p.countdown.launch = 29  # Default

    def find_target(self, p: Plant, row: int) -> Optional[Zombie]:
        """对应 C++ plant_base::find_target"""
        flags = AttackFlags.GROUND
        if p.type in (PlantType.CATTAIL, PlantType.CACTUS):
            flags |= AttackFlags.FLYING_BALLOON

        pr_x = p.x
        pr_y = p.y
        pr_w = 900

        if p.type == PlantType.GLOOMSHROOM:
            pr_x = p.x - 80
            pr_w = 240
        elif p.type == PlantType.FUMESHROOM:
            pr_w = 4 * 80
        elif p.type == PlantType.PUFFSHROOM:
            pr_w = 3 * 80

        best_target: Optional[Zombie] = None
        best_weight = -999999.0

        # Optimization: Spatial Partitioning
        candidate_rows = [row]
        if p.type in (PlantType.GLOOMSHROOM, PlantType.THREEPEATER):
            candidate_rows = [row - 1, row, row + 1]
        elif p.type == PlantType.CATTAIL:
            candidate_rows = range(self.scene.rows)

        for r in candidate_rows:
            if not (0 <= r < self.scene.rows):
                continue

            # Iterate only zombies in this row
            for z_id in self.scene.zombies_by_row[r]:
                z = self.scene.zombies.get(z_id)
                if z is None or z.is_dead:
                    continue

                if not self.damage_system.can_be_attacked(z, flags):
                    continue

                # Range check
                if p.type not in (PlantType.GLOOMSHROOM, PlantType.CATTAIL):
                    if z.x < p.x:  # Behind plant
                        continue
                    if z.x > p.x + pr_w:  # Out of range
                        continue
                elif p.type == PlantType.GLOOMSHROOM:
                    if z.x < pr_x or z.x > pr_x + pr_w:
                        continue

                # Weight calculation
                weight = 0.0

                if p.type == PlantType.CATTAIL:
                    dx = z.x - p.x
                    dy = (z.row - p.row) * 100
                    dist = math.sqrt(dx * dx + dy * dy)
                    weight = -dist

                    if z.status in (ZombieStatus.BALLOON_FLYING, ZombieStatus.BALLOON_FALLING):
                        weight += 10000
                else:
                    weight = -z.x

                if best_target is None or weight > best_weight:
                    best_weight = weight
                    best_target = z

        return best_target

    def get_pea_offset(self, p: Plant) -> tuple[int, int]:
        rfs = p.reanimate.get_frame_status()

        # 根据植物类型获取对应的偏移数组
        if p.type == PlantType.PEA_SHOOTER:
            offsets = PEA_OFFSETS_PEA_SHOOTER
        elif p.type == PlantType.SNOW_PEA:
            offsets = PEA_OFFSETS_SNOW_PEA
        elif p.type == PlantType.REPEATER:
            offsets = PEA_OFFSETS_REPEATER
        elif p.type == PlantType.SPLIT_PEA:
            offsets = PEA_OFFSETS_SPLIT_PEA
        elif p.type == PlantType.GATLING_PEA:
            offsets = PEA_OFFSETS_GATLING_PEA
        else:
            return 0, 0

        # 防越界保护
        if rfs.frame >= len(offsets) or rfs.next_frame >= len(offsets):
            return 0, 0

        cx, cy = offsets[rfs.frame]
        nx, ny = offsets[rfs.next_frame]

        # 线性插值计算当前精确的偏移量
        x = int((nx - cx) * rfs.frame_progress + cx)
        y = int((ny - cy) * rfs.frame_progress + cy)

        return x, y

    def launch(self, p: Plant, target: Optional[Zombie], row: int, is_alt_attack: bool = False) -> None:
        """对应 C++ plant_system::launch"""
        proj_type = ProjectileType.NONE

        if p.type == PlantType.FUMESHROOM:
            # damage.range_attack(p, 0x0 | zombie_damage_flags::not_reduce)
            self.fume_shroom_subsystem.attack(p)
            return
        elif p.type == PlantType.GLOOMSHROOM:
            # damage.range_attack(p, 0x0 | zombie_damage_flags::not_reduce)
            return
        elif p.type == PlantType.STARFRUIT:
            self.starfruit_subsystem.attack(p)
            return
        elif p.type in (
        PlantType.PEA_SHOOTER, PlantType.REPEATER, PlantType.THREEPEATER, PlantType.SPLIT_PEA, PlantType.GATLING_PEA):
            proj_type = ProjectileType.PEA
        elif p.type == PlantType.SNOW_PEA:
            proj_type = ProjectileType.SNOW_PEA
        elif p.type == PlantType.CABBAGEPULT:
            proj_type = ProjectileType.CABBAGE
        elif p.type == PlantType.KERNELPULT:
            proj_type = ProjectileType.BUTTER if is_alt_attack else ProjectileType.KERNEL
        elif p.type == PlantType.MELONPULT:
            proj_type = ProjectileType.MELON
        elif p.type == PlantType.WINTER_MELON:
            proj_type = ProjectileType.WINTERMELON
        elif p.type in (PlantType.PUFFSHROOM, PlantType.SCAREDYSHROOM, PlantType.SEASHROOM):
            proj_type = ProjectileType.PUFF
        elif p.type in (PlantType.CACTUS, PlantType.CATTAIL):
            proj_type = ProjectileType.CACTUS
        elif p.type == PlantType.COB_CANNON:
            proj_type = ProjectileType.COB_CANNON

        if proj_type == ProjectileType.NONE:
            return

        # Calculate spawn position
        x, y = 0, 0
        if p.type == PlantType.PUFFSHROOM:
            x = p.x + 40
            y = p.y + 40
        elif p.type == PlantType.SEASHROOM:
            x = p.x + 45
            y = p.y + 63
        elif p.type == PlantType.CABBAGEPULT:
            x = p.x + 5
            y = p.y - 12
        elif p.type in (PlantType.MELONPULT, PlantType.WINTER_MELON):
            x = p.x + 25
            y = p.y - 46
        elif p.type == PlantType.CATTAIL:
            x = p.x + 20
            y = p.y - 3
        elif p.type == PlantType.KERNELPULT:
            if is_alt_attack:
                x = p.x + 12
                y = p.y - 56
            else:
                x = p.x + 19
                y = p.y - 37
        elif p.type in (PlantType.PEA_SHOOTER, PlantType.SNOW_PEA, PlantType.REPEATER):
            ox, oy = self.get_pea_offset(p)
            x = p.x + 24 + ox
            y = p.y - 33 + oy
        elif p.type == PlantType.GATLING_PEA:
            ox, oy = self.get_pea_offset(p)
            x = p.x + 34 + ox
            y = p.y - 33 + oy
        elif p.type == PlantType.SPLIT_PEA:
            ox, oy = self.get_pea_offset(p)
            if is_alt_attack:
                x = p.x - 64 + ox
            else:
                x = p.x + 24 + ox
            y = p.y - 33 + oy
        elif p.type == PlantType.THREEPEATER:
            x = p.x + 45
            y = p.y + 10
        elif p.type == PlantType.SCAREDYSHROOM:
            x = p.x + 29
            y = p.y + 21
        elif p.type == PlantType.CACTUS:
            if p.status == PlantStatus.CACTUS_TALL_IDLE:
                x = p.x + 93
                y = p.y - 50
            else:
                x = p.x + 70
                y = p.y + 23
        elif p.type == PlantType.COB_CANNON:
            x = p.x - 44
            y = p.y - 184
        else:
            x = p.x + 10
            y = p.y + 5

        # Adjust for flower pot (Optimized using plant_map)
        if 0 <= p.row < len(self.scene.plant_map) and 0 <= p.col < 9:
            pot = self.scene.plant_map[p.row][p.col].get('base')
            if pot and pot.type == PlantType.FLOWER_POT:
                if not pot.is_smashed and pot.edible != PlantEdibleStatus.INVISIBLE_AND_NOT_EDIBLE and not pot.is_dead:
                    y -= 5

        proj = self.projectile_factory.create(proj_type, row, x, y)

        # Set attack flags (simplified, C++ uses p.get_attack_flags)
        # Assuming projectile_factory already sets default flags, we might need to override based on plant

        dist_x: float = 0.0
        dist_y: float = 0.0

        if p.type in (PlantType.CABBAGEPULT, PlantType.KERNELPULT, PlantType.MELONPULT, PlantType.WINTER_MELON):
            if target is None:
                dist_x = 700.0 - x
                dist_y = 0.0
            else:
                zr = target.get_hit_box_rect()

                # Simple prediction: target current x + speed * 50
                # C++: zombie_base(scene).predict_after(*target, 50)
                predicted_x = target.x + target.dx * 50.0  # dx is typically negative for zombies moving left
                dist_x = predicted_x - x - 30.0
                dist_y = float(zr.y) - y

                if target.status == ZombieStatus.DOLPHIN_RIDE:
                    dist_x -= 60.0
                elif target.type == ZombieType.POGO and target.has_item_or_walk_left:
                    dist_x -= 60.0
                elif target.status == ZombieStatus.SNORKEL_SWIM:
                    dist_x -= 40.0

            proj.motion_type = ProjectileMotionType.PARABOLA
            proj.dx = float(max(40.0, dist_x) / 120.0)
            proj.dy2 = 0.0
            proj.ddy = float(dist_y / 120.0 - 7.0)
            proj.dddy = 0.115

        elif p.type == PlantType.THREEPEATER:
            if row > p.row:
                proj.motion_type = ProjectileMotionType.SWITCH_WAY
                proj.dy2 = 3.0
                proj.shadow_y -= 80.0
            elif row < p.row:
                proj.motion_type = ProjectileMotionType.SWITCH_WAY
                proj.dy2 = -3.0
                proj.shadow_y += 80.0

        elif p.type in (PlantType.PUFFSHROOM, PlantType.SEASHROOM):
            proj.motion_type = ProjectileMotionType.PUFF

        elif p.type == PlantType.CATTAIL:
            proj.dx = 2.0
            proj.motion_type = ProjectileMotionType.CATTAIL
            # Store target ID or reference. C++ stores index.
            if target:
                proj.target_id = id(target)  # Or handle this in projectile update

        elif p.type == PlantType.COB_CANNON:
            proj.flags = p.get_attack_flags(False)
            proj.dx = 0.001
            proj.motion_type = ProjectileMotionType.PARABOLA
            proj.dy2 = 0.0
            proj.ddy = -8.0
            proj.dddy = 0.0
            proj.cannon_x = float(p.cannon_x)
            proj.cannon_row = get_row_by_x_and_y(self.scene.type, p.cannon_x, p.cannon_y)

        elif p.type == PlantType.SPLIT_PEA:
            if is_alt_attack:
                proj.motion_type = ProjectileMotionType.LEFT_STRAIGHT
