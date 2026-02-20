from pvzemu2.enums import ProjectileType, ProjectileMotionType, AttackFlags
from pvzemu2.objects.projectile import Projectile
from pvzemu2.scene import Scene
from pvzemu2.systems.rng import RNG


class ProjectileFactory:
    def __init__(self, scene: Scene) -> None:
        self.scene = scene
        self.rng = RNG(scene=self.scene)

    def create(self, projectile_type: ProjectileType, row: int, x: float, y: float) -> Projectile:
        """对应 C++ projectile_factory::create"""
        proj = Projectile(
            type=projectile_type,
            row=row,
            x=x,
            y=y
        )

        # 赋予子弹一个初始高度，防止被 _roof_set_disappear 误判为撞地
        # 67.0 是一个经验值（参考了 CobCannon 的重置逻辑）
        proj.shadow_y = proj.y + 67.0

        # 初始化物理属性 (对应 C++ alloc_and_init)
        proj.dx = 0.0
        proj.dy1 = 0.0
        proj.motion_type = ProjectileMotionType.STRAIGHT

        # 根据类型设置属性
        if projectile_type in (ProjectileType.PEA, ProjectileType.SNOW_PEA, ProjectileType.FIRE_PEA):
            proj.dx = 3.33  # 基础飞行速度
            proj.attack_box_width = 40
            proj.attack_box_height = 40

        elif projectile_type in (ProjectileType.CABBAGE, ProjectileType.MELON, ProjectileType.KERNEL):
            proj.motion_type = ProjectileMotionType.PARABOLA
            # 抛物线逻辑较复杂，初期可简化为直线或后续完善
            proj.dx = 2.0

            # 设置攻击标志位 (Flags)
        # 简化处理：默认为地面攻击
        proj.flags = AttackFlags.GROUND | AttackFlags.DYING_ZOMBIES

        self.scene.projectiles.add(proj)
        return proj

    def destroy(self, proj: Projectile) -> None:
        proj.is_disappeared = True
        self.scene.projectiles.remove_obj(proj)
