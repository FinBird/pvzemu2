---

# PvZ Emulator 2 (pvzemu2)

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-WIP-orange)

`pvzemu2` 是一个基于 Python 开发的《植物大战僵尸》(Plants vs. Zombies) 核心逻辑模拟器。
本项目重写自原版的 [PvZ-Emulator](https://github.com/dnartz/PvZ-Emulator) (C++)，在保留原版精确的帧级物理碰撞、动画状态机与伤害计算的基础上，**重新设计了更加现代化、Pythonic 的 API 接口**，同时仅使用Python标准库编写，使其更易于用于强化学习 (RL) 环境构建、游戏机制测试与数据分析以及逻辑调试。

> **⚠️ 注意 / Note**：
> 本项目目前仍处于 **WIP (Work In Progress)** 状态。虽然核心的植物、僵尸战斗逻辑已可用，但距离完全复刻原版游戏（特别是小游戏、解谜模式等）仍有大量 TODO 需要完善。欢迎提交 PR！

---

## 🚀 快速开始 & 最简示例

以下示例展示了如何创建一个“白天”场景，种植一个豌豆射手，生成一个普通僵尸，并模拟它们的战斗过程：

### 代码示例

```python
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
    for frame in range(1, 2101):
        world.update()
        if frame % 140 == 0: # 打印关键帧状态
            z_col = get_col_by_x(int(zombie.x))
            print(f"[Frame {frame:4}] 僵尸位置: {zombie.x:6.2f} | 所在列: {z_col} | 僵尸 HP: {zombie.hp:3}")

    print(f"=== 模拟结束 ===")


if __name__ == "__main__":
    simple_battle_example()
```

### 预期输出

```text
=== 战斗开始 ===
植物初始 HP: 300, 僵尸初始 HP: 270
[Frame  140] 僵尸位置: 667.80 | 所在列: 7 | 僵尸 HP: 270
[Frame  280] 僵尸位置: 635.60 | 所在列: 7 | 僵尸 HP: 250
[Frame  420] 僵尸位置: 603.40 | 所在列: 7 | 僵尸 HP: 230
[Frame  560] 僵尸位置: 571.20 | 所在列: 6 | 僵尸 HP: 210
[Frame  700] 僵尸位置: 539.00 | 所在列: 6 | 僵尸 HP: 190
[Frame  840] 僵尸位置: 506.80 | 所在列: 5 | 僵尸 HP: 150
[Frame  980] 僵尸位置: 474.60 | 所在列: 5 | 僵尸 HP: 130
[Frame 1120] 僵尸位置: 442.40 | 所在列: 5 | 僵尸 HP: 110
[Frame 1260] 僵尸位置: 410.20 | 所在列: 4 | 僵尸 HP:  90
[Frame 1400] 僵尸位置: 378.00 | 所在列: 4 | 僵尸 HP:  70
[Frame 1540] 僵尸位置: 345.80 | 所在列: 3 | 僵尸 HP:  50
[Frame 1680] 僵尸位置: 313.60 | 所在列: 3 | 僵尸 HP:  30
[Frame 1820] 僵尸位置: 281.40 | 所在列: 3 | 僵尸 HP:  10
[Frame 1960] 僵尸位置: 265.99 | 所在列: 2 | 僵尸 HP:   0
[Frame 2100] 僵尸位置: 265.99 | 所在列: 2 | 僵尸 HP:   0
=== 模拟结束 ===
```

*(僵尸不断向左移动，豌豆射手发射子弹，命中后僵尸扣除 20 点 HP。)*

---

## 📖 API 接口文档 (`World` 类)

`pvzemu2.world.World` 是与模拟器交互的统一入口。更多示例请参考`example`文件夹下的代码

| 方法接口 | 参数与说明 |
| :--- | :--- |
| `__init__(self, scene_type)` | **初始化世界**。<br>`scene_type`: `SceneType` 枚举，例如 `DAY`, `NIGHT`, `POOL` 等。 |
| `update(self) -> bool` | **执行单帧物理步进**。<br>包含系统级调度（生成、伤害、动画等）。<br>返回 `True` 表示游戏结束（僵尸进家）。 |
| `step(self, frames: int = 1) -> bool` | **向前模拟指定帧数**。<br>通常用于强化学习或快速跳过动画。返回 `True` 表示游戏结束。 |
| `plant(self, plant_type, row, col) -> Plant`| **种植植物**。<br>`plant_type`: `PlantType` 枚举。<br>返回种植成功的 `Plant` 对象，如果该位置不合法或阳光不足则返回 `None`。 |
| `spawn(self, zombie_type, row, x) -> Zombie`| **生成僵尸**。<br>`zombie_type`: `ZombieType` 枚举。<br>`x`: 生成的横坐标（默认 800.0）。返回生成的 `Zombie` 对象。 |
| `remove_plant(self, row, col) -> bool` | **铲除植物**。<br>移除指定网格上的植物，返回 `True` 表示铲除成功。 |
| `get_state(self) -> Dict` | **获取状态字典**。<br>返回当前场景的完整数据快照（包含全部植物、僵尸、子弹坐标及属性）。 |
| `to_json(self) -> str` | **导出 JSON**。<br>将当前状态序列化为 JSON 字符串，方便与其他语言或前端调试器通信。 |
| `reset(self, scene_type=None)` | **重置世界**。<br>清空所有对象并将状态恢复到初始值。 |

---

## 🚧 进度

为了实现完美的 PvZ 模拟，我们对比了 **原版游戏** 以及 `PvZ-Emulator`。
以下是目前的完成度与 TODO 规划：

### 目前进度
* **核心框架**：各场景坐标系转换、对象池复用机制 (`ObjList`)。
* **场景基础**：6种基础场地支持（白天、黑夜、水池、浓雾、屋顶、月夜），水路逻辑支持。
* **战斗系统**：基础植物与僵尸的生成、攻击、受击逻辑。
* **物理机制**：抛物线计算（投手类植物、篮球等）、直线飞行物、屋顶斜坡高度补偿。
* **动画系统**：根据 `Reanim` 数据表准确重构了帧率、移动速度（`_ground` 驱动）、冰冻减速。
* **重构优化**：彻底剥离了 C++ 版中的 UI 和渲染层，提取为纯净的数据驱动 Python 模型。

### 进行中
相比原版游戏，以下子系统在目前模拟器中尚不完善或缺失：

- [ ] **谜题与小游戏**
  - [ ] 砸罐子模式 (Vasebreaker) 的生成与逻辑。
  - [ ] 我是僵尸模式 (I, Zombie) 的大脑判定与计分。
  - [ ] 坚果保龄球 (Wall-nut Bowling) 物理回弹算法补全。
  - [ ] 宝石迷阵 (Beghouled) 消除逻辑。
- [ ] **经济与成就系统**
  - [ ] 完美模拟掉落物（金币、银币、钻石、巧克力、盆栽）的散落轨道与收集。
  - [ ] 全成就触发条件检测。
- [ ] **关卡进程控制**
  - [ ] 严格复刻原版的“权重池”僵尸刷新算法（精准的 Wave / Flag 控制）。

### 未完成
原版模拟器中存在、但在 `pvzemu2` 尚未完全实现的功能：

- [ ] **强化学习接口 (`observation_factory.cpp` 对应功能)**
  - [ ] 提供将 `get_state()` 转换为 Numpy/PyTorch Tensor 矩阵的 Wrapper（用于 Gymnasium）。
  - [ ] 支持动作掩码 (Action Masks) 的生成，以限制非法动作（如在有植物的格子再次种植）。
- [ ] **僵尸博士与雪橇车逻辑**
  - [ ] 原版模拟器因 Survival Endless 模式不存在而忽略了 Dr. Zomboss 和 雪橇车小队 (Bobsled Team)，考虑在 `pvzemu2` 中补全完整逻辑。
- [ ] **C++ 性能扩展加速**
  - [ ] 由于纯 Python 在进行大量碰撞检测时性能有限，未来计划使用 `pybind11` 或 `Cython` 将核心循环 (Update Loop) 再次下放至 C++ 以提升训练速度。
  

## 🌳 植物系统 (Plant System) 覆盖情况

核心逻辑（生成、计时器、攻击判定、伤害处理）已在 `PlantSystem` 和 `DamageSystem` 中实现，大部分植物的**状态机更新**和**发射逻辑**已通过子系统实现。

### 🟢 已实现核心逻辑的植物类型

| 植物类型 | 关键实现点 | 覆盖文件 |
| :--- | :--- | :--- |
| **豌豆家族** (Pea Family) | **豌豆射手**、**三线射手**、**寒冰射手**、**机枪射手**、**裂荚射手** 逻辑基础。 | `pea_family.py`, `plant_system.py` |
| **向日葵家族** (Sun Plants) | 阳光生产逻辑（Sun/Twin/Shroom）。 | `sun_plants.py` |
| **蘑菇家族** (Mushroom Family) | **冰蘑菇**（冰冻/睡眠）、**磁力菇**（吸取配件/梯子）、**大喷菇**（穿透伤害）、**阳光菇**（成长）。 | `mushroom_family.py` |
| **倭瓜** (Squash) | 完整的跳跃、锁定目标、着陆、压扁状态机。 | `squash.py` |
| **食人花** (Chomper) | 咬合尝试、成功/失败、咀嚼/吞咽状态机。 | `chomper.py` |
| **土豆雷** (Potato Mine) | 潜伏、出土、布防、触发判定逻辑。 | `potato_mine.py` |
| **三叶草** (Blover) | 激活机制，对气球的清除效果标记（在 `DamageSystem` 中）。 | `blover.py` |
| **玉米投手** (Pults) | 基础抛物线发射逻辑。 | `plant_system.py` |
| **咖啡豆** (Coffee Bean) | 唤醒蘑菇逻辑和自身死亡消失机制。 | `coffee_bean.cpp` |
| **南瓜头** (Pumpkin) | 基础血量与结构定义。 | `shield_plants.cpp` |

### 🟡 仅定义结构/基础实现，逻辑待完善的植物类型
（主要通过 `enums.py` 和 `plant_factory.py` 推断，但缺乏完整的 `Update` 逻辑）

*   **玉米炮 (Cob Cannon)**：基础发射流程和状态机已定义，但可能缺少炮弹飞行和爆炸后的处理。
*   **模仿者 (Imitater)**：变身状态机已定义，但变身后的行为（如发射/攻击）需依赖被模仿植物的系统。
*   **地刺/钢地刺 (Spike Family)**：基础攻击逻辑定义，但可能缺少精确的伤害反馈和计时器同步。
*   **杨桃 (Starfruit)**：发射逻辑已实现，但复杂的五向弹道与碰撞优先级可能需要验证。
*   **墓碑吞噬者 (Grave Buster)**：着陆和摧毁墓碑的逻辑已实现。
*   **叶子保护伞 (Umbrella Leaf)**：基础状态转换已定义。

---

## 🧟 僵尸系统 (Zombie System) 覆盖情况

核心的移动、受击、状态（如冰冻、黄油）处理已实现，特别是与动画和物理相关的 `_ground` 位移表逻辑已基本移植完成。

### 🟢 已实现核心逻辑的僵尸类型
（主要通过 `system/zombie/` 中的独立文件和 `ZombieSystem::update` 推断）

| 僵尸类型 | 关键实现点 | 覆盖文件 |
| :--- | :--- | :--- |
| **基础僵尸** (Normal, Cone, Bucket) | 基础移动、啃食、被冰冻/减速、受到伤害、**掉落配件**（桶/铁桶/报纸）逻辑。 | `common.cpp`, `zombie_system.cpp` |
| **冲浪/雪橇/水池** | **泳尸**、**海豚骑士**的基础水上移动与上岸逻辑。 | `dolphin_rider.cpp`, `snorkel.cpp` |
| **Pogo** (跳跳僵尸) | 基础跳跃状态机和**收起/放下跳跳杆**逻辑。 | `pogo.cpp` |
| **矿工** (Digger) | **挖地/出土**状态机和动画驱动位移（依赖 `_ground`）。 | `digger.cpp` |
| **舞者/伴舞** (Dancer/Backup) | **召唤伴舞**、**相互啃食/伤害**逻辑，以及对减速的共享影响。 | `dancing.cpp` |
| **投石车** (Catapult) | 投掷篮球/坚果的逻辑与射击状态机。 | `catapult.cpp` |
| **巨人** (Gargantuar) | **投掷小鬼**、**砸地**（AOE 伤害）的机制。 | `gargantuar.cpp` |
| **冰车** (Zomboni) | 撞击冰道、撞击植物后的死亡（爆胎）逻辑。 | `zomboni.cpp` |
| **气球** (Balloon) | 飞行与落地状态机。 | `balloon.cpp` |

### 🟡 仅定义结构/基础实现，逻辑待完善的僵尸类型
（主要通过 `enums.py` 和 `zombie_factory.py` 推断，但缺乏独立系统文件）

*   **其他特殊僵尸**：如 **Jack-in-the-Box** (`jack_in_the_box.cpp`) 的爆炸、**Ladder Zombie** (`ladder.cpp`) 的爬梯逻辑等。

---

## ⚠️ 未完成项

### 🔴 遗失/待实现的的功能

| 来源 | 描述 | 影响模块 |
| :--- | :--- | :--- |
| `DamageSystem` | 荆棘植物 (`Spikerock`) 对巨人等高血量单位的伤害结算的精确性。 | `DamageSystem` |
| `DamageSystem` | 磁力菇 (`Magnetshroom`) 能够吸取的更复杂的配件和僵尸类型（例如吸走僵尸携带的杆子）。 | `PlantSystem` |
| `ZombieSystem` | 多数僵尸的**高级状态机**（如 Pogo 的精确跳跃高度、Digger 的挖掘返回值）。 | `ZombieSystem` |
| `ProjectileSystem` | **三线豌豆** (ThreePeater) 和 **星状果** (Starfruit) 的碰撞判定和轨道修正的精确度。 | `ProjectileSystem` |

### 🟠 待完善的 API/集成层
1.  **完整 API 暴露**：`pvzemu2` 核心系统（如 `DamageSystem`, `PlantFactory`, `ZombieSystem`）尚未完全暴露给 Python World 接口。
2.  **状态同步精度**：需要确保原版游戏中帧同步与 Pvzemu2 帧步进的精度匹配。


---

## 📜 许可证 (License)

本项目基于 **MIT License** 开源。

```text
MIT License

Copyright (c) 2026 pvzemu2 Contributors
Copyright (c) 2025 Crescendo and Reisen
Copyright (c) 2020 Testla

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

*声明：本项目仅供学习。所设计的游戏素材、IP等版权归属 PopCap Games / Electronic Arts 所有。*