from pvzemu2.enums import PlantStatus, PlantReanimName
from pvzemu2.objects.base import ReanimateType
from pvzemu2.objects.plant import Plant
from pvzemu2.systems.plant_subsystems.base import PlantSubsystem


class CobCannonSubsystem(PlantSubsystem):
    def update(self, plant: Plant) -> None:
        if plant.status == PlantStatus.COB_CANNON_UNARMED_IDLE:
            if plant.countdown.status == 0:
                plant.status = PlantStatus.COB_CANNON_CHARGE

                plant.set_reanim_frame(PlantReanimName.anim_charge)
                plant.reanimate.type = ReanimateType.ONCE
                plant.reanimate.fps = 12.0
                plant.reanimate.n_repeated = 0

        elif plant.status == PlantStatus.COB_CANNON_CHARGE:
            if plant.reanimate.n_repeated > 0:
                plant.status = PlantStatus.COB_CANNON_ARMED_IDLE

                plant.set_reanim_frame(PlantReanimName.anim_idle)
                plant.reanimate.type = ReanimateType.REPEAT
                plant.reanimate.fps = 12.0
                plant.reanimate.n_repeated = 0

    def launch(self, plant: Plant, x: int, y: int) -> bool:
        if plant.status != PlantStatus.COB_CANNON_ARMED_IDLE:
            return False

        plant.status = PlantStatus.COB_CANNON_LAUNCH
        plant.countdown.launch = 206

        plant.set_reanim_frame(PlantReanimName.anim_shooting)
        plant.reanimate.type = ReanimateType.ONCE
        plant.reanimate.fps = 12.0
        plant.reanimate.n_repeated = 0

        plant.cannon_x = int(x - 47.0)
        plant.cannon_y = y

        return True
