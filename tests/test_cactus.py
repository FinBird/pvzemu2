import unittest

from pvzemu2.enums import PlantType, PlantStatus, ZombieType, ZombieStatus, SceneType
from pvzemu2.objects.base import ReanimateType
from pvzemu2.scene import Scene
from pvzemu2.systems.damage import DamageSystem
from pvzemu2.systems.plant_factory import PlantFactory
from pvzemu2.systems.plant_system import PlantSystem
from pvzemu2.systems.projectile_factory import ProjectileFactory
from pvzemu2.systems.zombie_factory import ZombieFactory


class TestCactus(unittest.TestCase):
    def setUp(self):
        self.scene = Scene(SceneType.DAY)
        self.plant_factory = PlantFactory(self.scene)
        self.zombie_factory = ZombieFactory(self.scene)
        self.damage_system = DamageSystem(self.scene)
        self.projectile_factory = ProjectileFactory(self.scene)
        self.plant_system = PlantSystem(self.scene, self.projectile_factory, self.damage_system, self.plant_factory)

    def _move_zombie_to_row(self, zombie, row):
        """Helper to properly move a zombie to a row and update spatial cache"""
        if 0 <= zombie.row < len(self.scene.zombies_by_row):
            self.scene.zombies_by_row[zombie.row].discard(zombie.id)
        zombie.row = row
        self.scene.zombies_by_row[row].add(zombie.id)

    def test_cactus_initial_state(self):
        cactus = self.plant_factory.create(PlantType.CACTUS, 2, 2)
        self.assertEqual(cactus.status, PlantStatus.CACTUS_SHORT_IDLE)

    def test_cactus_grows_for_balloon(self):
        cactus = self.plant_factory.create(PlantType.CACTUS, 2, 2)

        balloon = self.zombie_factory.create(ZombieType.BALLOON)
        self._move_zombie_to_row(balloon, 2)
        balloon.x = 800.0
        balloon.int_x = 800

        # Manually set balloon status to flying as create might default to walking/spawning
        balloon.status = ZombieStatus.BALLOON_FLYING

        # Update plant system
        self.plant_system.update()

        # Cactus should transition to GROW_TALL
        self.assertEqual(cactus.status, PlantStatus.CACTUS_GROW_TALL)
        self.assertEqual(cactus.reanimate.type, ReanimateType.ONCE)

        # Simulate animation completion
        cactus.reanimate.n_repeated = 1
        self.plant_system.update()

        # Should be TALL_IDLE
        self.assertEqual(cactus.status, PlantStatus.CACTUS_TALL_IDLE)
        self.assertEqual(cactus.reanimate.type, ReanimateType.REPEAT)

    def test_cactus_shrinks_when_no_balloon(self):
        cactus = self.plant_factory.create(PlantType.CACTUS, 2, 2)
        cactus.status = PlantStatus.CACTUS_TALL_IDLE  # Force tall

        # No balloon zombies
        self.plant_system.update()

        # Should transition to GET_SHORT
        self.assertEqual(cactus.status, PlantStatus.CACTUS_GET_SHORT)
        self.assertEqual(cactus.reanimate.type, ReanimateType.ONCE)

        # Simulate animation completion
        cactus.reanimate.n_repeated = 1
        self.plant_system.update()

        # Should be SHORT_IDLE
        self.assertEqual(cactus.status, PlantStatus.CACTUS_SHORT_IDLE)

    def test_cactus_ignores_ground_zombies_for_growth(self):
        cactus = self.plant_factory.create(PlantType.CACTUS, 2, 2)
        zombie = self.zombie_factory.create(ZombieType.ZOMBIE)
        self._move_zombie_to_row(zombie, 2)
        zombie.x = 800.0
        zombie.int_x = 800

        self.plant_system.update()

        # Should remain SHORT_IDLE
        self.assertEqual(cactus.status, PlantStatus.CACTUS_SHORT_IDLE)

    def test_cactus_shoots_ground_zombies(self):
        cactus = self.plant_factory.create(PlantType.CACTUS, 2, 2)
        zombie = self.zombie_factory.create(ZombieType.ZOMBIE)
        self._move_zombie_to_row(zombie, 2)
        zombie.x = 400.0  # Closer (col ~5)
        zombie.int_x = 400

        # Force can_attack to trigger _update_attack
        cactus.can_attack = True
        cactus.countdown.generate = 0  # Ready to attack

        self.plant_system.update()

        # Should have set launch countdown
        self.assertEqual(cactus.countdown.launch, 35)
        # Should NOT grow tall
        self.assertEqual(cactus.status, PlantStatus.CACTUS_SHORT_IDLE)

    def test_cactus_shrinks_when_no_balloon_simple(self):
        cactus = self.plant_factory.create(PlantType.CACTUS, 2, 2)
        cactus.status = PlantStatus.CACTUS_TALL_IDLE  # Force tall
        # No balloon zombies
        self.plant_system.update()
        self.assertEqual(cactus.status, PlantStatus.CACTUS_GET_SHORT)

    def test_cactus_grows_for_balloon_simple(self):
        cactus = self.plant_factory.create(PlantType.CACTUS, 2, 2)
        cactus.status = PlantStatus.CACTUS_SHORT_IDLE
        balloon = self.zombie_factory.create(ZombieType.BALLOON)
        self._move_zombie_to_row(balloon, 2)
        balloon.x = 800.0
        balloon.int_x = 800
        balloon.status = ZombieStatus.BALLOON_FLYING
        self.plant_system.update()
        self.assertEqual(cactus.status, PlantStatus.CACTUS_GROW_TALL)
