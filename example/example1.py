import json

from pvzemu2.enums import SceneType, PlantType, PlantStatus
from pvzemu2.world import World


def example_basic():
    print("=== 示例 1: 基础模拟 ===")

    # 1. 初始化一个泳池关卡 (Pool)
    world = World(SceneType.POOL)
    print(f"初始化世界: {world.scene.type.name}")
    print(f"初始阳光: {world.scene.sun.sun}")

    # 2. 在第 2 行，第 2 列种植一个向日葵
    # 注意：行列从 0 开始
    row, col = 0, 2
    success = world.plant(PlantType.SUNFLOWER, row, col)

    if success:
        print(f"成功在 ({row}, {col}) 种植了向日葵！")
    else:
        print("种植失败（可能是阳光不足或位置被占用）。")

    # 3. 运行游戏循环 100 帧 (约 1 秒游戏时间)
    print("开始模拟 100 帧...")
    for _ in range(100):
        world.update()

    # 4. 检查结果
    plant = list(world.scene.plants)[0]
    print(f"模拟结束。当前帧: {world.scene.zombie_dancing_clock}")
    print(f"植物状态: HP={plant.hp}, 倒计时={plant.countdown.generate}")


def example_json_export():
    print("\n=== 示例 2: JSON 数据导出 ===")

    world = World(SceneType.DAY)

    # 放置一些植物构建场景
    world.plant(PlantType.PEA_SHOOTER, 1, 1)
    world.plant(PlantType.WALLNUT, 1, 3)

    # 模拟几帧让状态发生变化（例如动画帧推进）
    for _ in range(10):
        world.update()

    # 获取 JSON 字符串
    json_str = world.to_json()

    # 为了演示，我们将其解析回来并漂亮的打印部分数据
    data = json.loads(json_str)

    print("导出的数据概览:")
    print(f"- 关卡类型: {data['type']}")
    print(f"- 存活植物数: {len(data['plants'])}")
    print(f"- 僵尸跳舞时钟: {data['zombie_dancing_clock']}")

    print("\n植物详情 (前1个):")
    print(json.dumps(data['plants'][0], indent=2))


def example_auto_player():
    print("\n=== 示例 3: 自动化种植策略 ===")

    world = World(SceneType.ROOF)
    target_row = 2

    # 为了演示，给无限阳光
    world.scene.sun.sun = 9999

    print(f"开始自动在第 {target_row} 行种植豌豆射手...")

    # 模拟 500 帧
    for frame in range(500):
        world.update()

        # 每隔 30 帧尝试种植一次 (模拟操作频率)
        if frame % 30 == 0:
            for col in range(5):  # 尝试填满前5列
                # 检查该位置是否已有植物 (简单检查)
                cell_content = world.scene.plant_map[target_row][col]['content']

                if cell_content is None:
                    if world.plant(PlantType.PEA_SHOOTER, target_row, col):
                        print(f"[帧 {frame}] 在 ({target_row}, {col}) 种植豌豆射手")
                        break  # 一次只种一个

    print(f"模拟结束。场上共有 {len(world.scene.plants)} 株植物。")


def example_monitor_state():
    print("\n=== 示例 4: 状态监控 (土豆地雷) ===")

    world = World(SceneType.NIGHT)

    # 种植土豆地雷
    row, col = 3, 3
    world.plant(PlantType.POTATO_MINE, row, col)

    # 获取该植物的直接引用
    # 注意：在C++ wrapper中这里通常是引用，Python中也是引用
    potato = list(world.scene.plants)[0]

    print(f"初始状态: {potato.status.name}, 准备倒计时: {potato.countdown.status}")

    # 监控状态变化
    prev_status = potato.status

    # 土豆地雷需要约 1500 帧 (C++ 设定) 才能长出来，我们加速模拟
    # 假设每秒 100 帧
    target_frames = 1600
    for i in range(target_frames):
        world.update()

        if potato.status != prev_status:
            print(f"--> [帧 {i}] 状态发生改变: {prev_status.name} -> {potato.status.name}")
            prev_status = potato.status

            if potato.status == PlantStatus.POTATO_ARMED:  # 假设你有这个枚举值对应 0x10
                print("    土豆地雷已准备就绪！")
                break


def example_twinflower_upgrade():
    print("\n=== 示例 5: 紫卡升级 (双子向日葵) ===")
    world = World(SceneType.DAY)
    world.scene.sun.sun = 1000

    # 1. 种下基础向日葵
    p_base = world.plant(PlantType.SUNFLOWER, 1, 1)
    print(f"种植向日葵, ID: {p_base.id}")

    # 2. 种下双子向日葵（现在会自动替换）
    p_up = world.plant(PlantType.TWIN_SUNFLOWER, 1, 1)

    if p_up:
        print(f"成功升级为双子向日葵, ID: {p_up.id}")
        # 验证旧向日葵是否已死
        print(f"基础向日葵是否已销毁: {p_base.is_dead}")
        # 验证网格指向
        current_content = world.scene.plant_map[1][1]['content']
        print(f"网格当前植物类型: {current_content.type.name}")
    else:
        print("升级失败！")


if __name__ == "__main__":
    example_basic()
    example_json_export()
    example_auto_player()
    example_monitor_state()
    example_twinflower_upgrade()
