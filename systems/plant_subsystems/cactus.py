from pvzemu2.enums import PlantStatus, ZombieType, ZombieStatus, PlantReanimName
from pvzemu2.objects.base import ReanimateType
from pvzemu2.objects.plant import Plant
from pvzemu2.systems.plant_subsystems.base import PlantSubsystem


class CactusSubsystem(PlantSubsystem):
    def update(self, plant: Plant) -> None:
        if plant.countdown.launch > 0:
            return

        # 获取攻击标志位，用于索敌
        # 注意：C++ 中 update 里的 find_target 是为了决定是否长高 (针对气球)
        # 这里我们需要复刻 C++ 逻辑：只有发现气球时才长高，普通僵尸不长高但会攻击

        # 专门查找气球目标的逻辑 (用于状态切换)
        # 使用专门的方法查找气球僵尸
        has_balloon = self.find_balloon_target(plant)

        match plant.status:
            case PlantStatus.CACTUS_GROW_TALL if plant.reanimate.n_repeated > 0:
                plant.status = PlantStatus.CACTUS_TALL_IDLE
                plant.set_reanim_frame(PlantReanimName.anim_idlehigh)
                plant.reanimate.type = ReanimateType.REPEAT
                plant.reanimate.n_repeated = 0
                plant.countdown.generate = 1

            case PlantStatus.CACTUS_TALL_IDLE if not has_balloon:
                plant.status = PlantStatus.CACTUS_GET_SHORT
                plant.set_reanim_frame(PlantReanimName.anim_lower)
                plant.reanimate.type = ReanimateType.ONCE
                plant.reanimate.fps = 12
                plant.reanimate.n_repeated = 0

            case PlantStatus.CACTUS_GET_SHORT if plant.reanimate.n_repeated > 0:
                plant.status = PlantStatus.CACTUS_SHORT_IDLE
                plant.set_reanim_frame(PlantReanimName.anim_idle)
                plant.reanimate.type = ReanimateType.REPEAT
                plant.reanimate.n_repeated = 0

            case _:
                if has_balloon:
                    plant.status = PlantStatus.CACTUS_GROW_TALL
                    plant.set_reanim_frame(PlantReanimName.anim_rise)
                    plant.reanimate.type = ReanimateType.ONCE
                    plant.reanimate.fps = 12
                    plant.reanimate.n_repeated = 0

    def find_balloon_target(self, plant: Plant) -> bool:
        """Finds if there is a balloon zombie target in the same row."""
        for z in self.scene.zombies:
            if z.is_dead or z.is_hypno or z.row != plant.row:
                continue

            # 必须在植物右侧（或重叠）
            if z.x < plant.x:  # 简单判定
                continue

            if z.type == ZombieType.BALLOON and \
                    z.status in (ZombieStatus.BALLOON_FLYING, ZombieStatus.BALLOON_FALLING):

                if z.row == plant.row and z.x >= plant.x:
                    return True
        return False

    def set_launch_countdown(self, plant: Plant) -> None:
        # 根据 C++ plant_base.cpp 中的 set_launch_countdown 实现
        # 对于 CACTUS，总是设置 launch countdown，无论是否有目标
        # 实际的攻击决策在 update_attack 中处理

        if plant.status == PlantStatus.CACTUS_TALL_IDLE:
            # 高仙人掌射击
            plant.reanimate.type = ReanimateType.ONCE
            plant.reanimate.fps = 35.0
            plant.reanimate.n_repeated = 0
            plant.countdown.launch = 23
        else:
            # 标准射击
            plant.reanimate.type = ReanimateType.ONCE
            plant.reanimate.fps = 35.0
            plant.reanimate.n_repeated = 0
            plant.countdown.launch = 35
