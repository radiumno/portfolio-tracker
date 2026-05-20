"""分析结果数据模型"""

from typing import Optional
from pydantic import BaseModel, Field
from analysis.models.holdings import HoldingDetail, SectorExposure


class ETFAnalysisResult(BaseModel):
    """ETF 分析结果"""
    symbol: str
    name: str
    tracking_error: float = Field(default=0.0, description="跟踪偏离年化标准差(%)")
    expense_ratio: float = Field(default=0.0, description="管理费率(%)")
    bid_ask_spread: Optional[float] = Field(default=None, description="买卖价差(bp)")
    premium_discount: Optional[float] = Field(default=None, description="折溢价率(%)")
    daily_volume: float = Field(default=0, description="日均成交量(元)")
    nav_price: float = Field(default=0.0, description="最新净值")
    holdings: list[HoldingDetail] = Field(default_factory=list)
    sector_exposure: list[SectorExposure] = Field(default_factory=list)
    concentration: float = Field(default=0.0, description="持仓集中度 HHI")
    data_source: str = Field(default="", description="数据来源")


class FundAnalysisResult(BaseModel):
    """主动基金分析结果"""
    symbol: str
    name: str
    manager_name: str = Field(default="", description="基金经理")
    manager_tenure: float = Field(default=0, description="任职年限")
    nav_return_1y: float = Field(default=0.0, description="近 1 年收益(%)")
    nav_return_3y: float = Field(default=0.0, description="近 3 年收益(%)")
    max_drawdown_1y: float = Field(default=0.0, description="近 1 年最大回撤(%)")
    sharpe_ratio: float = Field(default=0.0, description="夏普比率")
    style_label: str = Field(default="", description="投资风格标签")
    holdings: list[HoldingDetail] = Field(default_factory=list)
    sector_exposure: list[SectorExposure] = Field(default_factory=list)
    data_source: str = Field(default="", description="数据来源")
