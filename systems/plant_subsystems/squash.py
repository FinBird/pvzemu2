from typing import Optional

from pvzemu2.enums import PlantStatus, ZombieStatus, AttackFlags, DamageFlags, ZombieType
from pvzemu2.objects.plant import Plant
from pvzemu2.objects.zombie import Zombie
from pvzemu2.systems.plant_subsystems.base import PlantSubsystem


class SquashSubsystem(PlantSubsystem):
    def update(self, plant: Plant) -> None:
        # Initial check for idle state to find target
        if plant.status == PlantStatus.IDLE:
            target = self.find_target(plant, plant.row)
            if target:
                # plant.target = target.id # TODO: Need to store target ref/id? C++ stores index

                zr = target.get_hit_box_rect()
                plant.cannon_x = zr.x + zr.width // 2 - plant.attack_box.width // 2

                plant.status = PlantStatus.SQUASH_LOOK
                plant.countdown.status = 45  # C++ says 45 in look? No wait, C++ says 80 in idle->look transition

                # In C++:
                # p.status = plant_status::squash_look;
                # p.countdown.status = 80; (Wait, I misread the C++ code in previous turn?)
                # Let's re-read the C++ snippet carefully from memory/history.
                # idle -> look: status=80. 
                # look -> jump_up: if status==0.

                plant.countdown.status = 80

                # Animation handling would go here (look left/right)
                # if plant.cannon_x >= plant.x: look right else look left
                return

        # State machine
        if plant.status == PlantStatus.SQUASH_LOOK:
            if plant.countdown.status == 0:
                # Trigger jump up
                # p.set_reanim(plant_reanim_name::anim_jumpup, reanim_type::once, 24);
                plant.status = PlantStatus.SQUASH_JUMP_UP
                plant.countdown.status = 45  # C++ says 45

        elif plant.status == PlantStatus.SQUASH_JUMP_UP:
            if plant.countdown.status == 0:
                # Find target again to refine landing
                target = self.find_target(plant, plant.row)
                if target:
                    # Predict position
                    # zombie_base(scene).predict_after(*z, 30)
                    # Simple prediction: x + dx * 30
                    predicted_x = target.x + target.dx * 30
                    plant.cannon_x = int(predicted_x - plant.attack_box.width / 2)

                plant.status = PlantStatus.SQUASH_STOP_IN_THE_AIR
                plant.countdown.status = 50

                # Detach from grid?
                # if (scene.plant_map[p.row][p.col].content == &p) { scene.plant_map[p.row][p.col].content = nullptr; }
                # In Python we might need a way to tell the world/scene to clear the grid cell

        elif plant.status == PlantStatus.SQUASH_STOP_IN_THE_AIR:
            # Interpolate position
            # p.x = get_jump_up_pos(p, get_x_by_col(p.col), p.cannon.x);
            # p.y = get_jump_up_pos(p, get_y_by_row_and_col(scene.type, p.row, p.col), y - 120);

            # We need start x,y. 
            # start_x = 80 * col + 40 (approx center of col) or plant's original x?
            # C++ uses get_x_by_col(p.col) which is usually col * 80 + 40?
            start_x = plant.col * 80 + 40  # Simplified
            # start_y = plant.row * 100 + ... 
            start_y = plant.row * 100 + 80  # Simplified

            target_y = start_y - 120  # Jump height

            plant.x = self._get_jump_up_pos(plant.countdown.status, start_x, plant.cannon_x)
            plant.y = self._get_jump_up_pos(plant.countdown.status, start_y, target_y)

            if plant.countdown.status == 0:
                # p.set_reanim(plant_reanim_name::anim_jumpdown, reanim_type::once, 60);
                plant.status = PlantStatus.SQUASH_JUMP_DOWN
                plant.countdown.status = 10

        elif plant.status == PlantStatus.SQUASH_JUMP_DOWN:
            # p.y = static_cast<int>(round(120.0 * (10.0 - p.countdown.status) / 10.0 + y - 120));
            # falling down
            # y is ground level
            ground_y = plant.row * 100 + 80  # Simplified
            start_fall_y = ground_y - 120

            plant.y = int(120.0 * (10.0 - plant.countdown.status) / 10.0 + start_fall_y)

            if plant.countdown.status == 5:
                self._kill(plant)
            elif plant.countdown.status == 0:
                # Check water?
                # if scene.is_water_grid...

                plant.status = PlantStatus.SQUASH_CRUSHED
                plant.countdown.status = 100

        elif plant.status == PlantStatus.SQUASH_CRUSHED:
            if plant.countdown.status == 0:
                plant.hp = -1  # Trigger destroy in system

    def _get_jump_up_pos(self, countdown_status: int, a: int, b: int) -> int:
        # float r = (50 - p.countdown.status) / 30.0f;
        # Wait, C++ logic: 
        # r = (50 - status) / 30.0
        # Wait, loop goes from 50 down to 0? 
        # In SQUASH_STOP_IN_THE_AIR, status starts at 50.
        # So r goes from 0 to 1.66?
        # If r > 1 return b.
        # So it moves for the first 30 frames (50->20), then stays at b for 20 frames (20->0)?

        r = (50 - countdown_status) / 30.0

        if r <= 0:
            return a
        elif r > 1:
            return b
        else:
            # Smooth step?
            # r = 3 * pow(r, 2) - 2 * pow(r, 3);
            # r = 3 * pow(r, 2) - 2 * pow(r, 3);
            r = 3 * r ** 2 - 2 * r ** 3
            r = 3 * r ** 2 - 2 * r ** 3
            return int(round((b - a) * r + a))

    def _kill(self, plant: Plant) -> None:
        # Damage logic
        # Area attack
        # C++: p.get_attack_box(pr)
        # Squash attack box is usually small around it?
        # But here we should use the plant's current position (which moved to target)

        # In C++ kill() uses p.get_attack_box(pr) which uses p.x, p.y.
        # Since p.x, p.y moved, it attacks where it landed.

        abs_attack_rect = plant.get_attack_box()

        # Spatial optimization: only iterate zombies in the same row
        candidates = []
        if 0 <= plant.row < len(self.scene.zombies_by_row):
            candidates = list(self.scene.zombies_by_row[plant.row])

        # Check overlap with zombies
        for z_id in candidates:
            z = self.scene.zombies.get(z_id)
            if z is None: continue

            if z.is_dead: continue
            # Row check implicit

            if not self.damage_system.can_be_attacked(z, AttackFlags.GROUND):  # Default flags
                continue

            zr = z.get_hit_box_rect()

            if abs_attack_rect.get_overlap_len(zr) > (-20 if z.type == ZombieType.FOOTBALL else 0):
                self.damage_system.take(z, 1800, DamageFlags.NO_LEAVE_BODY | DamageFlags.DAMAGE_HITS_SHIELD_AND_BODY)

    def find_target(self, plant: Plant, row: int, is_alt_attack: bool = False) -> Optional[Zombie]:
        # Squash looks left and right
        # Range is approx 1.5 grid?
        # C++ logic:
        # int d = z.is_eating ? 110 : 70;
        # if (-pr.get_overlap_len(zr) > d) continue;

        # Simplified: Check zombies in range [plant.x - range, plant.x + range]

        abs_attack_rect = plant.get_attack_box()

        best_target = None
        min_dist = 99999

        # Spatial optimization: only iterate zombies in the same row
        candidates = []
        if 0 <= row < len(self.scene.zombies_by_row):
            candidates = list(self.scene.zombies_by_row[row])

        for z_id in candidates:
            z = self.scene.zombies.get(z_id)
            if z is None: continue

            if z.is_dead: continue

            if z.status in (
            ZombieStatus.POLE_VALUTING_JUMPING, ZombieStatus.DOLPHIN_JUMP_IN_POOL, ZombieStatus.DOLPHIN_RIDE):
                continue

            zr = z.get_hit_box_rect()
            dist = -abs_attack_rect.get_overlap_len(zr)

            if dist <= (110 if z.is_eating else 70):
                if dist < min_dist:
                    min_dist = dist
                    best_target = z

        return best_target
