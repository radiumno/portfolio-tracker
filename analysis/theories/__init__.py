"""投资理论引擎 — BaseTheory 抽象基类 + 注册表 + 工厂"""

from abc import ABC, abstractmethod
from portfolio.models import Position
from analysis.models.theory import TheoryResult


class BaseTheory(ABC):
    """投资理论抽象基类。

    所有投资理论实现此接口，通过 TheoryRegistry 统一注册管理。
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """理论英文标识"""
        ...

    @property
    @abstractmethod
    def label(self) -> str:
        """理论中文名称"""
        ...

    @abstractmethod
    def analyze(self, positions: list[Position], **kwargs) -> list[TheoryResult]:
        """对持仓组合运行理论评估，返回每个标的或组合级的评估结果。"""
        ...


class TheoryRegistry:
    """投资理论注册表"""

    def __init__(self):
        self._theories: dict[str, BaseTheory] = {}

    def register(self, theory: BaseTheory) -> None:
        self._theories[theory.name] = theory

    def get(self, name: str) -> BaseTheory:
        if name not in self._theories:
            raise KeyError(f"未知投资理论: {name}")
        return self._theories[name]

    def all(self) -> list[BaseTheory]:
        return list(self._theories.values())

    def run_all(self, positions: list[Position], **kwargs) -> dict[str, list[TheoryResult]]:
        """运行所有已注册的理论，返回 {理论名: 结果列表}"""
        results = {}
        for theory in self._theories.values():
            try:
                results[theory.name] = theory.analyze(positions, **kwargs)
            except Exception as e:
                results[theory.name] = [
                    TheoryResult(
                        theory_name=theory.name,
                        theory_label=theory.label,
                        overall_score=0,
                        summary=f"分析异常: {e}",
                    )
                ]
        return results


def create_registry() -> TheoryRegistry:
    """创建并注册所有内置投资理论"""
    from analysis.theories.value import ValueTheory
    from analysis.theories.growth import GrowthTheory
    from analysis.theories.all_weather import AllWeatherTheory
    from analysis.theories.quant import QuantTheory
    from analysis.theories.behavioral import BehavioralTheory

    registry = TheoryRegistry()
    registry.register(ValueTheory())
    registry.register(GrowthTheory())
    registry.register(AllWeatherTheory())
    registry.register(QuantTheory())
    registry.register(BehavioralTheory())
    return registry


__all__ = [
    "BaseTheory", "TheoryRegistry", "create_registry",
]
