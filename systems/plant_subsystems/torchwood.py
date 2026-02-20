from pvzemu2.objects.plant import Plant
from pvzemu2.systems.plant_subsystems.base import PlantSubsystem


class TorchwoodSubsystem(PlantSubsystem):
    def update(self, p: Plant) -> None:
        # Torchwood logic (lighting peas) is primarily handled in ProjectileSystem._is_in_torchwood.
        # This subsystem can handle animation updates or other state management if needed.
        pass
