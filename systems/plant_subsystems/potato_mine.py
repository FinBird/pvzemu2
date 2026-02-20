from typing import Optional

from pvzemu2.enums import PlantStatus, ZombieStatus, ZombieType, AttackFlags
from pvzemu2.objects.plant import Plant
from pvzemu2.objects.zombie import Zombie
from pvzemu2.systems.plant_subsystems.base import PlantSubsystem


class PotatoMineSubsystem(PlantSubsystem):
    def update(self, plant: Plant) -> None:
        if plant.status == PlantStatus.IDLE:
            if plant.countdown.status == 0:
                # p.set_reanim(plant_reanim_name::anim_rise, reanim_type::once, 18);
                plant.status = PlantStatus.POTATO_SPROUT_OUT
                plant.countdown.status = 50  # Animation delay

        elif plant.status == PlantStatus.POTATO_SPROUT_OUT:
            if plant.countdown.status == 0:
                plant.status = PlantStatus.POTATO_ARMED

        elif plant.status == PlantStatus.POTATO_ARMED:
            if self.find_target(plant, plant.row):
                self.damage_system.activate_plant(plant)

    def find_target(self, plant: Plant, row: int) -> Optional[Zombie]:
        # Potato mine trigger range
        # C++: pr.x += 40, pr.width -= 40.
        # This means trigger area is the right half of the plant's tile?
        # Or centered?
        # Plant box 80x80. x+=40 means x=[40, 80] relative to plant.
        # So zombie needs to be past the center of the plant.

        trigger_x = plant.x + 40

        # Spatial optimization: only iterate zombies in the same row
        candidates = []
        if 0 <= row < len(self.scene.zombies_by_row):
            candidates = list(self.scene.zombies_by_row[row])

        for z_id in candidates:
            z = self.scene.zombies.get(z_id)
            if z is None: continue

            if z.is_dead: continue
            # Row check implicit

            # Ignore flying/jumping unless pole vaulting special case?
            # C++: if pogo or pole jumping/running -> continue

            if (z.type == ZombieType.POGO and z.has_item_or_walk_left) or \
                    z.status in (ZombieStatus.POLE_VALUTING_JUMPING, ZombieStatus.POLE_VALUTING_RUNNING):
                continue

            if z.type == ZombieType.BUNGEE and z.bungee_col != plant.col:
                continue

            if not self.damage_system.can_be_attacked(z, AttackFlags.GROUND):
                continue

            zr = z.get_hit_box_rect()

            # Check overlap with trigger area
            # Trigger area: [trigger_x, plant.x + 80]
            # Zombie rect overlap

            # Simple check: if zombie is close enough
            # Overlap check

            overlap_start = max(trigger_x, zr.x)
            overlap_end = min(plant.x + 80, zr.x + zr.width)

            if overlap_end > overlap_start:
                # Overlapping
                return z

        return None
