from pvzemu2.enums import PlantType
from pvzemu2.objects.plant import Plant
from pvzemu2.systems.plant_subsystems.base import PlantSubsystem


class SunPlantsSubsystem(PlantSubsystem):
    def update(self, p: Plant) -> None:
        amount = 25 if p.type == PlantType.SUNFLOWER else 50

        if self.scene.spawn.countdown_endgame > 0:
            return

        self.scene.sun.sun = min(9990, self.scene.sun.sun + amount)
        # 核心更新：产出后重置生产计时器
        p.countdown.generate = self.rng.randint(151) + 2350
