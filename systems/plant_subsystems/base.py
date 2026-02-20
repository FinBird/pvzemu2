import math
from typing import Optional, TYPE_CHECKING

from pvzemu2.enums import PlantType, ZombieStatus, PlantReanimName, PlantStatus
from pvzemu2.objects.base import ReanimateType

if TYPE_CHECKING:
    from pvzemu2.scene import Scene
    from pvzemu2.objects.plant import Plant
    from pvzemu2.objects.zombie import Zombie
    from pvzemu2.systems.damage import DamageSystem
    from pvzemu2.systems.rng import RNG


class PlantSubsystem:
    def __init__(self, scene: 'Scene', damage_system: 'DamageSystem', rng: 'RNG'):
        self.scene = scene
        self.damage_system = damage_system
        self.rng = rng

    def update(self, plant: 'Plant') -> None:
        """Called every frame for the plant. Override for specific state machine logic."""
        pass

    def set_launch_countdown(self, plant: 'Plant', is_alt_attack: bool = False) -> None:
        """
        Determines if the plant should attack and sets the launch countdown.
        Default implementation for standard shooters (Peashooters, Pults).
        """
        target = self.find_target(plant, plant.row, is_alt_attack)
        if target is None:
            return

        # Split pea rear attack
        if plant.type == PlantType.SPLIT_PEA and is_alt_attack:
            plant.set_reanim(PlantReanimName.anim_shooting, ReanimateType.ONCE, 35)
            plant.countdown.launch = 26
            plant.split_pea_attack_flags['back'] = True
            return

        # Pea‑family shooters with shooting animation
        if plant.type in (PlantType.PEA_SHOOTER, PlantType.SNOW_PEA, PlantType.REPEATER,
                          PlantType.GATLING_PEA, PlantType.SPLIT_PEA, PlantType.THREEPEATER):
            if plant.has_reanim(PlantReanimName.anim_shooting):
                plant.set_reanim(PlantReanimName.anim_shooting, ReanimateType.ONCE, 35)
                plant.countdown.launch = 35
                if plant.type in (PlantType.REPEATER, PlantType.SPLIT_PEA):
                    plant.countdown.launch = 26
                    if plant.type == PlantType.SPLIT_PEA:
                        plant.split_pea_attack_flags['front'] = True
                elif plant.type == PlantType.GATLING_PEA:
                    plant.countdown.launch = 100
                return

        # Cactus tall idle state
        if plant.status == PlantStatus.CACTUS_TALL_IDLE:
            if plant.has_reanim(PlantReanimName.anim_shootinghigh):
                plant.set_reanim(PlantReanimName.anim_shootinghigh, ReanimateType.ONCE, 35)
                plant.countdown.launch = 23
                return

        # Gloomshroom
        if plant.type == PlantType.GLOOMSHROOM:
            if plant.has_reanim(PlantReanimName.anim_shooting):
                plant.set_reanim(PlantReanimName.anim_shooting, ReanimateType.ONCE, 14)
                plant.countdown.launch = 200
                return

        # Cattail
        if plant.type == PlantType.CATTAIL:
            if plant.has_reanim(PlantReanimName.anim_shooting):
                plant.set_reanim(PlantReanimName.anim_shooting, ReanimateType.ONCE, 30)
                plant.countdown.launch = 50
                return

        # Plants without shooting animation (e.g., instant‑use plants) – launch immediately
        if not plant.has_reanim(PlantReanimName.anim_shooting):
            # We use 1 to trigger launch in next update if no animation
            plant.countdown.launch = 1
            return

        # Generic shooting animation for other plants
        plant.set_reanim(PlantReanimName.anim_shooting, ReanimateType.ONCE, 35)
        if plant.type == PlantType.FUMESHROOM:
            plant.countdown.launch = 50
        elif plant.type == PlantType.PUFFSHROOM:
            plant.countdown.launch = 29
        elif plant.type == PlantType.SCAREDYSHROOM:
            plant.countdown.launch = 25
        elif plant.type == PlantType.CABBAGEPULT:
            plant.countdown.launch = 32
        elif plant.type in (PlantType.MELONPULT, PlantType.WINTER_MELON):
            plant.countdown.launch = 36
        elif plant.type == PlantType.KERNELPULT:
            if self.rng.randint(4) == 0:
                plant.status = PlantStatus.KERNELPULT_LAUNCH_BUTTER
            else:
                plant.status = PlantStatus.IDLE
            plant.countdown.launch = 30
        elif plant.type == PlantType.CACTUS:
            plant.countdown.launch = 35
        else:
            plant.countdown.launch = 29

    def find_target(self, plant: 'Plant', row: int, is_alt_attack: bool = False) -> Optional['Zombie']:
        """
        Generic target finding logic corresponding to C++ `plant_base::find_target`.
        Handles ground plants, range checks, and gloomshroom/cattail specifics if needed (though usually overridden).
        """
        flags = plant.get_attack_flags(is_alt_attack)
        pr_abs = plant.get_attack_box(is_alt_attack)

        best_target: Optional['Zombie'] = None
        best_weight = -999999.0

        # Spatial Optimization: Only check relevant rows
        candidate_rows = [row]
        if plant.type == PlantType.GLOOMSHROOM:
            candidate_rows = [row - 1, row, row + 1]
        elif plant.type == PlantType.CATTAIL:
            candidate_rows = range(self.scene.rows)

        for r in candidate_rows:
            if not (0 <= r < self.scene.rows):
                continue

            for z_id in self.scene.zombies_by_row[r]:
                z = self.scene.zombies.get(z_id)
                if z is None: continue

                # Basic exclusions
                if not z.is_not_dying: continue

                # Special Tangle Kelp exclusion
                # if is_target_of_kelp(z): continue (TODO: Implement helper)

                # Potato mine specific checks
                if plant.type == PlantType.POTATO_MINE or plant.type == PlantType.CHOMPER:
                    # Logic handled in specific subsystems usually, but if called here:
                    pass

                # Gloomshroom Row Check
                if plant.type == PlantType.GLOOMSHROOM:
                    if abs(z.row - row) > 1: continue
                elif z.row != row and plant.type != PlantType.CATTAIL:
                    continue

                if not self.damage_system.can_be_attacked(z, flags):
                    continue

                # C++ overlap logic simplification
                zr = z.get_hit_box_rect()

                # Check overlap
                # C++: if (pr.get_overlap_len(zr) >= -overlap)
                # Here we simplify to standard overlap check
                overlap_len = pr_abs.get_overlap_len(zr)

                # Basic range check for standard shooters
                if plant.type not in (PlantType.GLOOMSHROOM, PlantType.CATTAIL):
                    if z.x < plant.x: continue  # Behind
                    if z.x > 800: continue  # Off screen right (approx)

                if overlap_len >= 0:  # Overlapping or within range
                    weight = -z.x  # Default: Target closest to house (leftmost) has highest weight (lowest x)

                    if plant.type == PlantType.CATTAIL:
                        dist = math.hypot(z.x - plant.x, (z.row - plant.row) * 100)
                        weight = -dist
                        # Priority to Balloon
                        if z.status in (ZombieStatus.BALLOON_FLYING, ZombieStatus.BALLOON_FALLING):
                            weight += 10000

                    if best_target is None or weight > best_weight:
                        best_weight = weight
                        best_target = z

        return best_target
