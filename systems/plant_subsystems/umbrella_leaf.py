from pvzemu2.enums import PlantStatus
from pvzemu2.objects.plant import Plant
from pvzemu2.systems.plant_subsystems.base import PlantSubsystem


class UmbrellaLeafSubsystem(PlantSubsystem):
    def update(self, p: Plant) -> None:
        if p.status == PlantStatus.UMBRELLA_LEAF_BLOCK:
            # Animation duration handling
            # Assuming countdown.status is used for animation timer
            if p.countdown.status == 0:
                p.status = PlantStatus.UMBRELLA_LEAF_SHRINK
                p.countdown.status = 50  # Example duration

        elif p.status == PlantStatus.UMBRELLA_LEAF_SHRINK:
            if p.countdown.status == 0:
                p.status = PlantStatus.IDLE
