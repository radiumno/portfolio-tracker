"""相关性分析数据模型"""

from typing import Optional
from pydantic import BaseModel, Field


class CorrelationPair(BaseModel):
    """相关系数对"""
    symbol_a: str
    symbol_b: str
    correlation: float = Field(default=0.0, ge=-1, le=1, description="皮尔逊相关系数")
    rolling_correlation: Optional[float] = Field(default=None, description="60 日滚动相关系数")


class CorrelationMatrix(BaseModel):
    """相关系数矩阵结果"""
    symbols: list[str] = Field(default_factory=list)
    matrix: list[list[float]] = Field(default_factory=list, description="N×N 相关系数矩阵")
    pairs: list[CorrelationPair] = Field(default_factory=list)
    avg_correlation: float = Field(default=0.0, ge=-1, le=1, description="平均两两相关系数")
    cluster_info: dict[str, list[str]] = Field(default_factory=dict, description="相关性聚类分组")
