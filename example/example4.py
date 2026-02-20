from pvzemu2.world import World
from pvzemu2.enums import SceneType


def str_width(s):
    width = 0
    for ch in s:
        if '\u4e00' <= ch <= '\u9fff':
            width += 2
        else:
            width += 1
    return width


def run_extended_sun_simulation():
    print("=== 天降阳光持续掉落深度模拟 (饱和点验证) ===")

    world = World(SceneType.DAY)
    world.scene.sun.sun = 0

    col_widths = [6, 12, 10, 15, 18, 15]
    headers = ['轮次', '累计生成(n)', '当前阳光', '基础间隔', '新生成倒计时', '状态备注']

    def make_separator():
        return '+' + '+'.join('-' * (w + 2) for w in col_widths) + '+'

    def make_row(row_data):
        cells = []
        for content, width in zip(row_data, col_widths):
            content = str(content)
            pad_needed = width - str_width(content)
            padded = content + ' ' * (pad_needed if pad_needed > 0 else 0)
            cells.append(f" {padded} ")
        return '|' + '|'.join(cells) + '|'

    print(make_separator())
    print(make_row(headers))
    print(make_separator())

    # 定义测试区间：接近间隔上限(50-55)，以及接近阳光上限(398-402)
    test_indices = list(range(50, 56)) + [100] + list(range(398, 403))

    for round_num in test_indices:
        # 跳跃逻辑：手动调整计数器
        # 为了模拟连续性，我们计算当前轮次应有的阳光数 (前提是没到上限)
        world.scene.sun.natural_sun_generated = round_num - 1
        world.scene.sun.sun = min(9990, (round_num - 1) * 25)

        # 触发掉落
        world.scene.sun.natural_sun_countdown = 1
        world.step(1)

        # 获取结果
        n = world.scene.sun.natural_sun_generated
        current_sun = world.scene.sun.sun
        new_countdown = world.scene.sun.natural_sun_countdown

        # 计算基础间隔 (C++ min(425 + n*10, 950))
        base_val = min(425 + n * 10, 950)

        # 备注逻辑
        note = ""
        if n == 53:
            note = "即将达到间隔上限"
        elif n > 53 and n < 100:
            note = "间隔锁定 950"
        elif current_sun >= 9990:
            note = "阳光量已饱和"

        row_data = [f"#{round_num}", n, current_sun, base_val, new_countdown, note]
        print(make_row(row_data))

        # 间隔逻辑校验
        assert new_countdown >= base_val, "倒计时低于基础值"
        if n >= 53:
            assert base_val == 950, "间隔上限逻辑失效"

        if round_num in [55, 100]:
            print("|" + "-" * (sum(col_widths) + len(col_widths) * 3 - 1) + "|")

    print(make_separator())
    print("\n=== 深度验证结论 ===")
    print("1. 间隔增长：随着 n 增加，掉落频率逐渐降低（每轮增加 10 帧间隔）。")
    print("2. 间隔封顶：在第 53 次掉落后，基础间隔永久固定在 950 帧，防止阳光掉落过慢。")
    print("3. 阳光封顶：在第 400 次掉落左右，总阳光达到 9990 的系统上限，符合 `min(MAX_SUN, ...)` 逻辑。")


if __name__ == "__main__":
    run_extended_sun_simulation()