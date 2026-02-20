from pvzemu2.enums import SceneType
from pvzemu2.scene import Scene
from pvzemu2.systems.rng import RNG


class SunSystem:
    MAX_SUN = 9990

    def __init__(self, scene: Scene) -> None:
        self.scene = scene
        self.data = scene.sun
        self.rng = RNG(scene)
        # 初始化第一个阳光的倒计时
        self.data.natural_sun_countdown = self._gen_nature_sun_countdown()

    def _gen_nature_sun_countdown(self) -> int:
        c = self.data.natural_sun_generated * 10 + 425
        return min(c, 950) + self.rng.randint(275)

    def add_sun(self, amount: int) -> None:
        self.data.sun = min(self.MAX_SUN, self.data.sun + amount)

    def update(self) -> None:
        # 仅在白天、水池、屋顶场景自然掉落阳光
        if self.scene.type not in (SceneType.POOL, SceneType.DAY, SceneType.ROOF):
            return

        self.data.natural_sun_countdown -= 1
        if self.data.natural_sun_countdown <= 0:
            self.add_sun(25)
            self.data.natural_sun_generated += 1
            self.data.natural_sun_countdown = self._gen_nature_sun_countdown()
