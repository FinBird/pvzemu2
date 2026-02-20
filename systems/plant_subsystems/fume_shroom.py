from pvzemu2.enums import DamageFlags
from pvzemu2.objects.plant import Plant
from pvzemu2.systems.plant_subsystems.base import PlantSubsystem


class FumeShroomSubsystem(PlantSubsystem):
    def update(self, plant: Plant) -> None:
        # 大喷菇的动画、倒计时均由 PlantSystem._update_attack 标准流处理
        pass

    def attack(self, plant: Plant) -> None:
        """由 PlantSystem.launch 调用"""
        # 伤害20，穿透标志位: 0x2 (HITS_SHIELD_AND_BODY)
        self.damage_system.range_attack(plant, DamageFlags.DAMAGE_HITS_SHIELD_AND_BODY)
