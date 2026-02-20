from pvzemu2.enums import PlantStatus, PlantType, DamageFlags, PlantReanimName
from pvzemu2.objects.base import ReanimateType
from pvzemu2.objects.plant import Plant
from pvzemu2.systems.plant_subsystems.base import PlantSubsystem


class SpikeFamilySubsystem(PlantSubsystem):
    def update(self, plant: Plant) -> None:
        if plant.status == PlantStatus.SPIKE_ATTACK:
            if plant.countdown.status == 0:
                plant.status = PlantStatus.IDLE

                plant.set_reanim_frame(PlantReanimName.anim_idle)
                plant.reanimate.type = ReanimateType.REPEAT
                plant.reanimate.fps = 12.0
                plant.reanimate.n_repeated = 0
                return

            t = 75
            if plant.type == PlantType.SPIKEROCK:
                if plant.countdown.status == 70:
                    self.attack(plant)
                    return
                t = 32

            if plant.countdown.status == t:
                self.attack(plant)

            return

        elif self.find_target(plant, plant.row):
            plant.set_reanim_frame(PlantReanimName.anim_attack)
            plant.reanimate.type = ReanimateType.ONCE
            plant.reanimate.fps = 18.0
            plant.reanimate.n_repeated = 0

            plant.status = PlantStatus.SPIKE_ATTACK
            plant.countdown.status = 100

    def attack(self, plant: Plant) -> None:
        self.damage_system.range_attack(plant, DamageFlags.SPIKE | DamageFlags.BYPASSES_SHIELD)

    def find_target(self, plant: Plant, row: int, is_alt_attack: bool = False) -> bool:
        flags = self.damage_system._get_plant_attack_flags(plant)

        pr = plant.attack_box
        pr_abs = plant.get_attack_box()

        # Spatial optimization: only iterate zombies in the same row
        candidates = []
        if 0 <= row < len(self.scene.zombies_by_row):
            candidates = list(self.scene.zombies_by_row[row])

        for z_id in candidates:
            z = self.scene.zombies.get(z_id)
            if z is None: continue

            # Row check implicit

            if not self.damage_system.can_be_attacked(z, flags):
                continue

            zr = z.get_hit_box_rect()
            if pr_abs.get_overlap_len(zr) > 0:
                return True

        return False
