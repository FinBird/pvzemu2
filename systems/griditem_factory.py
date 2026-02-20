from pvzemu2.enums import GridItemType
from pvzemu2.objects.griditem import GridItem
from pvzemu2.scene import Scene
from pvzemu2.systems.plant_factory import PlantFactory
from pvzemu2.systems.rng import RNG


class GridItemFactory:
    def __init__(self, scene: Scene) -> None:
        self.scene = scene
        self.rng = RNG(scene)

    def create(self, type: GridItemType, row: int, col: int) -> GridItem:
        # 对应 C++ griditem_factory::create
        item = GridItem(type=type, row=row, col=col)

        if type == GridItemType.GRAVE:
            # 墓碑会销毁该位置的植物
            plant_factory = PlantFactory(self.scene)
            # Safe iteration because destroy removes from list
            for p in list(self.scene.plants):
                if p.row == item.row and p.col == item.col:
                    plant_factory.destroy(p)

            item.countdown = -self.rng.randint(50)

        elif type == GridItemType.CRATER:
            item.countdown = 18000

        elif type == GridItemType.LADDER:
            item.countdown = 0

        self.scene.grid_items.add(item)
        return item

    def destroy(self, item: GridItem) -> None:
        item.is_disappeared = True
        self.scene.grid_items.remove_obj(item)
