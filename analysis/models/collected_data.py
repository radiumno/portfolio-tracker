"""P1 数据采集结果模型"""

from typing import Optional
import pandas as pd
from pydantic import BaseModel, Field, ConfigDict
from portfolio.models import MarketType


class AssetCollectedData(BaseModel):
    """单个标的采集到的原始数据"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    symbol: str
    name: str
    nav: Optional[pd.Series] = Field(default=None, description="净值序列")
    daily: Optional[pd.DataFrame] = Field(default=None, description="日线 OHLCV")
    info: dict = Field(default_factory=dict, description="基本信息")
    holdings: Optional[list[dict]] = Field(default=None, description="持仓明细")
    data_source: str = ""


class CollectedData(BaseModel):
    """P1 阶段采集的全部数据"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    assets: dict[str, AssetCollectedData] = Field(default_factory=dict)
    benchmark_nav: Optional[pd.Series] = Field(default=None, description="基准指数净值")
