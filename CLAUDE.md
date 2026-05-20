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
│   │   ├── etf_analyzer.py       # ETF 分析（跟踪误差、集中度）
│   │   ├── fund_analyzer.py      # 主动基金分析（夏普、回撤）
│   │   ├── risk_analyzer.py      # VaR/CVaR/波动率/回撤/Beta
│   │   ├── correlation.py        # 相关性矩阵/滚动相关/聚类
│   │   ├── concentration.py      # HHI/有效数/行业集中度
│   │   ├── stress_test.py        # 5 预设压力场景
│   │   └── debate.py             # 3 阶段 AI 辩论（DeepSeek Flash）
│   ├── theories/             # 投资理论
│   │   ├── value.py              # 价值投资（Graham/Buffett）
│   │   ├── growth.py             # 成长投资（Fisher/Lynch）
│   │   ├── all_weather.py        # 全天候（Dalio 风险平价）
│   │   ├── quant.py              # 量化多因子（动量/质量/低波/规模）
│   │   └── behavioral.py         # 行为金融（偏差检测）
│   └── models/               # Pydantic 数据模型
├── data/                     # 数据层（适配器模式）
│   ├── llm.py                # DeepSeek/OpenAI 兼容 LLM 客户端
│   └── providers/            # akshare / yfinance / MCP
├── cli/                      # Typer 交互式 CLI
│   ├── main.py               # 入口（analyze/report 子命令）
│   └── commands/
│       ├── analyze.py        # 分析 + Rich 可视化
│       └── report.py         # JSON 报告导出
├── config/                   # Pydantic Settings 配置管理
│   └── settings.py           # FUND_DEEPSEEK_API_KEY 等
├── tests/                    # 75 个测试
├── .env                      # API Key（不进版本控制）
└── docs/
    ├── agents/               # 技能配置
    └── superpowers/
        ├── specs/            # 设计文档
        └── plans/            # 实施计划
```

### 层间依赖

```
portfolio → analysis → data → (CLI / Web API)
```

每一层通过抽象接口通信，核心逻辑不依赖具体数据源。

## Analysis Pipeline (7 Stages)

| Phase | Name | Status | Description |
|-------|------|--------|-------------|
| P1 | 数据采集 | ✅ | 并行获取 ETF/基金数据（akshare/yfinance） |
| P2 | 标的体检 | ✅ | ETF（跟踪误差）/ 基金（夏普/回撤） |
| P3 | 组合分析 | ✅ | 相关性矩阵、HHI 集中度、压力测试 |
| P4 | 理论评估 | ✅ | 5 大投资理论并行评估 |
| P5 | 辩论引擎 | ✅ | DeepSeek Flash：结构/调仓/优先级 |
| P6 | 风险评估 | ✅ | VaR/CVaR/波动率/集中度评级 |
| P7 | 操作推荐 | ✅ | 综合评分 + 逐标的建议 |

## Key Technologies

- **Python 3.11+** — 主语言
- **DeepSeek API** — 辩论引擎 LLM（Flash 标准模型）
- **Pydantic** — 数据模型与结构化输出
- **Rich + Typer** — 交互式 CLI
- **Pandas / NumPy** — 数据分析与金融计算
- **httpx** — LLM API 调用
- **akshare / yfinance** — 数据源

## Key Commands

```bash
# 安装
pip install -e ".[dev]"

# CLI 分析
python -m cli.main analyze holdings.csv

# JSON 报告导出
python -m cli.main report holdings.csv -o report.json

# 测试
pytest tests/ -v
pytest tests/test_analysis/ -v -k "test_etf or test_risk"
pytest tests/test_analysis/test_theories.py -v
```

## Configuration

- `config/settings.py` — Pydantic Settings，环境变量前缀 `FUND_`
- `.env` — `FUND_DEEPSEEK_API_KEY=sk-xxx`（不进版本控制）
- 默认使用 DeepSeek Flash 模型（`deepseek-chat`，非 R1）

## Investment Theories

每个理论实现 `BaseTheory` 接口，在 `analysis/theories/__init__.py` 注册：

```python
class BaseTheory(ABC):
    @abstractmethod
    def analyze(self, positions: list[Position], **kwargs) -> list[TheoryResult]: ...
```

注册表工厂: `create_registry()` 创建含全部 5 个理论的 `TheoryRegistry`。

## 3-Stage Debate

1. **Stage 1** — 组合结构合理性评估（保守派 vs 进取派）
2. **Stage 2** — 逐标调仓方案辩论
3. **Stage 3** — 优先级排序与最终裁决

无需 API Key 时自动跳过，不影响流水线。

## Data Sources

| 市场 | 数据源 | 获取方式 |
|------|--------|---------|
| A 股/中国基金| akshare | `pip install akshare` |
| 美股/全球 ETF | yfinance | `pip install yfinance` |
| LLM 辩论 | DeepSeek API | `.env` 配置 `FUND_DEEPSEEK_API_KEY` |

## Project-Level Configuration

- `config/settings.py` — Pydantic Settings 配置模型
- `.env` — API keys（不进版本控制）
- `pyproject.toml` — 项目元数据与依赖
