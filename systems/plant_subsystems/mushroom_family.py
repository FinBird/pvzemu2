import math
from typing import Optional

from pvzemu2.enums import PlantType, PlantStatus, ZombieType, ZombieStatus, ZombieAccessoriesType2, GridItemType, \
    ZombieAction, PlantReanimName
from pvzemu2.objects.base import ReanimateType
from pvzemu2.objects.plant import Plant
from pvzemu2.objects.zombie import Zombie
from pvzemu2.systems.plant_subsystems.base import PlantSubsystem


class MushroomFamilySubsystem(PlantSubsystem):
    def update(self, p: Plant) -> None:
        if p.type == PlantType.DOOMSHROOM:
            self._update_doomshroom(p)
        elif p.type == PlantType.SUNSHROOM:
            self._update_sunshroom(p)
        elif p.type == PlantType.ICESHROOM:
            self._update_iceshroom(p)
        elif p.type == PlantType.MAGNETSHROOM:
            self._update_magnetshroom(p)
        elif p.type == PlantType.SCAREDYSHROOM:
            self._update_scaredyshroom(p)

    def _update_doomshroom(self, p: Plant) -> None:
        if p.is_sleeping or p.status == PlantStatus.WORK:
            return

        p.status = PlantStatus.WORK
        p.countdown.effect = 100
        p.set_reanim_frame(PlantReanimName.anim_explode)
        p.reanimate.fps = 23
        p.reanimate.type = ReanimateType.ONCE

    def _update_sunshroom(self, p: Plant) -> None:
        if p.is_sleeping:
            return

        if p.status == PlantStatus.SUNSHROOM_SMALL:
            if p.countdown.status <= 0:
                p.set_reanim_frame(PlantReanimName.anim_grow)
                p.reanimate.type = ReanimateType.ONCE
                p.reanimate.fps = 12
                p.status = PlantStatus.SUNSHROOM_GROW

        elif p.status == PlantStatus.SUNSHROOM_GROW:
            if p.reanimate.n_repeated > 0:
                p.set_reanim_frame(PlantReanimName.anim_bigidle)
                p.reanimate.type = ReanimateType.REPEAT
                p.reanimate.fps = self.rng.randfloat(12, 15)
                p.status = PlantStatus.SUNSHROOM_BIG

    def handle_sunshroom_production(self, p: Plant) -> None:
        amount = 15 if p.status == PlantStatus.SUNSHROOM_SMALL else 25
        self.scene.sun.sun = min(9990, self.scene.sun.sun + amount)
        # 重置倒计时
        p.countdown.generate = self.rng.randint(151) + 2350

    def _update_iceshroom(self, p: Plant) -> None:
        if not p.is_sleeping and p.status != PlantStatus.WORK:
            p.status = PlantStatus.WORK
            p.countdown.effect = 100

    def _update_magnetshroom(self, p: Plant) -> None:
        if p.status == PlantStatus.MAGNETSHROOM_INACTIVE_IDLE:
            if p.countdown.status == 0:
                p.status = PlantStatus.WAIT
                p.set_reanim_frame(PlantReanimName.anim_idle)
                p.reanimate.type = ReanimateType.REPEAT
                p.reanimate.fps = self.rng.randfloat(10, 15)
            return
        elif p.status == PlantStatus.MAGNETSHROOM_WORKING:
            if p.reanimate.n_repeated > 0:
                p.set_reanim_frame(PlantReanimName.anim_nonactive_idle2)
                p.reanimate.type = ReanimateType.REPEAT
                p.reanimate.fps = 2
                p.status = PlantStatus.MAGNETSHROOM_INACTIVE_IDLE
            return

        if self._magnet_attack_zombie(p):
            return

        self._magnet_attack_ladder(p)

    def _magnet_attack_zombie(self, p: Plant) -> bool:
        target: Optional[Zombie] = None
        min_dist = float('inf')

        for z in self.scene.zombies:
            row_diff = abs(p.row - z.row)

            # Basic checks
            if (z.is_hypno or
                    not z.is_not_dying or
                    z.action != ZombieAction.NONE or
                    z.status == ZombieStatus.RISING_FROM_GROUND or
                    z.is_dead or
                    z.x > 800 or
                    row_diff > 2):
                continue

            if (z.status in (ZombieStatus.DIGGER_DIG, ZombieStatus.DIGGER_DIZZY, ZombieStatus.DIGGER_WALK_RIGHT) or
                    z.type == ZombieType.POGO):
                if not z.has_item_or_walk_left:
                    continue
            else:
                # Check accessories
                # Note: Accessory 1 (Bucket, Football) is handled by Type check in absence of accessory_1 field
                is_bucket = z.type == ZombieType.BUCKET_HEAD
                is_football = z.type == ZombieType.FOOTBALL

                is_screen = z.accessory_2_type == ZombieAccessoriesType2.SCREEN_DOOR
                is_ladder = z.accessory_2_type == ZombieAccessoriesType2.LADDER
                is_jack = z.type == ZombieType.JACK_IN_THE_BOX

                if not (is_bucket or is_football or is_screen or is_ladder or is_jack):
                    continue

            # Range check: circle overlap
            # p (x, y) vs z circle (x, y, radius)
            # z.hit_box is relative. z.x, z.y are coordinates.
            # C++: zr.is_overlap_with_circle(p.x, p.y, z.is_eating ? 320 : 270)

            range_radius = 320 if z.is_eating else 270

            # Simple distance check
            dx = p.x - z.x
            dy = p.y - z.y
            dist_sq = dx * dx + dy * dy
            if dist_sq <= range_radius * range_radius:
                # Weighted distance
                d = math.sqrt(dist_sq) + row_diff * 80
                if target is None or d < min_dist:
                    target = z
                    min_dist = d

        if target is None:
            return False

        p.status = PlantStatus.MAGNETSHROOM_WORKING
        p.countdown.status = 1500
        p.set_reanim_frame(PlantReanimName.anim_shooting)
        p.reanimate.type = ReanimateType.ONCE
        p.reanimate.fps = 12

        # Apply effect
        if target.type == ZombieType.BUCKET_HEAD:
            target.type = ZombieType.ZOMBIE
            target.hp = min(target.hp, 270)  # Reset HP to normal zombie max
            target.max_hp = 270
        elif target.type == ZombieType.FOOTBALL:
            target.type = ZombieType.ZOMBIE
            target.hp = min(target.hp, 270)
            target.max_hp = 270
        elif target.accessory_2_type in (ZombieAccessoriesType2.SCREEN_DOOR, ZombieAccessoriesType2.LADDER):
            # damage(scene).destroy_accessory_2(*target)
            target.accessory_2_type = ZombieAccessoriesType2.NONE
            target.accessory_2_hp = 0
            target.status = ZombieStatus.WALKING
            # if (!target->is_eating) reanim(scene).update_status(*target);
        elif target.type == ZombieType.POGO:
            # zombie_pogo(scene).remove_stick(*target)
            target.has_item_or_walk_left = False  # Remove stick
            target.status = ZombieStatus.POGO_JUMP_ACROSS  # Or similar? logic to transition to normal jump/walk
        elif target.status == ZombieStatus.JACKBOX_WALKING:
            # reanim(scene).update_dx(*target)
            target.status = ZombieStatus.WALKING
        elif target.type == ZombieType.DIGGER:
            if target.status == ZombieStatus.DIGGER_DIG:
                target.status = ZombieStatus.DIGGER_LOST_DIG
                target.countdown.action = 200
                # reanim.set_fps(*target, 0)
            target.has_item_or_walk_left = False

        return True

    def _magnet_attack_ladder(self, p: Plant) -> None:
        target_item = None
        min_dist = float('inf')

        for item in self.scene.grid_items:
            if item.type == GridItemType.LADDER:
                d1 = abs(item.col - p.col)  # Assuming griditem has col/row
                d2 = abs(item.row - p.row)

                if max(d1, d2) <= 2:
                    d = d1 * 0.05 + max(d1, d2)
                    if target_item is None or d < min_dist:
                        target_item = item
                        min_dist = d

        if target_item:
            p.status = PlantStatus.MAGNETSHROOM_WORKING
            p.countdown.status = 1500

            # griditem_factory(scene).destroy(*target)
            # Since we don't have direct access to factory destroy, we might need to remove from list manually
            # or use a method if available. 
            # Assuming scene.grid_items is the list
            if target_item in self.scene.grid_items:
                self.scene.grid_items.remove(target_item.id)

    def _update_scaredyshroom(self, p: Plant) -> None:
        if p.countdown.launch > 0:
            return

        found_scared = False
        for z in self.scene.zombies:
            diff = abs(p.row - z.row)
            if not z.is_hypno and not z.is_dead and diff <= 1:  # check death status?
                # zr.is_overlap_with_circle(p.x, p.y + 20, 120)
                dx = p.x - z.x
                dy = (p.y + 20) - z.y
                if dx * dx + dy * dy <= 120 * 120:
                    found_scared = True
                    break

        if p.status == PlantStatus.WAIT:
            if found_scared:
                p.status = PlantStatus.SCAREDYSHROOM_SCARED
                p.set_reanim_frame(PlantReanimName.anim_scared)
                p.reanimate.type = ReanimateType.ONCE
                p.reanimate.fps = 12  # Guessing FPS
        elif p.status == PlantStatus.SCAREDYSHROOM_SCARED:
            if p.reanimate.n_repeated > 0:
                p.status = PlantStatus.SCAREDYSHROOM_SCARED_IDLE
                p.set_reanim_frame(PlantReanimName.anim_scaredidle)
                p.reanimate.type = ReanimateType.REPEAT
                p.reanimate.fps = 12
        elif p.status == PlantStatus.SCAREDYSHROOM_SCARED_IDLE:
            if not found_scared:
                p.status = PlantStatus.SCAREDYSHROOM_GROW
                p.set_reanim_frame(PlantReanimName.anim_grow)
                p.reanimate.type = ReanimateType.ONCE
                p.reanimate.fps = 12
        elif p.status == PlantStatus.SCAREDYSHROOM_GROW:
            if p.reanimate.n_repeated > 0:
                p.status = PlantStatus.WAIT
                p.set_reanim_frame(PlantReanimName.anim_idle)
                p.reanimate.type = ReanimateType.REPEAT
                p.reanimate.fps = 12

        if p.status != PlantStatus.WAIT:
            p.countdown.generate = p.max_boot_delay  # prevent attack while scared/transitioning


class HypnoShroomSubsystem(PlantSubsystem):
    def update(self, plant: Plant) -> None:
        pass  # 真的什么都不用做
