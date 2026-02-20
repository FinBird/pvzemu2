from pvzemu2.enums import GridItemType
from pvzemu2.scene import Scene
from pvzemu2.systems.griditem_factory import GridItemFactory


class GridItemSystem:
    def __init__(self, scene: Scene, griditem_factory: GridItemFactory) -> None:
        self.scene = scene
        self.griditem_factory = griditem_factory

    def update(self) -> None:
        for item in self.scene.grid_items:
            if item.type == GridItemType.GRAVE:
                # 墓碑的倒计时增加（用于冒出动画等逻辑）
                if item.countdown < 100:
                    item.countdown += 1
            elif item.type == GridItemType.CRATER:
                # 弹坑的倒计时衰减，归零时恢复成正常土地
                if item.countdown > 0:
                    item.countdown -= 1
                    if item.countdown == 0:
                        self.griditem_factory.destroy(item)
