from pvzemu2 import World
from pvzemu2.enums import SceneType, PlantType, ZombieType, PlantStatus, ZombieStatus


def run_visual_scenario():
    # 1. 初始化世界
    world = World(SceneType.DAY)
    world.scene.stop_spawn = True

    print("🛡️  正在布置特定的战斗实验...")

    # --- 场景 1: Row 1 - 两个豌豆射手击杀路障僵尸 ---
    world.plant(PlantType.PEA_SHOOTER, row=1, col=0)
    world.plant(PlantType.PEA_SHOOTER, row=1, col=1)
    # 放置路障僵尸，设置稍慢的速度
    z1 = world.spawn(ZombieType.CONE_HEAD, row=1, x=600)
    z1.dx = 0.2

    # --- 场景 2: Row 2 - 地雷最终炸掉 3 个同一位置释放的路障 ---
    world.plant(PlantType.POTATO_MINE, row=2, col=3)
    for i in range(3):
        z_cone = world.spawn(ZombieType.CONE_HEAD, row=2, x=750 + i * 5)  # 稍微错开防止重叠太完美
        z_cone.dx = 0.5

    # --- 场景 3: Row 3 - 大嘴花吞噬铁桶僵尸 ---
    world.plant(PlantType.CHOMPER, row=3, col=2)
    z3 = world.spawn(ZombieType.BUCKET_HEAD, row=3, x=500)
    z3.dx = 0.3

    # 全局调整：禁用动画位移以获得稳定的线性演示
    for z in world.scene.zombies:
        z._ground = None

    print("🚀 模拟开始！\n")

    for frame_batch in range(200):
        # 步进 20 帧
        world.step(20)

        if frame_batch % 10 == 0:
            print(f"【 Frame {frame_batch * 20:04d} 】" + "-" * 50)
            for r in range(1, 4):
                lane = [" . "] * 9
                # 渲染植物
                for p in [p for p in world.scene.plants if p.row == r]:
                    char = "P" if p.type == PlantType.PEA_SHOOTER else "C"
                    if p.type == PlantType.POTATO_MINE: char = "M" if p.status == PlantStatus.POTATO_ARMED else "m"
                    if p.status == PlantStatus.CHOMPER_CHEW: char = "😋"
                    lane[p.col] = f" {char} "

                # 渲染僵尸
                z_in_row = [z for z in world.scene.zombies if z.row == r]
                for z in z_in_row:
                    col = min(8, max(0, int(z.x // 80)))
                    icon = "🧟"
                    if z.type == ZombieType.CONE_HEAD: icon = "🪣"
                    if z.type == ZombieType.BUCKET_HEAD: icon = "🪖"
                    if z.status == ZombieStatus.DYING: icon = "💀"
                    lane[col] = f" {icon} "

                print(f"Row {r}: {''.join(lane)} | Zombies: {len(z_in_row)}")

        if len(list(world.scene.zombies)) == 0:
            print("\n🎉 实验完成：所有目标已达成！")
            break

    # 最终报告
    print("\n--- 实验总结 ---")
    print(f"Row 1: 路障僵尸已被集火击杀" if not [z for z in world.scene.zombies if z.row == 1] else "Row 1: 仍在交战")
    print(f"Row 2: 地雷成功完成三连杀" if not [z for z in world.scene.zombies if
                                               z.row == 2] else "Row 2: 地雷未触发或未炸完")
    chomper = next((p for p in world.scene.plants if p.type == PlantType.CHOMPER), None)
    if chomper and chomper.status == PlantStatus.CHOMPER_CHEW:
        print("Row 3: 大嘴花正在享受铁桶僵尸大餐")


if __name__ == "__main__":
    run_visual_scenario()
