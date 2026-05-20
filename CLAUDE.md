# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

基金/ETF 智能分析系统 — 提交持仓和关注列表，通过 7 阶段分析流水线 + 多智能体辩论 + 投资大师理论，给出操作推荐。支持中国市场（A 股基金/港股通 ETF）和全球市场（美股 ETF/全球基金）。

## Architecture

```
fund/
├── portfolio/                # 持仓管理（导入/跟踪/再平衡提醒）
├── analysis/                 # 核心分析引擎
│   ├── agents/               # ETF/基金/风险/相关性/辩论/决策
│   ├── theories/             # 价值/成长/全天候/量化/行为金融
│   └── models/               # Pydantic 数据模型
├── data/                     # 数据层（适配器模式）
│   └── providers/            # akshare / yfinance / MCP
├── web/                      # Streamlit + FastAPI
├── cli/                      # Typer 交互式 CLI
├── config/                   # Pydantic Settings 配置管理
├── refs/                     # 参考项目源码（TradingAgents 等）
├── tests/                    # 测试
└── docs/                     # 设计文档 + ADR
```

### 层间依赖

```
portfolio → analysis → data → (CLI / Web API / MCP)
```

每一层通过抽象接口通信，核心逻辑不依赖具体数据源。

## Analysis Pipeline (7 Stages)

| Phase | Name | Description |
|-------|------|-------------|
| P1 | 数据采集 | 并行获取 ETF/基金/宏观数据 |
| P2 | 标的体检 | 每只标的分独立分析（ETF/基金/风险） |
| P3 | 组合分析 | 相关性、风险分解、集中度、压力测试 |
| P4 | 理论评估 | 5 大投资理论并行评估 |
| P5 | 辩论引擎 | 3 阶段辩论（结构/调仓/优先级） |
| P6 | 风险评估 | 下行/流动性/集中度/宏观风险 |
| P7 | 操作推荐 | 量化操作建议 + 仓位比例 + 优先级 |

## Key Technologies

- **Python 3.11+** — 主语言
- **LangGraph** — 多智能体流水线编排
- **FastAPI** — REST API
- **Streamlit** — Dashboard
- **Pydantic** — 数据模型与结构化输出
- **Rich + Typer** — 交互式 CLI
- **Pandas / NumPy** — 数据分析与金融计算
- **akshare / yfinance** — 数据源
- **SQLite** — 缓存

## Development Workflow

### 分析引擎开发

```bash
# 运行完整分析流水线
python -m analysis.pipeline --portfolio holdings.csv

# 运行指定阶段
python -m analysis.pipeline --stages P1,P2 --watchlist watch.csv

# 运行单个分析器
python -m analysis.agents.etf_analyzer --ticker 510050
```

### 投资理论

每个理论实现 `BaseTheory` 接口，在 `analysis/theories/__init__.py` 注册：

```python
class BaseTheory(ABC):
    @abstractmethod
    def analyze(self, positions: list[Position], market: MarketData) -> TheoryResult: ...
```

## Key Commands

```bash
# 安装
pip install -e ".[dev]"

# CLI 分析
python -m cli.main analyze holdings.csv

# CLI 生成报告
python -m cli.main report --format html

# 启动 Dashboard
streamlit run web/dashboard/app.py

# 启动 API
uvicorn web.api.main:app --reload

# 测试
pytest tests/ -v
pytest tests/test_analysis/ -v -k "test_etf"
```

## Reference Projects

源码缓存于 `refs/tradingagents/`：

- **TauricResearch/TradingAgents** — 多智能体交易框架（LangGraph 编排、结构化输出 Schema、对抗辩论机制）
- **anthropics/financial-services** — Claude for Financial Services（Skill 体系、MCP 连接器模式）

## Data Sources

| 市场 | 数据源 | 获取方式 |
|------|--------|---------|
| A 股/中国基金 | akshare | `pip install akshare` |
| 美股/全球 ETF | yfinance | `pip install yfinance` |
| 机构级数据 | MCP connectors | Morningstar/Daloopa/FactSet |

## Agent skills

### Issue tracker

Issues live as GitHub issues on `radiumno/portfolio-tracker`. See `docs/agents/issue-tracker.md`.

### Triage labels

Five canonical labels: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Multi-context repo — `CONTEXT-MAP.md` at root points to per-context `CONTEXT.md` files. See `docs/agents/domain.md`.

## Project-Level Configuration

- `config/settings.py` — Pydantic Settings 配置模型
- `config/default.yaml` — 默认配置
- `.env` — API keys（不进版本控制）
- `pyproject.toml` — 项目元数据与依赖
