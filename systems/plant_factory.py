from pvzemu2.enums import PlantType, GridItemType, SceneType, PlantEdibleStatus, PlantStatus, PlantReanimName
from pvzemu2.objects.base import get_uuid, ReanimateType
from pvzemu2.objects.plant import Plant, COST_TABLE, CAN_ATTACK_TABLE
from pvzemu2.scene import Scene
from pvzemu2.systems.rng import RNG
from pvzemu2.systems.util import get_y_by_row_and_col


class PlantFactory:
    def __init__(self, scene: Scene) -> None:
        self.scene = scene

    def is_pos_valid(self, row: int, col: int) -> bool:
        """
        校验植物放置位置是否合法
        - POOL / FOG: 6行 (索引 0-5)
        - 其他所有场景: 5行 (索引 0-4)
        - 所有场景默认均为 9列 (索引 0-8)
        """
        if not (0 <= col <= 8):
            return False

        match self.scene.type:
            case SceneType.POOL | SceneType.FOG:
                max_row = 5
            case _:
                max_row = 4
        return 0 <= row <= max_row

    def is_covered_by_griditem(self, row: int, col: int) -> tuple[bool, bool]:
        has_grave = False
        has_crater = False

        for item in self.scene.grid_items:
            if item.col == col and item.row == row:
                if item.type == GridItemType.GRAVE:
                    has_grave = True
                elif item.type == GridItemType.CRATER:
                    has_crater = True

                if has_grave and has_crater:
                    return True, True

        return has_grave, has_crater

    def is_not_covered_by_ice_path(self, row: int, col: int) -> bool:
        """
        检查指定格子是否未被冰道覆盖。
        对应 C++: plant_factory::is_not_covered_by_ice_path
        """
        # 各列对应的 X 坐标阈值
        ICE_PATH_TABLE = (108, 188, 268, 348, 428, 508, 588, 668, 751)

        # 如果该行没有冰道倒计时，则未被覆盖
        if self.scene.ice_path.countdown[row] <= 0:
            return True

        # 如果冰道的左端点 (x) 在目标格子的右侧，则该格子未被覆盖
        # (冰车从右向左开，留下的冰道延伸到 x)
        if col < 0 or col >= len(ICE_PATH_TABLE):
            return True  # 越界保护，视为未覆盖

        return self.scene.ice_path.x[row] >= ICE_PATH_TABLE[col]

    def get_cost(self, type: PlantType) -> int:
        if type < 0 or type >= len(COST_TABLE):
            return 0

        base_cost = COST_TABLE[type]
        if type >= PlantType.GATLING_PEA:
            n = sum(1 for p in self.scene.plants if p.type == type)
            return base_cost + 50 * n
        return base_cost

    def can_plant_advanced_plant(self, status: dict, row: int, col: int, advanced: PlantType) -> bool:
        content = status.get('content')
        base = status.get('base')

        if advanced != PlantType.CATTAIL and \
                (content is None or content.edible == PlantEdibleStatus.INVISIBLE_AND_EDIBLE):
            return False

        match advanced:
            case PlantType.GATLING_PEA:
                return content.type == PlantType.REPEATER

            case PlantType.TWIN_SUNFLOWER:
                return content.type == PlantType.SUNFLOWER

            case PlantType.GLOOMSHROOM:
                return content.type == PlantType.FUMESHROOM

            case PlantType.WINTER_MELON:
                return content.type == PlantType.MELONPULT

            case PlantType.GOLD_MAGNET:
                return content.type == PlantType.MAGNETSHROOM

            case PlantType.SPIKEROCK:
                return content.type == PlantType.SPIKEWEED

            case PlantType.CATTAIL:
                # Cattail can be planted on a Lily Pad without any content.
                return base is not None and base.type == PlantType.LILY_PAD and content is None

            case PlantType.COB_CANNON:
                if content.type != PlantType.KERNELPULT or \
                        content.col >= 8:
                    return False

                # Check next column
                if 0 <= row < 6 and 0 <= col + 1 < 9:
                    s1 = self.scene.plant_map[row][col + 1]
                    content1 = s1.get('content')
                    # Cob Cannon requires two Kernel-pults side-by-side
                    if content1 and content1.type == PlantType.KERNELPULT:
                        return True
                return False

            case _:
                return False

    def can_plant(self, row: int, col: int, type: PlantType, imitater_type: PlantType = PlantType.NONE) -> bool:
        # 1. Basic environment validation
        if not self.is_pos_valid(row, col) or not self.is_not_covered_by_ice_path(row, col):
            return False

        # Check grid items (Grave/Crater)
        has_grave, has_crater = self.is_covered_by_griditem(row, col)
        if has_crater:
            return False

        # Identify target plant type
        target_type = imitater_type if type == PlantType.IMITATER else type
        scene = self.scene

        # Sun cost check
        if self.get_cost(target_type) > scene.sun.sun:
            return False

        # Get cell status - use direct access for performance
        status = scene.plant_map[row][col]
        content = status['content']

        # Grave Buster specific check
        if target_type == PlantType.GRAVE_BUSTER:
            return content is None and has_grave

        if has_grave:
            return False

        # Pre-calculate environmental flags
        is_roof = scene.type == SceneType.ROOF or scene.type == SceneType.MOON_NIGHT
        is_water = (scene.type == SceneType.POOL or scene.type == SceneType.FOG) and (row == 2 or row == 3)

        # Check for Pot/Lily base
        base = status['base']
        has_pot = base and base.type == PlantType.FLOWER_POT and base.edible != PlantEdibleStatus.INVISIBLE_AND_EDIBLE
        has_lily = base and base.type == PlantType.LILY_PAD and base.edible != PlantEdibleStatus.INVISIBLE_AND_EDIBLE

        # Stage 1: Special placement logic (C++ Switch 1)
        match target_type:
            case PlantType.LILY_PAD | PlantType.TANGLE_KELP | PlantType.SEASHROOM:
                return is_water and base is None and content is None

            case PlantType.SPIKEWEED:
                return not is_water and not is_roof and base is None and content is None

            case PlantType.SPIKEROCK:
                return (not is_water and not is_roof and base is None and
                        self.can_plant_advanced_plant(status, row, col, PlantType.SPIKEROCK))

            case PlantType.FLOWER_POT:
                return not is_water and status['pumpkin'] is None and content is None and base is None

            case PlantType.COFFEE_BEAN:
                return (status['coffee_bean'] is None and content and content.is_sleeping and
                        content.countdown.awake == 0 and content.edible != PlantEdibleStatus.INVISIBLE_AND_EDIBLE)

            case PlantType.PUMPKIN:
                # Environment check: Roof needs Pot, Water needs Lily or Cattail
                env_ok = (not is_roof or has_pot) and (
                        not is_water or has_lily or (content and content.type == PlantType.CATTAIL))
                # Occupancy: Cannot plant on Cob Cannon
                content_ok = content is None or content.type != PlantType.COB_CANNON
                # Repair logic: Can replant if HP < 2/3 (2666)
                pumpkin = status['pumpkin']
                repair_ok = pumpkin is None or (pumpkin.type == PlantType.PUMPKIN and pumpkin.hp < 2666 and
                                                pumpkin.edible != PlantEdibleStatus.INVISIBLE_AND_EDIBLE)
                return env_ok and content_ok and repair_ok

            case _:
                # Default environment constraint
                if (is_roof and not has_pot) or (is_water and not has_lily):
                    return False

        # Stage 2: Occupancy and Nut repair (C++ Switch 2)
        match target_type:
            case PlantType.WALLNUT:
                # Repair threshold 2666 (2/3 of 4000)
                return (content is None or (content.type == PlantType.WALLNUT and content.hp < 2666 and
                                            content.edible != PlantEdibleStatus.INVISIBLE_AND_EDIBLE))

            case PlantType.TALLNUT:
                # Repair threshold 5333 (2/3 of 8000)
                return (content is None or (content.type == PlantType.TALLNUT and content.hp < 5333 and
                                            content.edible != PlantEdibleStatus.INVISIBLE_AND_EDIBLE))
            case t if Plant.is_upgrade(t):
                return self.can_plant_advanced_plant(status, row, col, t)

            case _:
                # Block if cell is already occupied
                if content is not None:
                    return False

        # Stage 3: Specific restrictions and Upgrades (C++ Switch 3)
        match target_type:
            case PlantType.POTATO_MINE:
                return not is_water
            case _:
                return True

    def create(self, type: PlantType, row: int, col: int, imitater_target: PlantType = PlantType.NONE) -> Plant:
        # 确定实际产出的类型（处理模仿者）
        actual_type = imitater_target if type == PlantType.IMITATER else type
        # 获取当前格子的状态
        cell = self.scene.plant_map[row][col]

        # --- 补齐逻辑：处理升级植物的替换过程 ---
        if Plant.is_upgrade(actual_type):
            # 特殊情况：玉米加农炮（占用两格，需要销毁两个玉米投手）
            if actual_type == PlantType.COB_CANNON:
                # 销毁左侧基础植物
                base_left = cell.get('content')
                if base_left:
                    self.destroy(base_left)
                # 销毁右侧基础植物 (col + 1)
                if col + 1 < 9:
                    base_right = self.scene.plant_map[row][col + 1].get('content')
                    if base_right:
                        self.destroy(base_right)

            # 特殊情况：香蒲（种在莲叶上，莲叶是 base，content 通常为 None）
            elif actual_type == PlantType.CATTAIL:
                # 按照 C++ 逻辑，香蒲不销毁莲叶，只是占据 content 位置
                # 但如果 content 位置恰好有模仿者未消失或其他情况，则清理
                base_content = cell.get('content')
                if base_content:
                    self.destroy(base_content)

            # 通用升级：双子向日葵、机枪豌豆、忧郁菇、冰西瓜、地刺王、金磁铁
            else:
                base_plant = cell.get('content')
                # 只有当格子上有植物时才销毁（基础植物通常在 content 槽位）
                if base_plant:
                    self.destroy(base_plant)

        # Calculate coordinates
        x = col * 80 + 40
        y = get_y_by_row_and_col(self.scene.type, row, col)

        uuid = get_uuid()

        if type == PlantType.WALLNUT:
            hp = 4000
        elif type == PlantType.TALLNUT:
            hp = 8000
        elif type == PlantType.PUMPKIN:
            hp = 4000
        elif type == PlantType.GARLIC:
            hp = 400
        elif type == PlantType.SPIKEROCK:
            hp = 450
        else:
            hp = 300

        max_hp = hp

        status = PlantStatus.IDLE

        max_boot_delay = 0
        # Set max_boot_delay for shooting plants (approx 1.5s = 150 frames)
        if type in (PlantType.PEA_SHOOTER, PlantType.SNOW_PEA, PlantType.REPEATER,
                    PlantType.GATLING_PEA, PlantType.SPLIT_PEA, PlantType.THREEPEATER,
                    PlantType.CACTUS, PlantType.CABBAGEPULT, PlantType.KERNELPULT,
                    PlantType.MELONPULT, PlantType.WINTER_MELON, PlantType.CATTAIL,
                    PlantType.STARFRUIT, PlantType.PUFFSHROOM, PlantType.FUMESHROOM,
                    PlantType.SCAREDYSHROOM, PlantType.SEASHROOM, PlantType.GLOOMSHROOM):
            max_boot_delay = 150

        plant = Plant(
            type=type,
            row=row,
            col=col,
            x=x,
            y=y,
            hp=hp,
            max_hp=max_hp,
            can_attack=CAN_ATTACK_TABLE[type] if type < len(CAN_ATTACK_TABLE) else True,
            max_boot_delay=max_boot_delay,
            status=status,
        )
        if type in (PlantType.SUNFLOWER, PlantType.TWIN_SUNFLOWER, PlantType.SUNSHROOM):
            rng = RNG(self.scene)
            plant.countdown.generate = rng.randint(951) + 300
            if type == PlantType.SUNSHROOM:
                plant.status = PlantStatus.SUNSHROOM_SMALL
                plant.countdown.status = 12000

        if Plant.is_nocturnal(type):
            if self.scene.type in (SceneType.DAY, SceneType.POOL, SceneType.ROOF):
                plant.set_sleep(True)

        if type == PlantType.BLOVER:
            plant.countdown.effect = 50
            plant.set_reanim(PlantReanimName.anim_idle, ReanimateType.ONCE, 10.0)
        elif type == PlantType.COB_CANNON:
            plant.status = PlantStatus.COB_CANNON_UNARMED_IDLE
            plant.countdown.status = 500
            plant.set_reanim_frame(PlantReanimName.anim_unarmed_idle)
        elif type == PlantType.GRAVE_BUSTER:
            plant.status = PlantStatus.GRAVE_BUSTER_LAND
            plant.set_reanim(PlantReanimName.anim_land, ReanimateType.ONCE, 12.0)
        elif type == PlantType.CHOMPER:
            plant.status = PlantStatus.WAIT
        elif type == PlantType.CACTUS:
            plant.status = PlantStatus.CACTUS_SHORT_IDLE
        elif type == PlantType.COFFEE_BEAN:
            plant.countdown.effect = 100
        elif type == PlantType.IMITATER:
            plant.imitater_target = imitater_target
            plant.status = PlantStatus.IDLE
            plant.countdown.status = 30  # Approx delay before transforming

        self.scene.plants.add(plant)

        # Update Grid Map
        if 0 <= row < len(self.scene.plant_map) and 0 <= col < 9:
            cell = self.scene.plant_map[row][col]

            if type == PlantType.PUMPKIN:
                cell['pumpkin'] = plant
            elif type == PlantType.COFFEE_BEAN:
                cell['coffee_bean'] = plant
            elif type in (PlantType.FLOWER_POT, PlantType.LILY_PAD):
                cell['base'] = plant
            elif type == PlantType.COB_CANNON:
                cell['content'] = plant
                if col + 1 < 9:
                    self.scene.plant_map[row][col + 1]['content'] = plant
            else:
                cell['content'] = plant

        return plant

    def destroy(self, plant: Plant) -> None:
        plant.is_dead = True
        self.scene.plants.remove_obj(plant)

        # Handle Tangle Kelp target logic (Simplified, assumes we can't easily access zombie from here without more info)
        # In C++: if (p.type == plant_type::tangle_kelp && p.target != -1) ...

        if plant.type != PlantType.COFFEE_BEAN:
            # Destroy ladders at this position
            for item in self.scene.grid_items:
                if item.row == plant.row and item.col == plant.col and item.type == GridItemType.LADDER:
                    # Circular import avoidance: We don't import GridItemFactory here. 
                    # Just mark item as disappeared or use a callback if possible.
                    item.is_disappeared = True

        if 0 <= plant.row < len(self.scene.plant_map) and 0 <= plant.col < 9:
            status = self.scene.plant_map[plant.row][plant.col]

            if status.get('pumpkin') == plant:
                status['pumpkin'] = None

            if status.get('coffee_bean') == plant:
                status['coffee_bean'] = None

            if status.get('base') == plant:
                status['base'] = None

            if status.get('content') == plant:
                status['content'] = None

            if plant.type == PlantType.COB_CANNON:
                if plant.col + 1 < 9:
                    s2 = self.scene.plant_map[plant.row][plant.col + 1]
                    if s2.get('content') == plant:
                        s2['content'] = None
