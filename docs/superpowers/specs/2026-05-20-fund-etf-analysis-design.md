# Fund/ETF Smart Analysis System — Design Spec

## Overview

智能基金/ETF 分析系统。用户提交持仓和关注列表，系统通过 7 阶段分析流水线（数据采集→标的体检→组合分析→理论评估→辩论→风控→推荐），结合多智能体辩论和投资大师理论，输出量化的操作建议。

## Architecture

```
                    用户交互层
    ┌─────────────────────┐  ┌──────────────────┐
    │   Streamlit Dash     │  │  Claude Code     │
    │   (Web 可视化)       │  │  (AI 对话式)     │
    └─────────┬───────────┘  └────────┬─────────┘
              │ HTTP/REST             │ 本地调用
              ▼                       ▼
    ┌────────────────────────────────────────────┐
    │           FastAPI 服务层                    │
    │  /api/portfolio /api/analyze /api/report   │
    └────────────────────┬───────────────────────┘
                         │
    ┌────────────────────▼───────────────────────┐
    │        分析引擎 (LangGraph Pipeline)        │
    │  P1→P2→P3→P4→P5→P6→P7                     │
    └────────────────────┬───────────────────────┘
                         │
    ┌────────────────────▼───────────────────────┐
    │  数据层 (适配器模式)                        │
    │  akshare | yfinance | MCP | CSV            │
    └────────────────────────────────────────────┘
```

## Project Structure

```
fund/
├── portfolio/                   # 持仓管理（独立模块）
│   ├── models.py                # 持仓/关注列表数据模型
│   ├── loader.py                # CSV/API/手动导入
│   └── tracker.py               # 收益跟踪、再平衡提醒
│
├── analysis/                    # 核心分析引擎
│   ├── __init__.py
│   ├── pipeline.py              # LangGraph 7 阶段流水线编排
│   ├── agents/                  # 多智能体系统
│   │   ├── __init__.py
│   │   ├── etf_analyzer.py      # ETF 分析器（跟踪误差/费率/流动性/折溢价）
│   │   ├── fund_analyzer.py     # 基金分析器（经理评价/Brinson 归因/风格漂移）
│   │   ├── risk_analyzer.py     # 风险分析器（波动率/回撤/VaR）
│   │   ├── concentration.py     # 集中度分析
│   │   ├── correlation.py       # 相关性分析
│   │   ├── stress_test.py       # 压力测试
│   │   ├── debaters.py          # 辩论引擎（持仓结构/调仓/优先级辩论）
│   │   └── decision.py          # 最终决策引擎
│   ├── theories/                # 投资理论（可插拔）
│   │   ├── __init__.py
│   │   ├── base.py              # BaseTheory 抽象基类
│   │   ├── value_investing.py   # 价值投资（Graham/Buffett）
│   │   ├── growth_investing.py  # 成长投资（Fisher/Lynch）
│   │   ├── all_weather.py       # 全天候（Dalio）
│   │   ├── quant_factors.py     # 量化因子（动量/质量/低波）
│   │   └── behavioral.py        # 行为金融（偏差检测）
│   └── models/                  # 数据模型
│       ├── __init__.py
│       ├── holdings.py           # 持仓相关
│       ├── analysis.py           # 分析结果
│       ├── recommendations.py    # 操作推荐
│       └── risk.py               # 风险指标
│
├── data/                        # 数据层
│   ├── __init__.py
│   ├── base.py                  # BaseDataProvider 抽象接口
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── akshare_provider.py  # 中国 A 股/基金数据
│   │   ├── yfinance_provider.py # 美股/全球 ETF 数据
│   │   └── mcp_provider.py      # MCP 数据连接器
│   ├── cache.py                 # SQLite 缓存
│   └── market.py                # 市场数据工具函数
│
├── web/                         # Streamlit Dashboard
│   ├── dashboard/
│   │   ├── app.py               # 主应用
│   │   ├── pages/
│   │   │   ├── portfolio.py     # 持仓概览
│   │   │   ├── analysis.py      # 分析结果
│   │   │   ├── risk.py          # 风险仪表盘
│   │   │   └── history.py       # 历史追踪
│   │   └── components/          # 可复用组件
│   └── api/
│       ├── main.py              # FastAPI 入口
│       ├── portfolio.py         # 持仓 API
│       ├── analysis.py          # 分析 API
│       └── report.py            # 报告 API
│
├── cli/                         # 交互式 CLI
│   ├── main.py                  # Typer 入口
│   ├── commands/
│   │   ├── analyze.py           # fund analyze
│   │   ├── report.py            # fund report
│   │   └── watchlist.py         # fund watch
│   └── reports/
│       ├── html_renderer.py     # HTML 报告
│       └── text_renderer.py     # 文本报告
│
├── config/                      # 配置管理
│   ├── settings.py              # Pydantic Settings
│   └── default.yaml             # 默认配置
│
├── refs/                        # 参考项目源码
│   ├── tradingagents/           # TradingAgents (原 _tmp_*.py)
│   └── financial-services/      # Anthropic FSI 参考
│
├── notebooks/                   # Jupyter 探索
├── scripts/                     # 工具脚本
├── tests/                       # 测试
│   ├── test_analysis/
│   ├── test_data/
│   └── test_portfolio/
│
├── docs/                        # 文档
│   ├── adr/
│   ├── agents/
│   └── superpowers/specs/
│
├── CONTEXT-MAP.md
├── CLAUDE.md
└── pyproject.toml
```

## Data Flow

```
用户输入持仓 CSV/API
        │
        ▼
┌─────────────────────────────────────────────────────┐
│ Phase 1: 数据采集 (并行)                              │
│ ETF: yfinance → 净值/跟踪误差/费率/成交量/折溢价        │
│ 基金: akshare → 持仓穿透/经理/历史/同类排名            │
│ 宏观: akshare → 市场资金流向/利率/行业表现              │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│ Phase 2: 标的体检 (每个标的独立分析)                   │
│ ETF: 跟踪偏离度、费率侵蚀模型、流动性评分               │
│ 基金: Brinson 归因、风格漂移检测、同类百分位             │
│ 风险: 波动率/最大回撤/VaR/CVaR                        │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│ Phase 3: 组合分析                                     │
│ 相关性矩阵 → 风险分解 → 集中度检查 → 压力测试          │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│ Phase 4: 投资理论评估 (并行)                           │
│ 价值 | 成长 | 全天候 | 量化因子 | 行为金融              │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│ Phase 5: 辩论引擎                                     │
│ 辩论1: 持仓结构合理性                                   │
│ 辩论2: 哪些标的要调仓                                   │
│ 辩论3: 操作优先级                                      │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│ Phase 6: 风险评估                                     │
│ 下行风险 | 流动性 | 集中度 | 宏观                      │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│ Phase 7: 操作推荐                                     │
│ 标的级别: 买入/卖出/持有/加仓/减仓 + 仓位比例          │
│ 组合级别: 优先级排序 + 调整后组合模拟                  │
└──────────────────────────────────────────────────────┘
```

## Financial Analysis Design

### 1. ETF Analyzer

核心指标计算：

```python
class ETFAnalysis:
    tracking_error: float          # 跟踪偏离年化标准差
    expense_ratio: float           # 管理费率
    bid_ask_spread: float          # 买卖价差
    premium_discount: float        # 折溢价率
    daily_volume: float            # 日均成交量
    sector_exposure: dict          # 行业暴露
    top_holdings: list             # 前十大持仓
    concentration: float           # 持仓集中度 (HHI)
```

### 2. Fund Analyzer (主动基金)

```python
class FundAnalysis:
    # 经理评价
    manager_tenure: int
    manager_past_performance: pd.Series
    manager_style: str              # 投资风格标签
    
    # 业绩归因 (Brinson)
    allocation_effect: float        # 资产配置贡献
    selection_effect: float         # 选股贡献
    interaction_effect: float       # 交互效应
    
    # 风格漂移
    style_drift_score: float        # 风格漂移得分
    actual_style: str               # 实际持仓风格
    declared_style: str             # 招募说明书风格
    
    # 同类排名
    percentile_1y: float
    percentile_3y: float
    percentile_5y: float
```

### 3. Portfolio Risk Decomposition

```python
class PortfolioRisk:
    covariance_matrix: np.ndarray    # 协方差矩阵
    marginal_risk: dict              # 边际风险贡献
    component_var: dict              # 成分 VaR
    diversification_ratio: float     # 分散化比率
    effective_n: int                 # 有效持仓数 (Herfindahl)
    
    # Stress Tests
    scenarios: list[ScenarioResult]  # 历史情景模拟
```

### 4. Multi-Agent Debate Structure

辩论采用 **3 阶段辩论制**，每阶段 LLM 驱动：

```
辩论1: 持仓结构合理性
├── 正方（现状派）: 当前配置符合长期目标
├── 反方（调仓派）: 需要再平衡
└── 裁决: 总体判定 + 问题点列表

辩论2: 逐标的审视
├── 逐一检视每个持仓
├── 双方：持有 vs 调出/调减
└── 裁决: 每个标的的操作建议

辩论3: 优先级排序
├── 综合考虑风险、收益、确定性
├── 排定操作优先级
└── 裁决: 有序的操作计划
```

### 5. Recommendation Output Schema

```python
class Recommendation:
    # 组合级别
    portfolio_score: float            # 综合评分 1-100
    risk_level: str                   # 低/中/高
    diversification_grade: str        # A/B/C/D
    rebalance_urgency: str            # 紧迫度
    
    # 标的级别
    actions: list[Action]             # 操作列表
    # Action: symbol, name, action_type (buy/sell/hold/add/reduce),
    #         current_weight, target_weight, confidence,
    #         reason (理论引用), priority
    
    # 调整模拟
    projected_impact: dict            # 调整后的预期影响
```

## Implementation Priority

### Phase 1: Core Engine (MVP)
1. `analysis/models/` — 数据模型
2. `data/base.py` + `data/providers/` — 数据层
3. `analysis/agents/etf_analyzer.py` — ETF 分析
4. `analysis/agents/fund_analyzer.py` — 基金分析
5. `analysis/pipeline.py` — 流水线骨架

### Phase 2: Analysis Depth
6. `analysis/agents/risk_analyzer.py` — 风险分析
7. `analysis/agents/correlation.py` — 相关性
8. `analysis/agents/concentration.py` — 集中度
9. `analysis/theories/` — 投资理论

### Phase 3: AI Debate
10. `analysis/agents/debaters.py` — 辩论引擎
11. `analysis/agents/decision.py` — 决策引擎

### Phase 4: Interfaces
12. `cli/` — 命令行
13. `web/api/` — REST API
14. `web/dashboard/` — Dashboard
