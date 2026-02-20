from pvzemu2.enums import PlantStatus, PlantReanimName
from pvzemu2.objects.base import ReanimateType
from pvzemu2.objects.plant import Plant
from pvzemu2.systems.plant_subsystems.base import PlantSubsystem


class BloverSubsystem(PlantSubsystem):
    def update(self, plant: Plant) -> None:
        # C++ Logic:
        # if (p.reanim.n_repeated > 0 && p.reanim.type != reanim_type::repeat) {
        #     p.set_reanim_frame(plant_reanim_name::anim_loop);
        #     p.reanim.type = reanim_type::repeat;
        # }

        if plant.reanimate.n_repeated > 0 and plant.reanimate.type != ReanimateType.REPEAT:
            plant.set_reanim_frame(PlantReanimName.anim_loop)
            plant.reanimate.type = ReanimateType.REPEAT
            plant.reanimate.n_repeated = 0

        # C++ Logic:
        # if (p.status != plant_status::work && p.countdown.effect == 0) {
        #     damage(scene).activate_plant(p);
        # }

        if plant.status != PlantStatus.WORK and plant.countdown.effect == 0:
            self.damage_system.activate_plant(plant)
