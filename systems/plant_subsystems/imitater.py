from pvzemu2.enums import PlantStatus
from pvzemu2.objects.plant import Plant
from pvzemu2.systems.plant_factory import PlantFactory
from pvzemu2.systems.plant_subsystems.base import PlantSubsystem


class ImitaterSubsystem(PlantSubsystem):
    def update(self, plant: Plant) -> None:
        if plant.status == PlantStatus.IMITATER_MORPHING:
            # When effect countdown reaches 0, the transformation is complete
            if plant.countdown.effect == 0:
                target_type = plant.imitater_target
                row = plant.row
                col = plant.col

                # Create a new factory instance to handle destruction and creation
                factory = PlantFactory(self.scene)

                # Destroy the Imitater plant
                factory.destroy(plant)

                # Create the target plant at the same location
                # Note: create() updates the plant_map, so the new plant will take the spot
                factory.create(target_type, row, col)

        # Initial countdown to start transformation
        elif plant.countdown.status == 0:
            plant.status = PlantStatus.IMITATER_MORPHING
            plant.countdown.effect = 20  # Approx frames for transformation animation
