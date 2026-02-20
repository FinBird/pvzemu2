from pvzemu2.enums import ZombieType
from pvzemu2.scene import Scene
from pvzemu2.systems.rng import RNG
from pvzemu2.systems.zombie_factory import ZombieFactory


class SpawnSystem:
    def __init__(self, scene: Scene, zombie_factory: ZombieFactory) -> None:
        self.scene = scene
        self.data = scene.spawn
        self.zombie_factory = zombie_factory
        self.rng = RNG(scene)

    def update(self) -> None:
        """初步实现 C++ spawn::update 中 next_spawn_countdown_update 的部分功能"""
        # TODO：这里仅包含初步的波次推进逻辑，后续可完全补齐 C++ 的权重表
        if self.data.countdown_endgame > 0:
            return

        if self.data.countdown_next_wave > 0:
            self.data.countdown_next_wave -= 1

        if self.data.countdown_next_wave == 0:
            # TODO: 后续可接入完整的 C++ gen_spawn_list
            # 这里初步实现：每波生成 5 只不同路线的普通僵尸用于维持引擎闭环
            for _ in range(5):
                self.zombie_factory.create(ZombieType.ZOMBIE)

            self.data.wave += 1

            if self.data.wave == 10:
                self.data.total_flags += 1

            # 重置倒计时（简化版）
            self.data.countdown_next_wave = self.rng.randint(600) + 2500
            self.data.countdown_next_wave_initial = self.data.countdown_next_wave
