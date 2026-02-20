import math
from functools import cached_property
from typing import Final

from pvzemu2.enums import ProjectileType, ProjectileMotionType, ZombieType, PlantReanimName
from pvzemu2.objects.base import ReanimateType
from pvzemu2.objects.plant import Plant
from pvzemu2.scene import Scene
from pvzemu2.systems.damage import DamageSystem
from pvzemu2.systems.plant_subsystems.base import PlantSubsystem
from pvzemu2.systems.projectile_factory import ProjectileFactory
from pvzemu2.systems.rng import RNG
from pvzemu2.systems.util import predict_after


class StarfruitPhysics:
    """杨桃物理参数计算与缓存"""

    # 杨桃的攻击是典型的五向散射，其核心逻辑基于 3.33 像素/帧 的基准速度和 30 度的发射角。
    BASE_SPEED: Final[float] = 3.33  # C++ 中单精度 float 3.33f 在转换为 double 时约为 3.329999923706055
    BASE_ANGLE_DEG: Final[float] = 30.0  # 散射角：杨桃前方两个子弹相对于水平线的夹角

    @cached_property
    def projectile_speed(self) -> float:
        """返回标量速率：3.33"""
        return self.BASE_SPEED

    @cached_property
    def v_cos(self) -> float:
        """
        计算斜向子弹的 X 轴速度分量 (Forward Diagonal X)
        公式: Speed * cos(30°) = 3.33 * (√3 / 2)
        实际值: ~2.883864528529686
        """
        return self.BASE_SPEED * math.cos(math.radians(self.BASE_ANGLE_DEG))

    @cached_property
    def v_sin(self) -> float:
        """
        计算斜向子弹的 Y 轴速度分量 (Forward Diagonal Y)
        公式: Speed * sin(30°) = 3.33 * 0.5
        实际值: 1.665 (C++中由于float精度显示为 1.6649999618530275)
        """
        return self.BASE_SPEED * math.sin(math.radians(self.BASE_ANGLE_DEG))

    @cached_property
    def rad_to_deg(self) -> float:
        """弧度转角度因子
        公式: (180 / PI)
        实际值: ~57.2957795... (C++硬编码值为 57.2957763671875)
        """
        return 180.0 / math.pi


# 单例实例化物理参数库
PHYSICS: Final = StarfruitPhysics()

# Offset Constants
# 杨桃判定中心点相对于左上角坐标的偏移量
PLANT_CENTER_OFFSET_X: Final[int] = 40
PLANT_CENTER_OFFSET_Y: Final[int] = 40

# 子弹生成点偏移
PROJECTILE_OFFSET_X: Final[int] = 25
PROJECTILE_OFFSET_Y: Final[int] = 25

# 修正：矿工僵尸在地下移动，其受击箱宽度在判定时需要额外增加 10 像素
DIGGER_OFFSET_WIDTH: Final[int] = 10

# 攻击发动后的冷却延迟（帧）
LAUNCH_DELAY: Final[int] = 40


class StarfruitSubsystem(PlantSubsystem):
    def __init__(self, scene: Scene, damage_system: DamageSystem, rng: RNG,
                 projectile_factory: ProjectileFactory) -> None:
        super().__init__(scene, damage_system, rng)
        self.projectile_factory = projectile_factory

    def update(self, p: Plant) -> None:
        pass

    def has_target(self, p: Plant) -> bool:
        if p.countdown.eaten > 0:
            return True

        flags = self.damage_system._get_plant_attack_flags(p, False)

        # 计算植物中心坐标 (px, py)
        px = p.x + PLANT_CENTER_OFFSET_X
        py = p.y + PLANT_CENTER_OFFSET_Y

        proj_speed = PHYSICS.projectile_speed

        for z in self.scene.zombies:
            if not self.damage_system.can_be_attacked(z, flags):
                continue

            zr = z.get_hit_box_rect()

            # Same row logic - Starfruit shoots backward only in the same row
            if z.row == p.row:
                # 僵尸在植物后面（僵尸右边缘 < 植物中心）
                if zr.x + zr.width < px:
                    return True
                continue

            # Adjust hit box for Digger Zombie
            if z.type == ZombieType.DIGGER:
                zr.width += DIGGER_OFFSET_WIDTH

            # 获取僵尸当前中心点
            hzw = zr.width / 2 + zr.x
            hzh = zr.height / 2 + zr.y

            # 计算植物中心到僵尸中心的位移向量 (dx, dy)
            dx = hzw - float(px)
            dy = hzh - float(py)

            # 估算子弹到达僵尸当前位置所需的时间 t (帧)
            # 公式: t = 欧几里得距离 / 速度
            t = math.hypot(dx, dy) / proj_speed

            # Predict zombie position based on time to impact
            predict = predict_after(self.scene, z, float(t))

            # 杨桃上下方垂直方向的子弹可以击中该僵尸 (对应朝上和朝下的两枚子弹)
            # Check for vertical hits (Up/Down stars)
            # C++: if (px < predict + zr.width / 2 && predict - zr.width / 2 < px)
            z_half_w = zr.width / 2
            if (predict - z_half_w) < px < (predict + z_half_w):
                return True

            # 斜向命中判定 (对应前方斜上 30° 和斜下 30° 的两枚子弹)
            # Check for diagonal hits
            # C++: int x_predict = static_cast<int>(predict + zr.width / 2 - px);
            # C++: int y_predict = static_cast<int>(zr.y + zr.height / 2 - py);
            x_predict = (predict + z_half_w) - px
            y_predict = (zr.y + zr.height / 2) - py

            # 避免除以零或非常小的 x_predict
            if abs(x_predict) < 0.001:
                continue

            # 使用 atan2 计算极角 (弧度)，然后转换为角度 (deg)
            deg = math.degrees(math.atan2(y_predict, x_predict))

            row_diff = abs(int(p.row) - int(z.row))

            if row_diff >= 2:  # 目标在隔行或更远，判定区间较窄 (约 10 度宽)
                # 判定夹角是否在误差 5° 的范围内 (斜下 25~35，斜上 -28~-38)
                if (25 < deg < 35) or (-38 < deg < -28):
                    return True
            else:  # 目标在相邻行，判定区间较宽 (约 20 度宽)
                # 判定夹角是否在误差 10° 的范围内 (斜下 20~40，斜上 -25~-45)
                if (20 < deg < 40) or (-45 < deg < -25):
                    return True

        return False

    def set_launch_countdown(self, p: Plant) -> None:
        if self.has_target(p):
            p.set_reanim_frame(PlantReanimName.anim_shoot)
            p.reanimate.type = ReanimateType.ONCE
            p.reanimate.n_repeated = 0
            p.reanimate.fps = 28.0
            p.countdown.launch = LAUNCH_DELAY

    def attack(self, p: Plant) -> None:
        # Launch 5 stars: Back, Down, Up, Diag-Down (Forward), Diag-Up (Forward)
        flags = self.damage_system._get_plant_attack_flags(p)

        for i in range(5):
            proj = self.projectile_factory.create(
                ProjectileType.STAR,
                p.row,
                p.x + PROJECTILE_OFFSET_X,
                p.y + PROJECTILE_OFFSET_Y
            )

            proj.flags = flags
            proj.motion_type = ProjectileMotionType.STARFRUIT

            match i:
                case 0:  # 正后 (Backward)
                    proj.dx = -PHYSICS.projectile_speed  # -3.33
                    proj.dy2 = 0.0
                case 1:  # 正下 (Down)
                    proj.dx = 0.0
                    proj.dy2 = PHYSICS.projectile_speed  # 3.33
                case 2:  # 正上 (Up)
                    proj.dx = 0.0
                    proj.dy2 = -PHYSICS.projectile_speed  # -3.33
                case 3:  # 斜下 (Forward Diagonal Down)
                    proj.dx = PHYSICS.v_cos  # ~2.88
                    proj.dy2 = PHYSICS.v_sin  # 1.665
                case 4:  # 斜上 (Forward Diagonal Up)
                    proj.dx = PHYSICS.v_cos  # ~2.88
                    proj.dy2 = -PHYSICS.v_sin  # -1.665
