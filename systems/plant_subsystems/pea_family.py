from typing import Optional

from pvzemu2.enums import PlantType
from pvzemu2.objects.plant import Plant
from pvzemu2.objects.zombie import Zombie
from pvzemu2.systems.plant_subsystems.base import PlantSubsystem


class PeaFamilySubsystem(PlantSubsystem):
    def set_launch_countdown(self, p: Plant, is_alt_attack: bool = False) -> None:
        target = self.find_target(p, p.row, is_alt_attack)

        if p.type == PlantType.THREEPEATER:
            # Check 3 rows
            t1 = self.find_target(p, p.row, False)
            t2 = self.find_target(p, p.row - 1, False) if p.row > 0 else None
            t3 = self.find_target(p, p.row + 1, False) if p.row < self.scene.rows - 1 else None

            if t1 or t2 or t3:
                p.countdown.launch = 35
            else:
                p.threepeater_time_since_first_shot = 0
            return

        if target is None:
            return

        if p.type == PlantType.SPLIT_PEA and is_alt_attack:
            p.countdown.launch = 26
            p.split_pea_attack_flags['back'] = True
            return

        if p.type in (PlantType.PEA_SHOOTER, PlantType.SNOW_PEA, PlantType.REPEATER,
                      PlantType.GATLING_PEA, PlantType.SPLIT_PEA, PlantType.THREEPEATER):
            # Assuming has_reanim(anim_shooting) is true
            p.countdown.launch = 35

            if p.type in (PlantType.REPEATER, PlantType.SPLIT_PEA):
                p.countdown.launch = 26
                if p.type == PlantType.SPLIT_PEA:
                    p.split_pea_attack_flags['front'] = True
            elif p.type == PlantType.GATLING_PEA:
                p.countdown.launch = 100

    def find_target(self, p: Plant, row: int, is_alt_attack: bool) -> Optional[Zombie]:
        # Use the same logic as PlantSystem.find_target for consistency
        from pvzemu2.enums import AttackFlags

        flags = AttackFlags.GROUND
        if p.type in (PlantType.CATTAIL, PlantType.CACTUS):
            flags |= AttackFlags.FLYING_BALLOON

        pr_x = p.x
        pr_w = 900

        if p.type == PlantType.SPLIT_PEA and is_alt_attack:
            pr_x = p.x - 900
            pr_w = 900 + 30
        elif p.type == PlantType.GLOOMSHROOM:
            pr_x = p.x - 80
            pr_w = 240
        elif p.type == PlantType.FUMESHROOM:
            pr_w = 4 * 80
        elif p.type == PlantType.PUFFSHROOM:
            pr_w = 3 * 80

        best_target: Optional[Zombie] = None
        best_weight = -999999.0

        for z in self.scene.zombies:
            if z.is_dead:
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
            weight = -z.x

            if best_target is None or weight > best_weight:
                best_weight = weight
                best_target = z

        return best_target
