# SPEC: Fund/ETF Smart Analysis System

## 1. Objective

**一句话目标**：用户提交持仓和关注列表，系统通过多智能体辩论 + 投资大师理论分析，输出量化的操作推荐。

**目标用户**：个人投资者（作者自己使用）。

**成功标准**：
- 个人投资者能通过 CLI 或 Web 提交持仓，一键获得完整分析报告
- 分析包含基本面、风险、理论评估、操作建议四个维度
- 每个结论都标注数据来源，每个建议附带风险提示
- 支持 A 股基金和美股 ETF 混合持仓

## 2. Commands

### CLI

```bash
# 安装
pip install -e ".[dev]"

# 分析持仓 CSV
python -m cli.main analyze holdings.csv

# 分析持仓并输出 HTML 报告
python -m cli.main analyze holdings.csv --report --format html

# 查看关注列表
python -m cli.main watchlist

# 仅运行指定阶段
python -m analysis.pipeline --portfolio holdings.csv --stages P1,P2,P3

# 指定分析器分析单只 ETF
python -m analysis.agents.etf_analyzer --ticker 510050 --market cn

# 测试
pytest tests/ -v
pytest tests/test_analysis/ -v -k "test_etf"
```

### Web

```bash
# 启动 Streamlit Dashboard
streamlit run web/dashboard/app.py

# 启动 FastAPI
uvicorn web.api.main:app --reload
```

## 3. Project Structure

```
fund/
├── portfolio/                 # 持仓管理
│   ├── __init__.py
│   ├── models.py              # Position, Watchlist 数据模型
│   ├── loader.py              # CSV / 手动输入导入
│   └── tracker.py             # 收益跟踪、再平衡提醒
│
├── analysis/                  # 核心分析引擎
│   ├── __init__.py
│   ├── pipeline.py            # LangGraph 7 阶段编排
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── etf_analyzer.py    # 跟踪误差/费率/流动性/折溢价
│   │   ├── fund_analyzer.py   # 经理评价/Brinson归因/风格漂移
│   │   ├── risk_analyzer.py   # 波动率/回撤/VaR/CVaR
│   │   ├── concentration.py   # 集中度 HHI
│   │   ├── correlation.py     # 相关性矩阵
│   │   ├── stress_test.py     # 历史情景模拟
│   │   ├── debaters.py        # 3 阶段辩论引擎
│   │   └── decision.py        # 最终决策引擎
│   ├── theories/
│   │   ├── __init__.py
│   │   ├── base.py            # BaseTheory ABC
│   │   ├── value_investing.py
│   │   ├── growth_investing.py
│   │   ├── all_weather.py
│   │   ├── quant_factors.py
│   │   └── behavioral.py
│   └── models/
│       ├── __init__.py
│       ├── holdings.py
│       ├── analysis.py
│       ├── recommendations.py
│       └── risk.py
│
├── data/
│   ├── __init__.py
│   ├── base.py                # BaseDataProvider ABC
│   ├── cache.py               # SQLite 缓存
│   ├── market.py              # 市场工具函数
│   └── providers/
│       ├── __init__.py
│       ├── akshare_provider.py   # 中国市场
│       ├── yfinance_provider.py  # 全球市场
│       └── mcp_provider.py       # MCP 连接器
│
├── config/
│   ├── __init__.py
│   ├── settings.py            # Pydantic Settings
│   └── default.yaml
│
├── web/
│   ├── dashboard/
│   │   ├── app.py
│   │   ├── pages/
│   │   │   ├── portfolio.py
│   │   │   ├── analysis.py
│   │   │   ├── risk.py
│   │   │   └── history.py
│   │   └── components/
│   └── api/
│       ├── __init__.py
│       ├── main.py
│       ├── portfolio.py
│       ├── analysis.py
│       └── report.py
│
├── cli/
│   ├── __init__.py
│   ├── main.py                # Typer 入口
│   ├── commands/
│   │   ├── analyze.py
│   │   ├── report.py
│   │   └── watchlist.py
│   └── reports/
│       ├── html_renderer.py
│       └── text_renderer.py
│
├── refs/tradingagents/        # TradingAgents 参考源码
├── tests/
│   ├── test_analysis/
│   ├── test_data/
│   └── test_portfolio/
└── docs/
    ├── superpowers/specs/
    ├── agents/
    └── adr/
```

## 4. Code Style

- **Python 3.11+**，类型注解全覆盖
- **Pydantic v2** 用于所有数据模型
- **ABC + Protocol** 用于接口定义（`BaseDataProvider`、`BaseTheory`）
- 函数/方法长度控制在 50 行以内，超出拆分为辅助函数
- 文件命名：snake_case
- 类名：PascalCase
- 避免使用全局变量，配置通过 `config/settings.py` 注入
- 异常使用自定义异常类（`AnalysisError`、`DataProviderError`）
- 所有 public 函数/方法写 docstring（中文，一行概括用途）
- 不写多余的注释，代码本身表达意图

### 接口风格示例

```python
class BaseDataProvider(ABC):
    @abstractmethod
    def get_etf_nav(self, ticker: str) -> pd.Series: ...

    @abstractmethod
    def get_fund_holdings(self, fund_code: str) -> pd.DataFrame: ...

class BaseTheory(ABC):
    @abstractmethod
    def analyze(self, positions: list[Position], market: MarketData) -> TheoryResult: ...
```

## 5. Testing Strategy

- **pytest** 作为测试框架
- **pytest-cov** 覆盖率报告
- 测试目录结构镜像源码：

```
tests/
├── test_analysis/
│   ├── test_etf_analyzer.py
│   ├── test_fund_analyzer.py
│   ├── test_risk_analyzer.py
│   ├── test_debaters.py
│   └── test_pipeline.py
├── test_data/
│   ├── test_base.py
│   ├── test_providers.py
│   └── test_cache.py
└── test_portfolio/
    ├── test_models.py
    └── test_loader.py
```

**测试原则：**
- 数据层：mock 外部 API（akshare/yfinance），测试适配器逻辑和缓存
- 分析引擎：使用固定样本数据测试计算逻辑的正确性
- 辩论/决策：使用 mock LLM 输出测试流程编排
- 标的级别：每只标的独立测试
- 组合级别：组合分析函数需要测试边界条件（空持仓、单标的）

**覆盖率目标**：核心计算逻辑（ETF/基金/风险分析器）>= 90%，整体 >= 70%

## 6. Boundaries

### 绝对规则（Always Do）

| # | 规则 |
|---|------|
| 1 | **AI 只给建议，不自动交易** — 所有推荐输出需用户手动确认才能执行 |
| 2 | **显示数据来源** — 每个分析结论都要标注数据源（akshare/yfinance/MCP） |
| 3 | **附带风险提示** — 每个操作建议必须包含"投资有风险，此建议仅供参考"类声明 |
| 4 | **所有输入数据本地化** — 不将用户持仓数据发送到外部服务 |
| 5 | **类型注解全覆盖** — 所有 public 函数参数和返回值必须标注类型 |

### 需询问后执行（Ask First）

- 引入新的外部数据源或 MCP 连接器
- 添加需要存储个人身份信息的特性
- 改变核心分析流水线的 7 阶段顺序
- 引入 LLM 自动执行操作的能力

### 不纳入范围（Never Do）

- 实际交易执行（下单、撤单）
- 用户账户资金管理
- 提供投资建议的法律责任声明替代
- 未经用户同意的数据收集或分析
