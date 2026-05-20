"""数据提供者抽象层 — 适配器模式"""

from abc import ABC, abstractmethod
from typing import Optional
import pandas as pd


class DataProviderError(Exception):
    """数据源异常基类"""
    pass


class BaseDataProvider(ABC):
    """数据提供者抽象基类"""

    @abstractmethod
    def get_etf_nav(self, symbol: str) -> Optional[pd.Series]:
        """获取 ETF 净值序列"""
        ...

    @abstractmethod
    def get_etf_daily(self, symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """获取 ETF 日线 OHLCV 数据"""
        ...

    @abstractmethod
    def get_fund_nav(self, symbol: str) -> Optional[pd.Series]:
        """获取基金净值序列"""
        ...

    @abstractmethod
    def get_fund_info(self, symbol: str) -> dict:
        """获取基金基本信息（经理、规模、费率等）"""
        ...

    @abstractmethod
    def get_fund_holdings(self, symbol: str) -> Optional[pd.DataFrame]:
        """获取基金持仓明细"""
        ...

    def name(self) -> str:
        return self.__class__.__name__


class ProviderRegistry:
    """数据提供者注册表"""

    def __init__(self):
        self._providers: dict[str, BaseDataProvider] = {}

    def register(self, name: str, provider: BaseDataProvider) -> None:
        self._providers[name] = provider

    def get(self, name: str) -> BaseDataProvider:
        if name not in self._providers:
            raise DataProviderError(f"未知数据提供者: {name}")
        return self._providers[name]

    def all(self) -> list[BaseDataProvider]:
        return list(self._providers.values())
