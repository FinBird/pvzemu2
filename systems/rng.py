from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pvzemu2.scene import Scene


@dataclass(slots=True)
class RNG:
    """模拟 C++ rng 类，绑定 Scene 实现确定性随机"""
    scene: "Scene"

    def randint(self, n: int) -> int:
        return self.scene.rng.randint(0, n - 1)

    def randfloat(self, a: float, b: float) -> float:
        return self.scene.rng.uniform(a, b)

    def random_weighted_sample(self, weights: list[int | float]) -> int:
        return self.scene.rng.choices(range(len(weights)), weights=weights, k=1)[0]
