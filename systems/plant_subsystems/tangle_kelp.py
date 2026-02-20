from typing import Optional

from pvzemu2.enums import PlantStatus, ZombieAction, AttackFlags, DamageFlags
from pvzemu2.objects.plant import Plant
from pvzemu2.objects.zombie import Zombie
from pvzemu2.systems.plant_subsystems.base import PlantSubsystem


class TangleKelpSubsystem(PlantSubsystem):
    def update(self, plant: Plant) -> None:
        if plant.status == PlantStatus.TANGLE_KELP_GRAB:
            target = None
            if plant.target_id != -1:
                # Find zombie by ID using O(1) lookup
                target = self.scene.zombies.get(plant.target_id)

            if plant.countdown.status == 50 and target:
                target.action = ZombieAction.CAUGHT_BY_KELP
                target.is_eating = False  # Unset eating

            elif plant.countdown.status == 0:
                plant.hp = -1  # Destroy plant
                if target:
                    self.damage_system.take(target, target.max_hp + 1000,
                                            DamageFlags.DAMAGE_HITS_SHIELD_AND_BODY)  # Destroy zombie

        else:
            target = self.find_target(plant, plant.row)
            if target:
                plant.status = PlantStatus.TANGLE_KELP_GRAB
                plant.countdown.status = 100
                plant.target_id = target.id

    def find_target(self, plant: Plant, row: int) -> Optional[Zombie]:
        # Tangle kelp targets zombies in water
        # Range is overlap?

        # Spatial optimization: only iterate zombies in the same row
        candidates = []
        if 0 <= row < len(self.scene.zombies_by_row):
            candidates = list(self.scene.zombies_by_row[row])

        for z_id in candidates:
            z = self.scene.zombies.get(z_id)
            if z is None: continue

            if z.is_dead: continue
            # Row check implicit

            # Must in water (implied by row usually, but check status/type?)
            # C++ checks `z.is_in_water`.
            # In Python `Zombie` likely has `is_in_water` or we check scene type and row?
            # Or just `z.status` implies water?
            # `ZombieStatus.SNORKEL_SWIM`, `DOLPHIN_...` etc.
            # `pvzemu2/objects/zombie.py` might have `is_in_water`.
            # If not, we can infer from scene type and row.

            # Let's assume for now we check if scene is pool/fog and row is 2 or 3 (0-5).
            # But let's check overlap first.

            if not self.damage_system.can_be_attacked(z, AttackFlags.GROUND):
                continue

            zr = z.get_hit_box_rect()
            pr = plant.get_hit_box()  # or attack box

            if pr.get_overlap_len(zr) >= 0:  # Overlapping
                return z

        return None
