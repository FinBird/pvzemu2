import unittest

from pvzemu2.enums import PlantType, PlantStatus, SceneType
from pvzemu2.scene import Scene
from pvzemu2.systems.damage import DamageSystem
from pvzemu2.systems.plant_factory import PlantFactory
from pvzemu2.systems.plant_system import PlantSystem
from pvzemu2.systems.projectile_factory import ProjectileFactory


class TestCoffeeBean(unittest.TestCase):
    def setUp(self):
        self.scene = Scene(SceneType.DAY)
        self.plant_factory = PlantFactory(self.scene)
        self.damage_system = DamageSystem(self.scene)
        self.projectile_factory = ProjectileFactory(self.scene)
        self.plant_system = PlantSystem(self.scene, self.projectile_factory, self.damage_system, self.plant_factory)

    def test_coffee_bean_wakes_up_mushroom(self):
        # Create a sleeping mushroom (e.g. Scaredy-shroom during day)
        mushroom = self.plant_factory.create(PlantType.SCAREDYSHROOM, 2, 2)
        mushroom.is_sleeping = True

        # Plant Coffee Bean on top
        coffee_bean = self.plant_factory.create(PlantType.COFFEE_BEAN, 2, 2)
        self.assertIsNotNone(coffee_bean)

        # Verify initial state
        self.assertEqual(coffee_bean.countdown.effect, 100)
        self.assertTrue(mushroom.is_sleeping)

        # Update loop to trigger effect
        for _ in range(101):  # 100 frames delay
            self.plant_system.update()

        # Coffee Bean should have activated
        self.assertEqual(coffee_bean.status, PlantStatus.WORK)
        self.assertEqual(coffee_bean.countdown.effect, 0)

        # Mushroom should be waking up (countdown set)
        self.assertEqual(mushroom.countdown.awake, 99)

        # Continue updating to wake up mushroom fully
        for _ in range(100):
            self.plant_system.update()

        self.assertFalse(mushroom.is_sleeping)
        self.assertEqual(mushroom.countdown.awake, 0)

        # Coffee Bean should be dead/destroyed
        # It takes countdown.dead frames to die. We set it to 50 in damage.py
        for _ in range(60):
            self.plant_system.update()

        self.assertTrue(coffee_bean.is_dead)

    def test_cannot_plant_coffee_bean_on_awake_plant(self):
        # Create an awake plant
        peashooter = self.plant_factory.create(PlantType.PEA_SHOOTER, 2, 2)
        peashooter.is_sleeping = False

        # Try to plant Coffee Bean
        can_plant = self.plant_factory.can_plant(2, 2, PlantType.COFFEE_BEAN)
        self.assertFalse(can_plant)

    def test_cannot_plant_coffee_bean_on_empty_tile(self):
        can_plant = self.plant_factory.can_plant(2, 2, PlantType.COFFEE_BEAN)
        self.assertFalse(can_plant)
