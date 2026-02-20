from pvzemu2.enums import PlantType
from pvzemu2.objects.plant import Plant
from pvzemu2.systems.plant_subsystems.base import PlantSubsystem


class SunPlantsSubsystem(PlantSubsystem):
    def update(self, p: Plant) -> None:
        amount = 25 if p.type == PlantType.SUNFLOWER else 50
        if self.scene.spawn.countdown_endgame > 0:
            return

        # 产出阳光
        self.scene.sun.sun = min(9990, self.scene.sun.sun + amount)

        # 对应 C++: RandRangeInt(2500 - 150, 2500)
        p.countdown.generate = self.rng.randint(151) + 2350
