# Context Map

This repo has multiple domain contexts. Each context has its own `CONTEXT.md` with domain language, models, and invariants.

## Contexts

| Context | Path | Description |
|---------|------|-------------|
| Portfolio Management | `portfolio/CONTEXT.md` | 持仓导入、跟踪、再平衡管理 |
| Analysis Engine | `analysis/CONTEXT.md` | 7 阶段分析流水线、多智能体、投资理论 |
| Data Layer | `data/CONTEXT.md` | 多市场数据适配、缓存策略 |
| Web Dashboard | `web/CONTEXT.md` | Streamlit 可视化 + FastAPI |
| CLI | `cli/CONTEXT.md` | 命令行交互、报告生成 |
| Config | `config/CONTEXT.md` | 全局配置管理 |

## ADR locations

- System-wide ADRs: `docs/adr/`
- Context-specific ADRs: `<context>/docs/adr/`
