"""投资理论评估结果数据模型"""

from typing import Literal, Optional
from pydantic import BaseModel, Field


class TheorySignal(BaseModel):
    """理论给出的具体操作信号"""
    direction: Literal["buy", "sell", "hold", "reduce"]
    reason: str
    confidence: float = Field(default=0.0, ge=0, le=1)


class TheoryResult(BaseModel):
    """投资理论对某个标的或组合的评估结果"""
    theory_name: str
    theory_label: str = Field(default="", description="理论中文名")
    overall_score: float = Field(default=0.0, ge=0, le=100, description="总体评分(0-100)")
    signals: list[TheorySignal] = Field(default_factory=list)
    summary: str = Field(default="", description="结论摘要")
    details: dict = Field(default_factory=dict, description="详细分析数据")


class StressTestScenario(BaseModel):
    """压力测试场景"""
    name: str
    description: str
    shock_pct: dict[str, float] = Field(default_factory=dict, description="各资产的市值冲击幅度(%)")
    impact_pct: float = Field(default=0.0, description="对组合总值的冲击(%)")


class StressTestResult(BaseModel):
    """压力测试结果"""
    scenarios: list[StressTestScenario] = Field(default_factory=list)
    worst_case_loss: float = Field(default=0.0, description="最坏场景损失(%)")
    resilient_assets: list[str] = Field(default_factory=list, description="在所有场景中跌幅最小的资产")
    vulnerable_assets: list[str] = Field(default_factory=list, description="在压力场景中跌幅最大的资产")


class DebateArgument(BaseModel):
    """辩论论点"""
    agent_name: str = Field(description="发言智能体名称")
    position: str = Field(description="立场：赞成/反对/中立")
    content: str = Field(description="论证内容")
    confidence: float = Field(default=0.5, ge=0, le=1, description="置信度")


class DebateRound(BaseModel):
    """一轮辩论"""
    round_number: int
    arguments: list[DebateArgument] = Field(default_factory=list)
    consensus: Optional[str] = Field(default=None, description="本轮共识")
    summary: str = Field(default="", description="本轮摘要")


class DebateResult(BaseModel):
    """辩论引擎输出结果"""
    topic: str
    rounds: list[DebateRound] = Field(default_factory=list)
    final_consensus: str = Field(default="", description="最终共识")
    decision: str = Field(default="", description="最终决策")
    confidence: float = Field(default=0.0, ge=0, le=1, description="决策置信度")
