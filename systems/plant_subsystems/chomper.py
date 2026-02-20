from typing import Optional,TYPE_CHECKING

from pvzemu2.enums import PlantStatus, ZombieStatus, ZombieType, AttackFlags, PlantReanimName
from pvzemu2.geometry import Rect
from pvzemu2.objects.base import ReanimateType

if TYPE_CHECKING:
    from pvzemu2.objects.plant import Plant
    from pvzemu2.objects.zombie import Zombie
from pvzemu2.systems.plant_subsystems.base import PlantSubsystem


class ChomperSubsystem(PlantSubsystem):
    def update(self, plant: 'Plant') -> None:
        if plant.status == PlantStatus.WAIT:
            target = self.find_target(plant, plant.row)
            if target:
                plant.set_reanim(PlantReanimName.anim_bite, ReanimateType.ONCE, 24.0)
                plant.status = PlantStatus.CHOMPER_BITE_BEGIN
                plant.countdown.status = 70

        elif plant.status == PlantStatus.CHOMPER_BITE_BEGIN:
            if plant.countdown.status == 0:
                self._attempt_bite(plant)

        elif plant.status == PlantStatus.CHOMPER_BITE_SUCCESS:
            if plant.reanimate.n_repeated > 0:
                plant.set_reanim(PlantReanimName.anim_chew, ReanimateType.REPEAT, 15.0)
                plant.status = PlantStatus.CHOMPER_CHEW
                plant.countdown.status = 4000

        elif plant.status == PlantStatus.CHOMPER_CHEW:
            if plant.countdown.status == 0:
                plant.set_reanim(PlantReanimName.anim_swallow, ReanimateType.ONCE, 12.0)
                plant.status = PlantStatus.CHOMPER_SWALLOW

        elif plant.status in (PlantStatus.CHOMPER_SWALLOW, PlantStatus.CHOMPER_BITE_FAIL):
            if plant.reanimate.n_repeated > 0:
                plant.set_reanim(PlantReanimName.anim_idle, ReanimateType.REPEAT, 12.0)
                plant.status = PlantStatus.WAIT

    def _is_bouncing_pogo(self, z: 'Zombie') -> bool:
        return ZombieStatus.POGO_WITH_STICK <= z.status <= ZombieStatus.POGO_JUMP_ACROSS

    def _attempt_bite(self, plant: 'Plant') -> None:
        target = self.find_target(plant, plant.row)

        do_bite = False
        do_miss = False

        if target:
            if target.type in (ZombieType.GARGANTUAR, ZombieType.GIGA_GARGANTUAR, ZombieType.ZOMBIE_BOSS):
                do_bite = True

            is_immobilized = target.countdown.freeze > 0 or target.countdown.butter > 0
            if not is_immobilized:
                if self._is_bouncing_pogo(target) or target.status in (
                        ZombieStatus.POLE_VALUTING_JUMPING, ZombieStatus.POLE_VALUTING_RUNNING):
                    do_miss = True
        else:
            do_miss = True

        if do_bite and target:
            self.damage_system.take(target, 40, 0)
            plant.status = PlantStatus.CHOMPER_BITE_FAIL
        elif do_miss:
            plant.status = PlantStatus.CHOMPER_BITE_FAIL
        elif target:
            self.damage_system.zombie_factory.destroy(target)
            plant.status = PlantStatus.CHOMPER_BITE_SUCCESS

    def find_target(self, plant: 'Plant', row: int, is_alt_attack: bool = False) -> Optional['Zombie']:
        # get_attack_box() 返回的已经是基于当前大嘴花 x, y 的绝对坐标
        abs_attack_rect = plant.get_attack_box()

        extra_range = 60 if plant.status == PlantStatus.CHOMPER_BITE_BEGIN else 0
        best_target = None
        min_x = 99999

        candidates = []
        if 0 <= row < len(self.scene.zombies_by_row):
            candidates = list(self.scene.zombies_by_row[row])

        for z_id in candidates:
            z = self.scene.zombies.get(z_id)
            if z is None or z.is_dead:
                continue

            if not self.damage_system.can_be_attacked(z, AttackFlags.GROUND):
                continue

            if self._is_bouncing_pogo(z) or (z.type == ZombieType.BUNGEE and z.bungee_col == plant.col):
                continue

            current_extra_range = extra_range
            if z.is_eating:
                current_extra_range = max(current_extra_range, 60)

            zr = z.get_hit_box_rect()

            # 对于地底行走的矿工，攻击框有所限制
            temp_attack_rect = Rect(abs_attack_rect.x, abs_attack_rect.y, abs_attack_rect.width, abs_attack_rect.height)
            if z.status == ZombieStatus.DIGGER_WALK_RIGHT:
                temp_attack_rect.x += 20
                temp_attack_rect.width -= 20

            overlap = temp_attack_rect.get_overlap_len(zr)

            if overlap >= -current_extra_range:
                # 寻找最靠前（最左边，x最小）的僵尸
                if z.int_x < min_x:
                    min_x = z.int_x
                    best_target = z

        return best_target
