import unittest

from pvzemu2.enums import PlantType, PlantStatus
from pvzemu2.scene import Scene
from pvzemu2.systems.damage import DamageSystem
from pvzemu2.systems.plant_factory import PlantFactory
from pvzemu2.systems.plant_system import PlantSystem
from pvzemu2.systems.projectile_factory import ProjectileFactory


class TestImitater(unittest.TestCase):
    def setUp(self):
        self.scene = Scene()
        self.plant_factory = PlantFactory(self.scene)
        self.projectile_factory = ProjectileFactory(self.scene)
        self.damage_system = DamageSystem(self.scene)
        self.plant_system = PlantSystem(self.scene, self.projectile_factory, self.damage_system, self.plant_factory)

    def test_imitater_transformation(self):
        # Create an Imitater imitating a Peashooter
        imitater = self.plant_factory.create(PlantType.IMITATER, 2, 2, imitater_target=PlantType.PEA_SHOOTER)

        self.assertEqual(imitater.type, PlantType.IMITATER)
        self.assertEqual(imitater.imitater_target, PlantType.PEA_SHOOTER)
        self.assertEqual(imitater.status, PlantStatus.IDLE)
        self.assertEqual(imitater.countdown.status, 30)

        # Update until transformation starts
        for _ in range(30):
            self.plant_system.update()

        self.assertEqual(imitater.status, PlantStatus.IMITATER_MORPHING)
        self.assertEqual(imitater.countdown.effect, 19)

        # Update until transformation completes
        for _ in range(20):
            self.plant_system.update()

        # The imitater should be destroyed and replaced by a Peashooter
        self.assertTrue(imitater.is_dead)

        # Check if a Peashooter exists at the same location
        plants_at_loc = [p for p in self.scene.plants if p.row == 2 and p.col == 2 and not p.is_dead]
        self.assertEqual(len(plants_at_loc), 1)
        new_plant = plants_at_loc[0]
        self.assertEqual(new_plant.type, PlantType.PEA_SHOOTER)


if __name__ == '__main__':
    unittest.main()
