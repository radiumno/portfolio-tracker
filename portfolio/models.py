"""持仓和关注列表数据模型"""

from enum import Enum
from pydantic import BaseModel, Field


class AssetType(str, Enum):
    """标的类型"""
    ETF = "etf"
    FUND = "fund"  # 主动管理基金
    STOCK = "stock"
    BOND = "bond"
    REIT = "reit"


class MarketType(str, Enum):
    CN = "cn"
    US = "us"
    HK = "hk"


class Position(BaseModel):
    """单个持仓"""
    symbol: str = Field(description="标的代码")
    name: str = Field(description="标的名称")
    asset_type: AssetType = Field(description="标的类型")
    shares: float = Field(ge=0, description="持有份额")
    cost_price: float = Field(ge=0, description="成本价")
    market_price: float = Field(default=0.0, ge=0, description="当前市价")
    market: MarketType = Field(description="上市市场")
    currency: str = Field(default="CNY", description="币种")

    @property
    def market_value(self) -> float:
        return self.shares * self.market_price

    @property
    def cost_basis(self) -> float:
        return self.shares * self.cost_price

    @property
    def unrealized_pnl(self) -> float:
        return self.market_value - self.cost_basis

    @property
    def unrealized_pnl_pct(self) -> float:
        if self.cost_basis == 0:
            return 0.0
        return round(self.unrealized_pnl / self.cost_basis, 4)

class Portfolio(BaseModel):
    """整个组合

    注意：
    - 持仓应通过 add_position() 方法修改，以自动触发市值重算。
    - 直接修改 positions 列表不会触发重算，可能导致 total_value 不一致。
    """
    positions: list[Position] = Field(default_factory=list)
    cash: float = Field(default=0.0, ge=0, description="现金余额")
    total_value: float = Field(default=0.0, ge=0, description="总市值")

    def add_position(self, position: Position) -> None:
        self.positions.append(position)
        self._recalc()

    def _recalc(self) -> None:
        self.total_value = sum(p.market_value for p in self.positions) + self.cash


class WatchlistItem(BaseModel):
    """关注列表中的单个标的"""
    symbol: str = Field(description="标的代码")
    name: str = Field(description="标的名称")
    asset_type: AssetType = Field(description="标的类型")
    market: MarketType = Field(description="上市市场")
    priority: int = Field(default=5, ge=1, le=10, description="关注优先级 1-10")
    note: str = Field(default="", description="备注")
