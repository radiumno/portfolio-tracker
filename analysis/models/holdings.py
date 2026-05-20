"""持仓穿透数据模型"""

from pydantic import BaseModel, Field


class HoldingDetail(BaseModel):
    """标的的底层持仓明细（穿透用）"""
    symbol: str = Field(description="底层资产代码")
    name: str = Field(description="底层资产名称")
    weight: float = Field(ge=0, le=100, description="占标的净值比例(%)")
    market_value: float = Field(default=0, ge=0, description="市值")


class SectorExposure(BaseModel):
    """行业暴露"""
    sector: str = Field(description="行业名称")
    weight: float = Field(ge=0, le=100, description="占标的净值比例(%)")
