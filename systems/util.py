from typing import TYPE_CHECKING, Optional

from pvzemu2.enums import SceneType, ZombieType, ZombieStatus, ZombieAction, PlantType
from pvzemu2.objects.zombie import Zombie

if TYPE_CHECKING:
    from pvzemu2.scene import Scene


def get_col_by_x(x: int) -> int:
    if x >= 40:
        return max(0, min(8, (x - 40) // 80))
    else:
        return -1


def get_y_by_col(scene_type: SceneType, row: int, col: int) -> float:
    y: float
    if scene_type in (SceneType.ROOF, SceneType.MOON_NIGHT):
        offset = float(20 * (5 - col) if col < 5 else 0)
        y = (85 * row + offset + 80) - 10
    elif scene_type in (SceneType.FOG, SceneType.POOL):
        y = float(85 * row + 80)
    else:
        y = float(100 * row + 80)
    return y


def get_y_by_row_and_x(scene_type: SceneType, row: int, x: float) -> float:
    if scene_type in (SceneType.ROOF, SceneType.MOON_NIGHT):
        offset = 0.0
        if x < 440:
            offset = (440.0 - x) * 0.25
        return get_y_by_col(scene_type, row, 8) + offset
    else:
        return get_y_by_col(scene_type, row, 0)


def get_y_by_row_and_col(scene_type: SceneType, row: int, col: int) -> int:
    """对应 C++ util.cpp::get_y_by_row_and_col"""
    if scene_type in (SceneType.ROOF, SceneType.MOON_NIGHT):
        offset = 20 * (5 - col) if col < 5 else 0
        return 85 * row + offset + 70
    elif scene_type in (SceneType.FOG, SceneType.POOL):
        return 85 * row + 80
    else:
        return 100 * row + 80


def get_row_by_x_and_y(scene_type: SceneType, x: int, y: int) -> int:
    col = get_col_by_x(x)
    if col == -1 or y < 80:
        return -1

    if scene_type in (SceneType.DAY, SceneType.NIGHT):
        return max(0, (y - 80) // 100)
    elif scene_type in (SceneType.POOL, SceneType.FOG):
        return max(0, min(5, (y - 80) // 85))
    elif scene_type in (SceneType.ROOF, SceneType.MOON_NIGHT):
        if col < 5:
            row = (y - 20 * (4 - col) - 80) // 85
        else:
            row = (y - 80) // 85
        return max(0, min(4, row))
    else:
        return -1


def zombie_init_y(scene_type: SceneType, z: Zombie, row: int) -> float:
    y = get_y_by_row_and_x(scene_type, row, z.x + 40) - 30
    if z.type == ZombieType.BALLOON:
        y -= 30
    elif z.type == ZombieType.POGO:
        y -= 16
    return y


def is_not_movable(scene: 'Scene', z: Zombie) -> bool:
    if (z.is_eating or
            z.countdown.freeze > 0 or
            z.countdown.butter > 0 or
            z.status == ZombieStatus.JACKBOX_POP or
            z.status == ZombieStatus.NEWSPAPER_DESTROYED or
            z.status == ZombieStatus.GARGANTUAR_THROW or
            z.status == ZombieStatus.GARGANTUAR_SMASH or
            z.status == ZombieStatus.CATAPULT_SHOOT or
            z.status == ZombieStatus.CATAPULT_IDLE or
            z.status == ZombieStatus.DIGGER_DRILL or
            z.status == ZombieStatus.DIGGER_LOST_DIG or
            z.status == ZombieStatus.DIGGER_LANDING or
            z.status == ZombieStatus.DIGGER_DIZZY or
            z.status == ZombieStatus.DANCING_POINT or
            z.status == ZombieStatus.DANCING_WAIT_SUMMONING or
            z.status == ZombieStatus.DANCING_SUMMONING or
            z.status == ZombieStatus.DANCING_DANCER_SPAWNING or
            z.status == ZombieStatus.IMP_FLYING or
            z.status == ZombieStatus.IMP_LANDING or
            z.status == ZombieStatus.LADDER_PLACING or
            z.action == ZombieAction.FALL_FROM_SKY or
            z.status == ZombieStatus.DANCING_ARMRISE1 or
            z.status == ZombieStatus.DANCING_ARMRISE2 or
            z.status == ZombieStatus.DANCING_ARMRISE3 or
            z.status == ZombieStatus.DANCING_ARMRISE4 or
            z.status == ZombieStatus.DANCING_ARMRISE5 or
            # z.action.value == 8 or # C++ checks static_cast<int>(z.action) == 8, but 8 is not in enum
            z.type == ZombieType.BUNGEE):
        return True

    p: Optional[Zombie] = None

    if z.type == ZombieType.DANCING:
        p = z
    elif z.type == ZombieType.BACKUP_DANCER:
        if z.master_id is not None:
            p = scene.zombies.get(z.master_id)
    else:
        return False

    if p is None:
        return False

    if p.is_eating or p.countdown.butter > 0 or p.countdown.freeze > 0:
        return True

    for i in p.partners:
        t = scene.zombies.get(i)
        if t and (t.is_eating or t.countdown.butter > 0 or t.countdown.freeze > 0):
            return True

    return False


def has_death_status(z: Zombie) -> bool:
    return z.status in (
        ZombieStatus.DYING,
        ZombieStatus.DYING_FROM_INSTANT_KILL,
        ZombieStatus.DYING_FROM_LAWNMOWER
    )


def is_walk_right(z: Zombie) -> bool:
    if z.is_hypno:
        return True

    if z.type == ZombieType.DIGGER:
        if z.status in (
                ZombieStatus.DIGGER_DRILL,
                ZombieStatus.DIGGER_DIZZY,
                ZombieStatus.DIGGER_WALK_RIGHT
        ):
            return True

        if has_death_status(z):
            return z.has_item_or_walk_left

        return False

    return z.type == ZombieType.YETI and not z.has_item_or_walk_left


def predict_after(scene: 'Scene', z: Zombie, cs: float) -> float:
    """
    预测僵尸在 cs 帧后的 X 坐标
    对应 C++ zombie_base::predict_after
    """
    dx = z.dx

    if z.countdown.slow > 0:
        dx *= 0.4000000059604645

    if is_walk_right(z):
        dx = -dx

    if is_not_movable(scene, z):
        dx = 0

    rect = z.get_hit_box_rect()
    # C++: return rect.x + static_cast<long double>(rect.width) / 2 - dx * cs;
    # In C++, get_hit_box returns absolute rect.
    # In Python, get_hit_box_rect returns absolute rect.

    return rect.x + rect.width / 2 - dx * cs


def is_target_of_kelp(scene: 'Scene', z: Zombie) -> bool:
    """
    新增：判断僵尸是否已经被缠绕水草锁定或抓取。
    对应 C++ util.cpp::is_target_of_kelp
    """
    # 如果不在水池/浓雾场景，或者不在水路(2,3行)，肯定不会被水草抓
    if scene.type not in (SceneType.FOG, SceneType.POOL) or z.row not in (2, 3):
        return False

    # 僵尸状态已被标记为正在被水草抓取
    if z.action == ZombieAction.CAUGHT_BY_KELP:
        return True

    # 扫描该行所有植物，看是否有水草的 target_id 指向了该僵尸
    for col in range(9):
        plant = scene.plant_map[z.row][col]['content']
        if plant and plant.type == PlantType.TANGLE_KELP and plant.target_id == z.id:
            return True

    return False


def is_slowed(scene: 'Scene', z: Zombie) -> bool:
    """
    核心更新：判断僵尸是否处于减速状态。
    对应 C++ util.cpp::is_slowed
    注意：舞王僵尸及其伴舞僵尸具有减速共享机制。
    """
    if z.countdown.slow > 0:
        return True

    p: Optional[Zombie] = None

    if z.type == ZombieType.BACKUP_DANCER:
        if z.master_id is not None:
            p = scene.zombies.get(z.master_id)

        if p is None:
            return False

        if p.countdown.slow > 0:
            return True
    elif z.type == ZombieType.DANCING:
        p = z
    else:
        return False

    # 检查伴舞团队是否被减速
    for partner_id in p.partners:
        if partner_id == -1:  # 忽略空位
            continue

        t = scene.zombies.get(partner_id)
        if t is not None and t.countdown.slow > 0:
            return True

    return False
