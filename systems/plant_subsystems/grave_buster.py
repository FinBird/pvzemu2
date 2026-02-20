from pvzemu2.enums import PlantStatus, GridItemType, PlantReanimName
from pvzemu2.objects.base import ReanimateType
from pvzemu2.objects.plant import Plant
from pvzemu2.systems.griditem_factory import GridItemFactory
from pvzemu2.systems.plant_factory import PlantFactory
from pvzemu2.systems.plant_subsystems.base import PlantSubsystem


class GraveBusterSubsystem(PlantSubsystem):
    def update(self, plant: Plant) -> None:
        if plant.status == PlantStatus.GRAVE_BUSTER_LAND:
            if plant.reanimate.n_repeated > 0:
                plant.set_reanim(PlantReanimName.anim_idle, ReanimateType.REPEAT, 12.0)
                plant.countdown.status = 400
                plant.status = PlantStatus.GRAVE_BUSTER_IDLE

        elif plant.status == PlantStatus.GRAVE_BUSTER_IDLE:
            if plant.countdown.status == 0:
                griditem_factory = GridItemFactory(self.scene)
                plant_factory = PlantFactory(self.scene)

                for item in self.scene.grid_items:
                    if item.col == plant.col and item.row == plant.row and item.type == GridItemType.GRAVE:
                        griditem_factory.destroy(item)
                        break

                plant_factory.destroy(plant)
