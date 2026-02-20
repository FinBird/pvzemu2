from pvzemu2.world import World
from pvzemu2.enums import SceneType, PlantType, ZombieType
from pvzemu2.systems.util import get_col_by_x


def simple_battle_example():
    # 初始化世界 (白天场景)
    world = World(SceneType.DAY)

    # 种植一个豌豆射手 在 row=2 col =1
    peashooter = world.plant(PlantType.PEA_SHOOTER, row=2, col=1)
    if peashooter:
        peashooter.countdown.generate = 0  # 取消初始攻击冷却

    # 在 row=2 距离房子 700 pixel 的位置生成一个普通僵尸
    zombie = world.spawn(ZombieType.ZOMBIE, row=2, x=700.0)

    # 禁用动画位移补偿，强制使用线性位移 (z.dx)，数据将不再抖动
    zombie._ground = None

    print(f"=== 战斗开始 ===")
    print(f"植物初始 HP: {peashooter.hp if peashooter else 'N/A'}, 僵尸初始 HP: {zombie.hp}")

    # 模拟运行2100帧
    for frame in range(1, 210100):
        world.update()
        if frame % 140 == 0: # 打印关键帧状态
            z_col = get_col_by_x(int(zombie.x))
            print(f"[Frame {frame:4}] 僵尸位置: {zombie.x:6.2f} | 所在列: {z_col} | 僵尸 HP: {zombie.hp:3}")

    print(f"=== 模拟结束 ===")


if __name__ == "__main__":
    from time import time
    t1 =time()
    simple_battle_example()
    t2 =time()
    print(t2-t1)