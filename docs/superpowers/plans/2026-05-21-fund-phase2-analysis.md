# Phase 2: Advanced Analysis Engine Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development to implement task-by-task. Steps use checkbox syntax.

**Goal:** Implement risk analysis (VaR/CVaR), correlation matrix, concentration analysis, stress testing, and 5 investment theories — wiring them into the 7-stage pipeline.

**Architecture:** Pure functions and Pydantic models for each analysis component. Theories follow BaseTheory ABC with registry pattern. All analysis functions accept data explicitly (no hidden data fetching) for testability.

**Tech Stack:** Python 3.11+, Pandas, NumPy, Pydantic v2

---

### Task 1: Risk Analysis Models

**Files:**
- Create: `analysis/models/risk.py`
- Modify: `analysis/models/__init__.py`

**Models:**

```python
# analysis/models/risk.py
from pydantic import BaseModel, Field
from typing import Optional


class VaRResult(BaseModel):
    """VaR 计算结果"""
    parametric_95: float = Field(default=0.0, description="参数法 VaR 95% (%)")
    parametric_99: float = Field(default=0.0, description="参数法 VaR 99% (%)")
    historical_95: float = Field(default=0.0, description="历史法 VaR 95% (%)")
    historical_99: float = Field(default=0.0, description="历史法 VaR 99% (%)")
    cvar_95: float = Field(default=0.0, description="CVaR 95% (%)")
    cvar_99: float = Field(default=0.0, description="CVaR 99% (%)")


class DrawdownInfo(BaseModel):
    """回撤信息"""
    max_drawdown: float = Field(default=0.0, description="最大回撤(%)")
    current_drawdown: float = Field(default=0.0, description="当前回撤(%)")
    avg_drawdown: float = Field(default=0.0, description="平均回撤(%)")
    drawdown_days: int = Field(default=0, description="回撤持续天数")
    recovery_days: int = Field(default=0, description="恢复天数")


class RiskMetrics(BaseModel):
    """单一资产风险指标"""
    symbol: str
    name: str
    volatility: float = Field(default=0.0, description="年化波动率(%)")
    downside_volatility: float = Field(default=0.0, description="下行波动率(%)")
    var: VaRResult = Field(default_factory=VaRResult)
    drawdown: DrawdownInfo = Field(default_factory=DrawdownInfo)
    beta: Optional[float] = Field(default=None, description="Beta 系数")
    alpha: Optional[float] = Field(default=None, description="Alpha 系数(%)")
    data_source: str = ""


class PortfolioRiskResult(BaseModel):
    """组合风险分析结果"""
    portfolio_volatility: float = Field(default=0.0, description="组合年化波动率(%)")
    portfolio_var: VaRResult = Field(default_factory=VaRResult)
    diversification_ratio: float = Field(default=0.0, description="分散化比率")
    asset_risks: list[RiskMetrics] = Field(default_factory=list)
```

### Task 2: Correlation Models

**Files:**
- Create: `analysis/models/correlation.py`
- Modify: `analysis/models/__init__.py`

```python
# analysis/models/correlation.py
from pydantic import BaseModel, Field
from typing import Optional


class CorrelationPair(BaseModel):
    """相关系数对"""
    symbol_a: str
    symbol_b: str
    correlation: float = Field(default=0.0, ge=-1, le=1, description="皮尔逊相关系数")
    rolling_correlation: Optional[float] = Field(default=None, description="滚动相关系数(60日)")


class CorrelationMatrix(BaseModel):
    """相关系数矩阵结果"""
    symbols: list[str] = Field(default_factory=list)
    matrix: list[list[float]] = Field(default_factory=list, description="NxN 相关系数矩阵")
    pairs: list[CorrelationPair] = Field(default_factory=list)
    avg_correlation: float = Field(default=0.0, ge=-1, le=1, description="平均相关系数")
    cluster_info: dict[str, list[str]] = Field(default_factory=dict, description="聚类分组")
```

### Task 3: Theory/Stress Test Models

**Files:**
- Create: `analysis/models/theory.py`
- Modify: `analysis/models/__init__.py`

```python
# analysis/models/theory.py
from pydantic import BaseModel, Field
from typing import Optional, Literal


class TheorySignal(BaseModel):
    """理论给出的具体信号"""
    direction: Literal["buy", "sell", "hold", "reduce"]
    reason: str
    confidence: float = Field(default=0.0, ge=0, le=1)


class TheoryResult(BaseModel):
    """投资理论评估结果"""
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
    shock_pct: dict[str, float] = Field(default_factory=dict, description="对各资产的冲击幅度(%)")
    impact_pct: float = Field(default=0.0, description="对组合的冲击(%)")


class StressTestResult(BaseModel):
    """压力测试结果"""
    scenarios: list[StressTestScenario] = Field(default_factory=list)
    worst_case_loss: float = Field(default=0.0, description="最坏损失(%)")
    resilient_assets: list[str] = Field(default_factory=list, description="抗压资产")
    vulnerable_assets: list[str] = Field(default_factory=list, description="脆弱资产")
```

### Task 4: BaseTheory Interface + Registry

**Files:**
- Create: `analysis/theories/__init__.py` (overwrite)
- Modify: `analysis/__init__.py` if needed

```python
# analysis/theories/__init__.py
from abc import ABC, abstractmethod
from typing import Optional
from portfolio.models import Position
from analysis.models.theory import TheoryResult


class BaseTheory(ABC):
    """投资理论抽象基类"""
    
    @property
    @abstractmethod
    def name(self) -> str: ...
    
    @property
    @abstractmethod
    def label(self) -> str: ...
    
    @abstractmethod
    def analyze(self, positions: list[Position], **kwargs) -> TheoryResult: ...


class TheoryRegistry:
    """理论注册表"""
    def __init__(self):
        self._theories: dict[str, BaseTheory] = {}
    
    def register(self, theory: BaseTheory) -> None:
        self._theories[theory.name] = theory
    
    def get(self, name: str) -> BaseTheory: ...
    
    def all(self) -> list[BaseTheory]: ...
    
    def run_all(self, positions: list[Position], **kwargs) -> list[TheoryResult]: ...


# 所有理论在一处注册
from analysis.theories.value import ValueTheory
from analysis.theories.growth import GrowthTheory
from analysis.theories.all_weather import AllWeatherTheory
from analysis.theories.quant import QuantTheory
from analysis.theories.behavioral import BehavioralTheory

def create_registry() -> TheoryRegistry:
    registry = TheoryRegistry()
    registry.register(ValueTheory())
    registry.register(GrowthTheory())
    registry.register(AllWeatherTheory())
    registry.register(QuantTheory())
    registry.register(BehavioralTheory())
    return registry
```

### Task 5: Risk Analyzer Implementation

**Files:**
- Create: `analysis/agents/risk_analyzer.py`
- Modify: `analysis/agents/__init__.py`

Implementation: VaR (parametric=normal assumption, historical percentile), CVaR (mean of tail), drawdown analysis, volatility (annualized), downside volatility (only negative returns).

### Task 6: Correlation Analyzer

**Files:**
- Create: `analysis/agents/correlation.py`
- Modify: `analysis/agents/__init__.py`

Pearson correlation matrix, 60-day rolling correlation, average correlation, simple clustering by correlation threshold (>0.7 = same cluster).

### Task 7: Concentration Analyzer

**Files:**
- Create: `analysis/agents/concentration.py`
- Modify: `analysis/agents/__init__.py`

Portfolio-level HHI (sum of squared weights), sector concentration (by sector weight), top-N concentration, effective N (1/HHI).

### Task 8: Stress Test Engine

**Files:**
- Create: `analysis/agents/stress_test.py`
- Modify: `analysis/agents/__init__.py`

Predefined scenarios: 2008-style crash (-50% equities), 2022-style correction (-20%), inflation shock, rate hike shock. Apply shocks to position market values.

### Task 9: Value Theory

**Files:**
- Create: `analysis/theories/value.py`

Graham/Buffett metrics: P/E ratio, P/B ratio, dividend yield, ROE. Score based on value metrics thresholds.

### Task 10: Growth Theory

**Files:**
- Create: `analysis/theories/growth.py`

Fisher/Lynch metrics: EPS growth rate, revenue growth, PEG ratio. Score based on growth trajectory.

### Task 11: All-Weather Theory

**Files:**
- Create: `analysis/theories/all_weather.py`

Dalio risk parity: check asset allocation across growth/inflation quadrants. Score based on diversification across regimes.

### Task 12: Quant Theory

**Files:**
- Create: `analysis/theories/quant.py`

Multi-factor: momentum (6-month return), quality (ROE, debt/equity), low volatility, size. Score based on factor exposure.

### Task 13: Behavioral Theory

**Files:**
- Create: `analysis/theories/behavioral.py`

Detect biases: disposition effect (selling winners too early), herding (concentration in popular names), overconfidence (lack of diversification). Score based on bias detection.

### Task 14: Pipeline Integration

**Files:**
- Modify: `analysis/pipeline.py`

Wire P3 (组合分析: correlation + concentration + stress test), P4 (理论评估: run all theories), P6 (风险评估: risk analyzer). Update AnalysisContext with new result fields.

### Task 15: Tests

**Files:**
- Create/Modify: `tests/test_analysis/test_risk_analyzer.py`
- Create: `tests/test_analysis/test_correlation.py`
- Create: `tests/test_analysis/test_concentration.py`
- Create: `tests/test_analysis/test_stress_test.py`
- Create: `tests/test_analysis/test_theories.py`
- Modify: `tests/test_analysis/__init__.py`

Test all 6 new modules: risk metrics (VaR, CVaR, drawdown), correlation (matrix, pairs), concentration (HHI, sector), stress test (scenarios, impact), each theory (at least 1 test per theory).
