from pvzemu2.enums import PlantStatus
from pvzemu2.objects.plant import Plant
from pvzemu2.systems.plant_subsystems.base import PlantSubsystem


class CoffeeBeanSubsystem(PlantSubsystem):
    def update(self, plant: Plant) -> None:
        if plant.status == PlantStatus.WORK:
            # Simulate animation effect
            if plant.countdown.effect > 0:
                plant.countdown.effect -= 1
            else:
                plant.is_dead = True
