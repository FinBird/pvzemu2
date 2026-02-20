from pvzemu2.enums import PlantType
from pvzemu2.objects.plant import Plant
from pvzemu2.systems.plant_subsystems.base import PlantSubsystem


class ShieldPlantsSubsystem(PlantSubsystem):
    def update(self, p: Plant) -> None:
        if p.type == PlantType.WALLNUT:
            self._update_wallnut(p)
        elif p.type == PlantType.TALLNUT:
            self._update_tallnut(p)
        elif p.type == PlantType.PUMPKIN:
            self._update_pumpkin(p)

    def _update_wallnut(self, p: Plant) -> None:
        # Thresholds: 1/3 and 2/3 of max HP (4000)
        # 1333 and 2666
        if p.hp < 1333:
            # Cracked 2
            # Assuming status or reanim frame sets this.
            # In some implementations, status changes.
            pass
        elif p.hp < 2666:
            # Cracked 1
            pass

        # TODO: Implement reanim state changes based on HP.
        # Currently, the reanimation data for damaged states (e.g., cracked Wall-nut)
        # is missing from the ported data sources.
        pass

    def _update_tallnut(self, p: Plant) -> None:
        # Thresholds: 1/3 and 2/3 of max HP (8000)
        # 2666 and 5333
        pass

    def _update_pumpkin(self, p: Plant) -> None:
        # Thresholds: 1/3 and 2/3 of max HP (4000)
        pass
