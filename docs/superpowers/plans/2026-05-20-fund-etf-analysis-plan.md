# Fund/ETF Smart Analysis System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a personal fund/ETF analysis system where user submits holdings CSV and gets quantified operation recommendations through a 7-stage multi-agent analysis pipeline.

**Architecture:** Modular monolith with 3 layers — data (abstract providers for akshare/yfinance), analysis (LangGraph pipeline with pluggable agents and theories), UI (CLI + Streamlit + FastAPI). All layers communicate through Pydantic models.

**Tech Stack:** Python 3.11+, Pydantic v2, LangGraph, pandas/numpy, akshare, yfinance, Typer (CLI), FastAPI (API), Streamlit (Dashboard).

---

## File Map

### Phase 1 — Core Engine (MVP)

```
Create:
├── config/__init__.py
├── config/settings.py
├── config/default.yaml
├── portfolio/__init__.py
├── portfolio/models.py
├── portfolio/loader.py
├── analysis/__init__.py
├── analysis/models/__init__.py
├── analysis/models/holdings.py
├── analysis/models/analysis.py
├── analysis/models/recommendations.py
├── analysis/models/risk.py
├── data/__init__.py
├── data/base.py
├── data/providers/__init__.py
├── data/providers/akshare_provider.py
├── data/providers/yfinance_provider.py
├── analysis/agents/__init__.py
├── analysis/agents/etf_analyzer.py
├── analysis/agents/fund_analyzer.py
├── analysis/pipeline.py
├── cli/__init__.py
├── cli/main.py
├── cli/commands/__init__.py
├── cli/commands/analyze.py
├── tests/__init__.py
├── tests/conftest.py
├── tests/test_portfolio/test_models.py
├── tests/test_portfolio/test_loader.py
├── tests/test_analysis/test_etf_analyzer.py
├── tests/test_analysis/test_fund_analyzer.py
├── tests/test_data/test_cache.py
├── pyproject.toml
```

### Phase 2 — Advanced Analysis (Future)

```
analysis/agents/risk_analyzer.py
analysis/agents/correlation.py
analysis/agents/concentration.py
analysis/agents/stress_test.py
analysis/theories/base.py
analysis/theories/value_investing.py
analysis/theories/growth_investing.py
analysis/theories/all_weather.py
analysis/theories/quant_factors.py
analysis/theories/behavioral.py
```

### Phase 3 — AI Debate (Future)

```
data/providers/llm_provider.py
analysis/agents/debaters.py
analysis/agents/decision.py
```

### Phase 4 — Interfaces (Future)

```
web/api/main.py
web/api/portfolio.py
web/api/analysis.py
web/dashboard/app.py
cli/commands/report.py
cli/reports/html_renderer.py
cli/reports/text_renderer.py
```

---

### Task 1: Project scaffolding — pyproject.toml and config

**Files:**
- Create: `pyproject.toml`
- Create: `config/__init__.py`
- Create: `config/settings.py`
- Create: `config/default.yaml`

- [ ] **Step 1: Write pyproject.toml**

```toml
[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "fund-analyzer"
version = "0.1.0"
description = "基金/ETF 智能分析系统 — 多智能体辩论 + 投资大师理论分析"
requires-python = ">=3.11"
dependencies = [
    "pydantic>=2.0",
    "pandas>=2.0",
    "numpy>=1.24",
    "pyyaml>=6.0",
    "typer>=0.9",
    "rich>=13.0",
    "httpx>=0.24",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "pytest-asyncio>=0.21",
]
cn = ["akshare>=1.0"]
global = ["yfinance>=0.2"]
all = ["akshare>=1.0", "yfinance>=0.2"]
web = ["streamlit>=1.28", "fastapi>=0.104", "uvicorn>=0.24"]
mcp = ["mcp>=0.1"]

[tool.setuptools.packages.find]
where = ["."]
include = ["config*", "portfolio*", "analysis*", "data*", "cli*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
```

- [ ] **Step 2: Write config/settings.py**

```python
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Project paths
    project_root: Path = Path(__file__).resolve().parent.parent
    data_cache_dir: Path = project_root / ".cache"
    default_config: Path = project_root / "config" / "default.yaml"

    # Data providers
    data_provider_cn: str = "akshare"
    data_provider_global: str = "yfinance"

    # Analysis defaults
    risk_free_rate: float = 0.03
    confidence_threshold: float = 0.6
    max_debate_rounds: int = 2

    # Cache
    cache_ttl_hours: int = 4

    model_config = {"env_prefix": "FUND_", "env_file": ".env"}


settings = Settings()
```

- [ ] **Step 3: Write config/__init__.py**

```python
from config.settings import settings

__all__ = ["settings"]
```

- [ ] **Step 4: Write config/default.yaml**

```yaml
analysis:
  risk_free_rate: 0.03
  confidence_threshold: 0.6
  max_debate_rounds: 2

cache:
  ttl_hours: 4
  backend: sqlite

data:
  providers:
    cn: akshare
    global: yfinance

portfolio:
  default_csv_encoding: utf-8
```

- [ ] **Step 5: Install dev dependencies and verify**

Run: `cd D:/Dev/AiProject/fund && pip install -e ".[dev]" 2>&1 | tail -5`

Run: `python -c "from config.settings import settings; print(settings.project_root)"`
Expected: prints the project root path

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml config/
git commit -m "feat: project scaffolding with pyproject.toml and config"
```

---

### Task 2: Portfolio data models

**Files:**
- Create: `portfolio/__init__.py`
- Create: `portfolio/models.py`
- Test: `tests/test_portfolio/test_models.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_portfolio/test_models.py
"""Test portfolio data models."""

from portfolio.models import Position, WatchlistItem, AssetType


def test_position_creation():
    p = Position(
        symbol="510050",
        name="华夏上证50ETF",
        asset_type=AssetType.ETF,
        shares=1000,
        cost_price=2.5,
        market_price=2.8,
        market="cn",
    )
    assert p.market_value == 2800.0
    assert p.cost_basis == 2500.0
    assert p.unrealized_pnl == 300.0
    assert p.unrealized_pnl_pct == 0.12


def test_position_zero_shares():
    p = Position(
        symbol="SPY",
        name="SPDR S&P 500 ETF",
        asset_type=AssetType.ETF,
        shares=0,
        cost_price=400.0,
        market_price=420.0,
        market="us",
    )
    assert p.market_value == 0.0
    assert p.unrealized_pnl == 0.0


def test_watchlist_item():
    w = WatchlistItem(symbol="QQQ", name="Invesco QQQ Trust", asset_type=AssetType.ETF, market="us")
    assert w.symbol == "QQQ"


def test_position_invalid_type():
    from pydantic import ValidationError
    import pytest

    with pytest.raises(ValidationError):
        Position(
            symbol="XXX",
            name="Test",
            asset_type="invalid",  # type: ignore
            shares=100,
            cost_price=10.0,
            market_price=11.0,
            market="cn",
        )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_portfolio/test_models.py -v`
Expected: ImportError or ModuleNotFoundError (portfolio/models.py doesn't exist yet)

- [ ] **Step 3: Write portfolio/__init__.py**

```python
from portfolio.models import Position, WatchlistItem, AssetType

__all__ = ["Position", "WatchlistItem", "AssetType"]
```

- [ ] **Step 4: Write portfolio/models.py**

```python
"""持仓和关注列表数据模型"""

from enum import Enum
from decimal import Decimal
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

    @property
    def weight(self) -> float:
        """占组合权重（需在 Portfolio 中设置 total_value 后使用）"""
        return 0.0


class Portfolio(BaseModel):
    """整个组合"""
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
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_portfolio/test_models.py -v`
Expected: 4 passed

- [ ] **Step 6: Commit**

```bash
git add portfolio/ tests/test_portfolio/test_models.py
git commit -m "feat: portfolio data models (Position, Portfolio, WatchlistItem)"
```

---

### Task 3: Portfolio CSV loader

**Files:**
- Create: `portfolio/loader.py`
- Create: `tests/test_portfolio/test_loader.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_portfolio/test_loader.py
"""Test portfolio CSV loader."""

import csv
import io
import tempfile
from portfolio.models import Position, AssetType, MarketType
from portfolio.loader import load_positions_from_csv


SAMPLE_CSV = """symbol,name,asset_type,shares,cost_price,market,currency
510050,华夏上证50ETF,etf,1000,2.5,cn,CNY
SPY,SPDR S&P 500,etf,50,400.0,us,USD
"""


def test_load_basic_csv():
    buf = io.StringIO(SAMPLE_CSV)
    positions = load_positions_from_csv(buf)
    assert len(positions) == 2
    assert positions[0].symbol == "510050"
    assert positions[0].asset_type == AssetType.ETF
    assert positions[0].market == MarketType.CN
    assert positions[1].symbol == "SPY"
    assert positions[1].market == MarketType.US


def test_load_empty_csv():
    buf = io.StringIO("symbol,name,asset_type,shares,cost_price,market,currency\n")
    positions = load_positions_from_csv(buf)
    assert positions == []


def test_load_file_path():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
        f.write(SAMPLE_CSV)
        tmp_path = f.name
    try:
        positions = load_positions_from_csv(tmp_path)
        assert len(positions) == 2
    finally:
        import os
        os.unlink(tmp_path)


def test_load_missing_required_column():
    bad_csv = "symbol,name,shares,cost_price\n510050,test,100,1.0\n"
    buf = io.StringIO(bad_csv)
    import pytest
    with pytest.raises(ValueError, match="缺少必需列"):
        load_positions_from_csv(buf)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_portfolio/test_loader.py -v`
Expected: ModuleNotFoundError or ImportError

- [ ] **Step 3: Write portfolio/loader.py**

```python
"""持仓数据导入模块 — 支持 CSV 文件/字符串输入"""

import csv
from pathlib import Path
from io import StringIO, TextIOBase
from typing import Union

from portfolio.models import Position, AssetType, MarketType


REQUIRED_COLUMNS = {"symbol", "name", "asset_type", "shares", "cost_price", "market"}
COLUMN_MAP = {
    "代码": "symbol", "名称": "name", "类型": "asset_type",
    "份额": "shares", "成本价": "cost_price", "市场": "market",
    "币种": "currency",
}


def _normalize_headers(headers: list[str]) -> list[str]:
    return [COLUMN_MAP.get(h, h) for h in headers]


def load_positions_from_csv(source: Union[str, Path, TextIOBase]) -> list[Position]:
    """从 CSV 加载持仓列表。

    支持文件路径（str/Path）或 TextIO 对象（如 StringIO）。
    CSV 必需列：symbol, name, asset_type, shares, cost_price, market
    """
    if isinstance(source, (str, Path)):
        with open(source, "r", encoding="utf-8-sig") as f:
            return _parse_csv(f)
    return _parse_csv(source)


def _parse_csv(fileobj: TextIOBase) -> list[Position]:
    reader = csv.DictReader(fileobj)
    reader.fieldnames = _normalize_headers(reader.fieldnames or [])

    missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
    if missing:
        raise ValueError(f"CSV 缺少必需列: {', '.join(sorted(missing))}")

    positions: list[Position] = []
    for row in reader:
        try:
            row["market"] = row.get("market", "cn").lower()
            market_str = row["market"]
            # Map common market names
            market_map = {"china": "cn", "us": "us", "usa": "us", "hongkong": "hk", "hong kong": "hk"}
            market_str = market_map.get(market_str, market_str)

            pos = Position(
                symbol=row["symbol"].strip(),
                name=row["name"].strip(),
                asset_type=AssetType(row["asset_type"].strip().lower()),
                shares=float(row["shares"]),
                cost_price=float(row["cost_price"]),
                market=MarketType(market_str),
                currency=row.get("currency", "CNY").strip().upper(),
            )
            positions.append(pos)
        except (ValueError, KeyError) as e:
            raise ValueError(f"解析行 '{row.get('symbol', '?')}' 失败: {e}")

    return positions
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_portfolio/test_loader.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add portfolio/loader.py tests/test_portfolio/test_loader.py
git commit -m "feat: portfolio CSV loader with column mapping and validation"
```

---

### Task 4: Analysis data models

**Files:**
- Create: `analysis/__init__.py`
- Create: `analysis/models/__init__.py`
- Create: `analysis/models/holdings.py`
- Create: `analysis/models/analysis.py`

- [ ] **Step 1: Write analysis models**

```python
# analysis/__init__.py
from analysis import models

__all__ = ["models"]
```

```python
# analysis/models/__init__.py
from analysis.models.holdings import HoldingDetail, SectorExposure
from analysis.models.analysis import ETFAnalysisResult, FundAnalysisResult

__all__ = ["HoldingDetail", "SectorExposure", "ETFAnalysisResult", "FundAnalysisResult"]
```

```python
# analysis/models/holdings.py
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
```

```python
# analysis/models/analysis.py
"""分析结果数据模型"""

from pydantic import BaseModel, Field
from analysis.models.holdings import HoldingDetail, SectorExposure


class ETFAnalysisResult(BaseModel):
    """ETF 分析结果"""
    symbol: str
    name: str
    tracking_error: float = Field(default=0.0, description="跟踪偏离年化标准差(%)")
    expense_ratio: float = Field(default=0.0, description="管理费率(%)")
    bid_ask_spread: float = Field(default=0.0, description="买卖价差(bp)")
    premium_discount: float = Field(default=0.0, description="折溢价率(%)")
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
```

- [ ] **Step 2: Write and run verification test**

```python
# Run inline test
from analysis.models.holdings import HoldingDetail, SectorExposure
from analysis.models.analysis import ETFAnalysisResult, FundAnalysisResult

# Test ETF result
etf = ETFAnalysisResult(
    symbol="510050", name="华夏上证50ETF",
    tracking_error=0.5, expense_ratio=0.5,
    data_source="akshare",
)
assert etf.tracking_error == 0.5
assert etf.data_source == "akshare"

# Test Fund result
fund = FundAnalysisResult(
    symbol="000001", name=" Test Fund",
    manager_name="Zhang San", manager_tenure=3.5,
    data_source="akshare",
)
assert fund.manager_tenure == 3.5
assert fund.style_label == ""

print("All model tests passed")
```

Run: `python -c "exec(open('tests/test_models_inline.py').read())"` OR just run inline

- [ ] **Step 3: Commit**

```bash
git add analysis/__init__.py analysis/models/
git commit -m "feat: analysis data models (ETF/Fund analysis results, holdings)"
```

---

### Task 5: Data provider abstraction layer

**Files:**
- Create: `data/__init__.py`
- Create: `data/base.py`
- Create: `data/providers/__init__.py`
- Create: `tests/test_data/test_cache.py`

- [ ] **Step 1: Write data/__init__.py**

```python
from data.base import BaseDataProvider, DataProviderError, ProviderRegistry

__all__ = ["BaseDataProvider", "DataProviderError", "ProviderRegistry"]
```

- [ ] **Step 2: Write data/base.py**

```python
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
```

- [ ] **Step 3: Write data/providers/__init__.py**

```python
from data.providers.akshare_provider import AkshareProvider
from data.providers.yfinance_provider import YFinanceProvider

__all__ = ["AkshareProvider", "YFinanceProvider"]
```

- [ ] **Step 4: Write test for abstract interface**

```python
# tests/test_data/test_cache.py
"""Test data provider interface"""

from data.base import BaseDataProvider, DataProviderError, ProviderRegistry


class MockProvider(BaseDataProvider):
    def get_etf_nav(self, symbol):
        import pandas as pd
        return pd.Series({"nav": 1.0}, name=symbol)

    def get_etf_daily(self, symbol, period="1y"):
        import pandas as pd
        return pd.DataFrame({"close": [1.0, 1.1]})

    def get_fund_nav(self, symbol):
        import pandas as pd
        return pd.Series({"nav": 1.0}, name=symbol)

    def get_fund_info(self, symbol):
        return {"name": "Test", "manager": "Test Mgr"}

    def get_fund_holdings(self, symbol):
        import pandas as pd
        return pd.DataFrame({"stock": ["A"], "weight": [50.0]})


def test_provider_registry():
    registry = ProviderRegistry()
    provider = MockProvider()
    registry.register("mock", provider)
    assert registry.get("mock") is provider


def test_provider_registry_unknown():
    registry = ProviderRegistry()
    try:
        registry.get("nonexistent")
        assert False, "Should have raised"
    except DataProviderError:
        pass


def test_mock_provider_interface():
    provider = MockProvider()
    nav = provider.get_etf_nav("510050")
    assert nav is not None
    info = provider.get_fund_info("000001")
    assert info["manager"] == "Test Mgr"
    assert provider.name() == "MockProvider"
```

Run: `pytest tests/test_data/test_cache.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add data/ tests/test_data/test_cache.py
git commit -m "feat: data provider abstraction with registry pattern"
```

---

### Task 6: Akshare provider (China market)

**Files:**
- Create: `data/providers/akshare_provider.py`

- [ ] **Step 1: Write akshare provider**

```python
"""A股/中国基金数据提供者 — 基于 akshare"""

from typing import Optional
import pandas as pd
from data.base import BaseDataProvider, DataProviderError


class AkshareProvider(BaseDataProvider):
    """通过 akshare 获取中国市场数据"""

    def __init__(self):
        self._akshare = None

    def _get_akshare(self):
        if self._akshare is None:
            try:
                import akshare as ak
                self._akshare = ak
            except ImportError:
                raise DataProviderError("需要安装 akshare: pip install akshare")
        return self._akshare

    def get_etf_nav(self, symbol: str) -> Optional[pd.Series]:
        try:
            ak = self._get_akshare()
            df = ak.fund_etf_hist_em(symbol=symbol, period="daily", start_date="", end_date="", adjust="")
            if df.empty:
                return None
            latest = df.iloc[-1]
            return pd.Series({
                "nav": float(latest.get("收盘价", 0)),
                "date": str(latest.get("日期", "")),
            }, name=symbol)
        except Exception as e:
            raise DataProviderError(f"获取 ETF 净值失败 {symbol}: {e}")

    def get_etf_daily(self, symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
        try:
            ak = self._get_akshare()
            df = ak.fund_etf_hist_em(symbol=symbol, period="daily", start_date="", end_date="", adjust="")
            if df.empty:
                return None
            df = df.rename(columns={
                "日期": "date", "开盘": "open", "收盘": "close",
                "最高": "high", "最低": "low", "成交量": "volume",
            })
            df["date"] = pd.to_datetime(df["date"])
            return df[["date", "open", "close", "high", "low", "volume"]]
        except Exception as e:
            raise DataProviderError(f"获取 ETF 日线失败 {symbol}: {e}")

    def get_fund_nav(self, symbol: str) -> Optional[pd.Series]:
        try:
            ak = self._get_akshare()
            df = ak.fund_open_fund_info_em(symbol=symbol, indicator="单位净值走势")
            if df.empty:
                return None
            latest = df.iloc[-1]
            return pd.Series({
                "nav": float(latest.get("单位净值", 0)),
                "date": str(latest.get("净值日期", "")),
                "accum_nav": float(latest.get("累计净值", 0)),
            }, name=symbol)
        except Exception as e:
            raise DataProviderError(f"获取基金净值失败 {symbol}: {e}")

    def get_fund_info(self, symbol: str) -> dict:
        try:
            ak = self._get_akshare()
            df = ak.fund_open_fund_info_em(symbol=symbol, indicator="基金概况")
            result = {}
            for _, row in df.iterrows():
                item = row.get("item", "")
                value = row.get("value", "")
                if "基金经理" in item:
                    result["manager"] = str(value)
                elif "管理费率" in item:
                    result["management_fee"] = str(value)
                elif "基金规模" in item:
                    result["scale"] = str(value)
                elif "成立日期" in item:
                    result["inception_date"] = str(value)
            result.setdefault("manager", "")
            return result
        except Exception as e:
            raise DataProviderError(f"获取基金信息失败 {symbol}: {e}")

    def get_fund_holdings(self, symbol: str) -> Optional[pd.DataFrame]:
        try:
            ak = self._get_akshare()
            df = ak.fund_portfolio_hold_em(symbol=symbol, date="")
            if df.empty:
                return None
            df = df.rename(columns={
                "股票代码": "stock_code", "股票名称": "stock_name",
                "占净值比例": "weight",
            })
            df["weight"] = pd.to_numeric(df["weight"], errors="coerce")
            return df[["stock_code", "stock_name", "weight"]]
        except Exception as e:
            raise DataProviderError(f"获取基金持仓失败 {symbol}: {e}")
```

- [ ] **Step 2: Write verification test (mock akshare)**

```python
# Inline test — test provider interface doesn't crash on import
from data.providers.akshare_provider import AkshareProvider

provider = AkshareProvider()
assert provider.name() == "AkshareProvider"
print("AkshareProvider import OK")
```

Run: `python -c "from data.providers.akshare_provider import AkshareProvider; p=AkshareProvider(); print(p.name())"`
Expected: `AkshareProvider`

- [ ] **Step 3: Commit**

```bash
git add data/providers/akshare_provider.py
git commit -m "feat: akshare data provider for China market"
```

---

### Task 7: YFinance provider (global market)

**Files:**
- Create: `data/providers/yfinance_provider.py`

- [ ] **Step 1: Write yfinance provider**

```python
"""全球市场数据提供者 — 基于 yfinance"""

from typing import Optional
import pandas as pd
from data.base import BaseDataProvider, DataProviderError


class YFinanceProvider(BaseDataProvider):
    """通过 yfinance 获取全球市场数据"""

    def __init__(self):
        self._yf = None

    def _get_yf(self):
        if self._yf is None:
            try:
                import yfinance as yf
                self._yf = yf
            except ImportError:
                raise DataProviderError("需要安装 yfinance: pip install yfinance")
        return self._yf

    def get_etf_nav(self, symbol: str) -> Optional[pd.Series]:
        try:
            yf = self._get_yf()
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")
            if hist.empty:
                return None
            latest = hist.iloc[-1]
            return pd.Series({
                "nav": float(latest["Close"]),
                "date": str(latest.name.date()),
            }, name=symbol)
        except Exception as e:
            raise DataProviderError(f"获取 ETF 净值失败 {symbol}: {e}")

    def get_etf_daily(self, symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
        try:
            yf = self._get_yf()
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
            if df.empty:
                return None
            df = df.reset_index()
            df = df.rename(columns={
                "Date": "date", "Open": "open", "Close": "close",
                "High": "high", "Low": "low", "Volume": "volume",
            })
            df["date"] = pd.to_datetime(df["date"])
            return df[["date", "open", "close", "high", "low", "volume"]]
        except Exception as e:
            raise DataProviderError(f"获取 ETF 日线失败 {symbol}: {e}")

    def get_fund_nav(self, symbol: str) -> Optional[pd.Series]:
        # yfinance 对主动基金支持有限，回退到 ETF 方式获取
        return self.get_etf_nav(symbol)

    def get_fund_info(self, symbol: str) -> dict:
        try:
            yf = self._get_yf()
            ticker = yf.Ticker(symbol)
            info = ticker.info or {}
            return {
                "name": info.get("longName", info.get("shortName", "")),
                "manager": info.get("fundManager", info.get("managementInfo", "")),
                "management_fee": str(info.get("expenseRatio", "")),
                "inception_date": str(info.get("fundInceptionDate", "")),
                "category": info.get("category", ""),
            }
        except Exception as e:
            raise DataProviderError(f"获取基金信息失败 {symbol}: {e}")

    def get_fund_holdings(self, symbol: str) -> Optional[pd.DataFrame]:
        try:
            yf = self._get_yf()
            ticker = yf.Ticker(symbol)
            holdings = ticker.major_holders
            if holdings is None or holdings.empty:
                # Try top holdings
                top = ticker.top_holdings or ticker.institutional_holders
                if top is None or top.empty:
                    return None
                holdings = top
            df = holdings.reset_index()
            df.columns = ["holder", "weight"] if len(df.columns) >= 2 else ["weight"]
            return df
        except Exception as e:
            raise DataProviderError(f"获取基金持仓失败 {symbol}: {e}")
```

- [ ] **Step 2: Verify import**

Run: `python -c "from data.providers.yfinance_provider import YFinanceProvider; p=YFinanceProvider(); print(p.name())"`
Expected: `YFinanceProvider`

- [ ] **Step 3: Commit**

```bash
git add data/providers/yfinance_provider.py
git commit -m "feat: yfinance data provider for global market"
```

---

### Task 8: ETF Analyzer

**Files:**
- Create: `analysis/agents/__init__.py`
- Create: `analysis/agents/etf_analyzer.py`
- Create: `tests/test_analysis/test_etf_analyzer.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_analysis/test_etf_analyzer.py
"""Test ETF analyzer."""

import pandas as pd
import numpy as np
from analysis.agents.etf_analyzer import analyze_etf, calc_tracking_error, calc_concentration


def test_calc_tracking_error():
    """跟踪误差计算"""
    etf_returns = pd.Series([0.01, 0.02, -0.01, 0.015])
    index_returns = pd.Series([0.012, 0.019, -0.008, 0.016])
    te = calc_tracking_error(etf_returns, index_returns)
    assert te >= 0
    assert isinstance(te, float)


def test_calc_concentration():
    """HHI 集中度计算"""
    weights = [50.0, 30.0, 20.0]
    hhi = calc_concentration(weights)
    # HHI = 50^2 + 30^2 + 20^2 = 2500 + 900 + 400 = 3800
    assert hhi == 3800.0


def test_calc_concentration_single():
    """单一持仓 HHI = 10000"""
    assert calc_concentration([100.0]) == 10000.0


def test_calc_concentration_empty():
    assert calc_concentration([]) == 0.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_analysis/test_etf_analyzer.py -v`
Expected: ImportError

- [ ] **Step 3: Write analysis/agents/__init__.py**

```python
from analysis.agents.etf_analyzer import analyze_etf, calc_tracking_error, calc_concentration

__all__ = ["analyze_etf", "calc_tracking_error", "calc_concentration"]
```

- [ ] **Step 4: Write analysis/agents/etf_analyzer.py**

```python
"""ETF 分析器 — 跟踪误差、费率、流动性、折溢价、集中度"""

from typing import Optional
import pandas as pd
import numpy as np
from analysis.models.analysis import ETFAnalysisResult
from analysis.models.holdings import SectorExposure, HoldingDetail


def calc_tracking_error(etf_returns: pd.Series, index_returns: pd.Series) -> float:
    """计算年化跟踪误差(%) = std(etf_returns - index_returns) * sqrt(252)"""
    diff = etf_returns - index_returns
    if len(diff) < 2:
        return 0.0
    return round(float(diff.std() * np.sqrt(252)), 4)


def calc_concentration(weights: list[float]) -> float:
    """计算 HHI 集中度 = sum(weight^2)（weight 为百分比值）"""
    if not weights:
        return 0.0
    return round(sum(w ** 2 for w in weights), 2)


def analyze_etf(
    symbol: str,
    name: str,
    daily_data: Optional[pd.DataFrame] = None,
    index_data: Optional[pd.DataFrame] = None,
    holdings: Optional[list[dict]] = None,
    expense_ratio: float = 0.0,
    data_source: str = "",
) -> ETFAnalysisResult:
    """执行 ETF 分析。

    Args:
        symbol: ETF 代码
        name: ETF 名称
        daily_data: 日线数据（需含 close 列）
        index_data: 基准指数日线（需含 close 列）
        holdings: 持仓明细列表 [{"name":..., "weight":...}]
        expense_ratio: 管理费率(%)
        data_source: 数据来源名称
    """
    result = ETFAnalysisResult(
        symbol=symbol,
        name=name,
        expense_ratio=expense_ratio,
        data_source=data_source,
    )

    # 跟踪误差
    if daily_data is not None and index_data is not None:
        etf_close = daily_data["close"].dropna()
        idx_close = index_data["close"].dropna()
        common_idx = etf_close.index.intersection(idx_close.index)
        if len(common_idx) > 20:
            etf_ret = etf_close.loc[common_idx].pct_change().dropna()
            idx_ret = idx_close.loc[common_idx].pct_change().dropna()
            result.tracking_error = calc_tracking_error(etf_ret, idx_ret)

    # 波动率
    if daily_data is not None:
        close = daily_data["close"].dropna()
        if len(close) > 20:
            returns = close.pct_change().dropna()
            result.daily_volume = float(daily_data.get("volume", pd.Series([0])).mean())
            result.nav_price = float(close.iloc[-1])

    # 行业和持仓
    if holdings:
        result.holdings = [
            HoldingDetail(name=h["name"], symbol=h.get("symbol", ""), weight=h["weight"])
            for h in holdings if h.get("weight", 0) > 0
        ]
        weights = [h["weight"] for h in holdings if h.get("weight", 0) > 0]
        result.concentration = calc_concentration(weights)

    return result
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_analysis/test_etf_analyzer.py -v`
Expected: 4 passed

- [ ] **Step 6: Commit**

```bash
git add analysis/agents/etf_analyzer.py analysis/agents/__init__.py tests/test_analysis/test_etf_analyzer.py
git commit -m "feat: ETF analyzer with tracking error and concentration"
```

---

### Task 9: Fund Analyzer

**Files:**
- Create: `analysis/agents/fund_analyzer.py`
- Create: `tests/test_analysis/test_fund_analyzer.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_analysis/test_fund_analyzer.py
"""Test fund analyzer."""

import pandas as pd
from analysis.agents.fund_analyzer import analyze_fund, calc_sharpe_ratio, calc_max_drawdown


def test_calc_sharpe_ratio():
    returns = pd.Series([0.01, 0.02, -0.01, 0.015, 0.005])
    sharpe = calc_sharpe_ratio(returns, risk_free=0.03)
    assert isinstance(sharpe, float)


def test_calc_max_drawdown():
    nav = pd.Series([1.0, 1.1, 1.05, 1.2, 1.15, 1.25])
    mdd = calc_max_drawdown(nav)
    assert mdd > 0
    # max drawdown: from 1.1 to 1.05 = -4.55%, or from 1.2 to 1.15 = -4.17%
    # The biggest is from peak 1.2 to trough 1.15 = (1.15-1.2)/1.2 = -4.17%
    assert round(mdd, 2) == 4.17


def test_calc_max_drawdown_flat():
    nav = pd.Series([1.0, 1.0, 1.0])
    assert calc_max_drawdown(nav) == 0.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_analysis/test_fund_analyzer.py -v`
Expected: ImportError

- [ ] **Step 3: Write analysis/agents/fund_analyzer.py**

```python
"""主动基金分析器 — 业绩指标、风格分析"""

from typing import Optional
import pandas as pd
import numpy as np
from analysis.models.analysis import FundAnalysisResult


def calc_sharpe_ratio(returns: pd.Series, risk_free: float = 0.03) -> float:
    """计算年化夏普比率"""
    if len(returns) < 10:
        return 0.0
    excess = returns - risk_free / 252
    if excess.std() == 0:
        return 0.0
    return round(float(excess.mean() / excess.std() * np.sqrt(252)), 4)


def calc_max_drawdown(nav: pd.Series) -> float:
    """计算最大回撤(%)"""
    if len(nav) < 2:
        return 0.0
    rolling_max = nav.expanding().max()
    drawdowns = (nav - rolling_max) / rolling_max
    mdd = abs(float(drawdowns.min()))
    return round(mdd * 100, 2)


def analyze_fund(
    symbol: str,
    name: str,
    nav_data: Optional[pd.Series] = None,
    info: Optional[dict] = None,
    holdings: Optional[list[dict]] = None,
    data_source: str = "",
) -> FundAnalysisResult:
    """执行主动基金分析。

    Args:
        symbol: 基金代码
        name: 基金名称
        nav_data: 净值时间序列
        info: 基金基本信息字典
        holdings: 持仓明细
        data_source: 数据来源
    """
    result = FundAnalysisResult(
        symbol=symbol,
        name=name,
        data_source=data_source,
    )

    if info:
        result.manager_name = info.get("manager", "")
        result.style_label = info.get("style", info.get("category", ""))

    if nav_data is not None and len(nav_data) > 20:
        returns = nav_data.pct_change().dropna()
        result.sharpe_ratio = calc_sharpe_ratio(returns)
        result.max_drawdown_1y = calc_max_drawdown(nav_data)

        # Calculate returns for different periods
        result.nav_return_1y = _calc_period_return(nav_data, 252)
        result.nav_return_3y = _calc_period_return(nav_data, 756)

    return result


def _calc_period_return(nav: pd.Series, trading_days: int) -> float:
    """计算指定交易日数的收益率(%)"""
    if len(nav) < trading_days:
        return 0.0
    start = nav.iloc[-trading_days - 1]
    end = nav.iloc[-1]
    if start == 0:
        return 0.0
    return round(float((end - start) / start * 100), 2)
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_analysis/test_fund_analyzer.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add analysis/agents/fund_analyzer.py tests/test_analysis/test_fund_analyzer.py
git commit -m "feat: fund analyzer with Sharpe ratio and max drawdown"
```

---

### Task 10: Pipeline skeleton and CLI entry point

**Files:**
- Create: `analysis/pipeline.py`
- Create: `cli/main.py`
- Create: `cli/__init__.py`
- Create: `cli/commands/__init__.py`
- Create: `cli/commands/analyze.py`

- [ ] **Step 1: Write analysis/pipeline.py**

```python
"""LangGraph 7 阶段分析流水线"""

from typing import Optional
from portfolio.models import Portfolio
from analysis.models.analysis import ETFAnalysisResult, FundAnalysisResult


class AnalysisContext:
    """贯穿流水线的上下文"""

    def __init__(self, portfolio: Portfolio):
        self.portfolio = portfolio
        self.etf_results: dict[str, ETFAnalysisResult] = {}
        self.fund_results: dict[str, FundAnalysisResult] = {}
        self.phase_outputs: dict[str, dict] = {}


class AnalysisPipeline:
    """7 阶段分析流水线"""

    def __init__(self):
        self.phases = {
            "P1": self._phase_data_collection,
            "P2": self._phase_asset_checkup,
            "P3": self._phase_portfolio_analysis,
            "P4": self._phase_theory_evaluation,
            "P5": self._phase_debate,
            "P6": self._phase_risk_assessment,
            "P7": self._phase_recommendation,
        }

    def run(self, portfolio: Portfolio, stages: Optional[list[str]] = None) -> AnalysisContext:
        """运行指定阶段的分析流水线。

        Args:
            portfolio: 用户持仓
            stages: 要运行的阶段列表，默认全运行
        """
        ctx = AnalysisContext(portfolio)
        target_phases = stages or list(self.phases.keys())

        for phase_name in target_phases:
            if phase_name not in self.phases:
                continue
            phase_fn = self.phases[phase_name]
            ctx.phase_outputs[phase_name] = phase_fn(ctx) or {}

        return ctx

    def _phase_data_collection(self, ctx: AnalysisContext) -> dict:
        """P1: 并行获取所有标的数据"""
        return {"status": "not_implemented"}

    def _phase_asset_checkup(self, ctx: AnalysisContext) -> dict:
        """P2: 每个标的分独立分析"""
        return {"status": "not_implemented"}

    def _phase_portfolio_analysis(self, ctx: AnalysisContext) -> dict:
        """P3: 组合级别的相关性、风险分解"""
        return {"status": "not_implemented"}

    def _phase_theory_evaluation(self, ctx: AnalysisContext) -> dict:
        """P4: 投资理论并行评估"""
        return {"status": "not_implemented"}

    def _phase_debate(self, ctx: AnalysisContext) -> dict:
        """P5: 多智能体辩论"""
        return {"status": "not_implemented"}

    def _phase_risk_assessment(self, ctx: AnalysisContext) -> dict:
        """P6: 风险评估"""
        return {"status": "not_implemented"}

    def _phase_recommendation(self, ctx: AnalysisContext) -> dict:
        """P7: 操作推荐"""
        return {"status": "not_implemented"}
```

- [ ] **Step 2: Write CLI files**

```python
# cli/__init__.py
from cli.main import app
__all__ = ["app"]
```

```python
# cli/commands/__init__.py
from cli.commands.analyze import analyze_cmd
__all__ = ["analyze_cmd"]
```

```python
# cli/commands/analyze.py
"""analyze 子命令"""

from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from portfolio.loader import load_positions_from_csv
from portfolio.models import Portfolio
from analysis.pipeline import AnalysisPipeline

console = Console()


def analyze_cmd(
    csv_path: str = typer.Argument(..., help="持仓 CSV 文件路径"),
    stages: Optional[str] = typer.Option(None, "--stages", help="指定阶段(逗号分隔), 如 P1,P2"),
):
    """分析持仓并输出结果"""
    positions = load_positions_from_csv(csv_path)
    portfolio = Portfolio(positions=positions)
    portfolio._recalc()

    # 显示持仓摘要
    table = Table(title=f"持仓分析 ({len(positions)} 只标的)")
    table.add_column("代码", style="cyan")
    table.add_column("名称")
    table.add_column("类型")
    table.add_column("市值", justify="right")
    table.add_column("盈亏%", justify="right")

    for p in positions:
        pnl_str = f"{p.unrealized_pnl_pct*100:.1f}%"
        table.add_row(p.symbol, p.name, p.asset_type.value,
                      f"{p.market_value:,.0f}", pnl_str)

    console.print(table)
    console.print(f"\n组合总市值: [bold]{portfolio.total_value:,.0f}[/bold]")

    # 运行分析
    target_stages = stages.split(",") if stages else None
    pipeline = AnalysisPipeline()
    ctx = pipeline.run(portfolio, stages=target_stages)

    console.print("\n[green]分析完成[/green]")
    for phase, output in ctx.phase_outputs.items():
        console.print(f"  {phase}: {output.get('status', 'done')}")
```

```python
# cli/main.py
"""Fund Analyzer CLI"""

import typer
from cli.commands.analyze import analyze_cmd

app = typer.Typer(
    name="fund",
    help="基金/ETF 智能分析系统",
)

app.command(name="analyze")(analyze_cmd)


def main():
    app()


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Write inline test**

```python
# Test CLI module imports
from cli.main import app
assert app.info.name == "fund"
print("CLI import OK")

from analysis.pipeline import AnalysisPipeline
p = AnalysisPipeline()
assert len(p.phases) == 7
print("Pipeline import OK")
```

Run: `python -c "exec(open('tests/test_cli_inline.py').read())"` or inline

- [ ] **Step 4: Also need to fix the `_recalc` method in Portfolio - it should be callable directly**

Edit `portfolio/models.py`:
```python
# Make _recalc public
def recalc(self) -> None:
    self.total_value = sum(p.market_value for p in self.positions) + self.cash
```

- [ ] **Step 5: Verify all imports work end-to-end**

Run: `python -c "from cli.main import app; from analysis.pipeline import AnalysisPipeline; from portfolio.loader import load_positions_from_csv; print('All imports OK')"`
Expected: `All imports OK`

- [ ] **Step 6: Commit**

```bash
git add analysis/pipeline.py cli/ tests/test_cli_inline.py
git commit -m "feat: pipeline skeleton and CLI entry point"
```

---

## Summary

**Phase 1 (MVP) — 10 tasks, ~43 files:**

| Task | Files | Tests |
|------|-------|-------|
| 1. Scaffolding | pyproject.toml, config/ | — |
| 2. Portfolio models | portfolio/models.py | 4 tests |
| 3. CSV loader | portfolio/loader.py | 4 tests |
| 4. Analysis models | analysis/models/ | Inline |
| 5. Data abstraction | data/base.py | 3 tests |
| 6. Akshare provider | data/providers/akshare_provider.py | Inline |
| 7. YFinance provider | data/providers/yfinance_provider.py | Inline |
| 8. ETF analyzer | analysis/agents/etf_analyzer.py | 4 tests |
| 9. Fund analyzer | analysis/agents/fund_analyzer.py | 3 tests |
| 10. Pipeline + CLI | analysis/pipeline.py, cli/ | Inline |

**Phase 2-4** (risk analysis, theories, debate, web UI) follow the same TDD pattern.
