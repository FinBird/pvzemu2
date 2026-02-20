from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pvzemu2.scene import Scene


class IcePathSystem:
    def __init__(self, scene: 'Scene') -> None:
        self.scene = scene
        self.data = scene.ice_path

    def update(self) -> None:
        """
        更新冰道状态。
        对应 C++: ice_path::update
        """
        for i in range(self.scene.rows):
            if self.data.countdown[i] > 0:
                self.data.countdown[i] -= 1
                if self.data.countdown[i] == 0:
                    # 倒计时结束，冰道消失（重置X坐标到屏幕外）
                    self.data.x[i] = 800
