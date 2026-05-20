# 🧠 Fund Analyzer — 基金/ETF 智能分析系统

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

提交持仓和关注列表，通过 **7 阶段分析流水线 + 多智能体辩论 + 投资大师理论**，输出量化的操作推荐。

支持 **A 股基金**（akshare）和 **美股 ETF**（yfinance）混合持仓。

---

## 快速开始

```bash
# 安装
pip install -e ".[dev,all]"

# 分析持仓 CSV
python -m cli.main analyze holdings.csv

# 运行测试
pytest tests/ -v
```

## 功能特性

| 特性 | 说明 |
|------|------|
| 📊 **多市场支持** | A 股 ETF/基金 + 美股 ETF 混合分析 |
| 🔬 **标的体检** | 跟踪误差、费率侵蚀、流动性、夏普比率、最大回撤 |
| 📈 **组合分析** | 相关性矩阵、集中度 HHI、边际风险贡献、压力测试 |
| 🧠 **投资理论** | 价值投资、成长投资、全天候、量化因子、行为金融 |
| 🗣️ **多智能体辩论** | 3 阶段辩论引擎 — 持仓结构 → 调仓审视 → 优先级排序 |
| 🛡️ **风险评估** | 下行风险、流动性风险、集中度风险、宏观风险 |
| 💻 **多界面** | CLI (Typer) + REST API (FastAPI) + Dashboard (Streamlit) |

## 分析流水线

```
P1 数据采集 → P2 标的体检 → P3 组合分析 → P4 理论评估 → P5 辩论 → P6 风控 → P7 推荐
```

## 数据来源

| 市场 | 数据源 | 安装 |
|------|--------|------|
| A 股/中国基金 | [akshare](https://github.com/akfamily/akshare) | `pip install akshare` |
| 美股/全球 ETF | [yfinance](https://github.com/ranaroussi/yfinance) | `pip install yfinance` |
| 机构级数据 | MCP (Morningstar/Daloopa/FactSet) | `pip install fund[mcp]` |

## 目录结构

```
fund/
├── portfolio/      # 持仓管理（导入/跟踪/再平衡）
├── analysis/       # 核心分析引擎（7 阶段流水线）
│   ├── agents/     # ETF/基金/风险/辩论/决策分析器
│   ├── theories/   # 5 大投资理论实现
│   └── models/     # Pydantic 数据模型
├── data/           # 数据层（适配器模式）
│   └── providers/  # akshare / yfinance / MCP
├── cli/            # Typer 交互式 CLI
├── web/            # FastAPI + Streamlit
├── config/         # Pydantic Settings 配置
└── tests/          # pytest 测试
```

## 安全声明

> **AI 只给建议，不自动交易** — 所有推荐输出需用户手动确认才能执行。
> 每个分析结论都标注数据来源，每个操作建议附带风险提示。
> **投资有风险，此建议仅供参考。**

## 许可证

[MIT](LICENSE)
