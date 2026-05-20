# Context: Config

## Domain

全局配置管理。使用 Pydantic Settings 统一管理所有配置项。

## Key Concepts

- **数据源配置**：akshare/yfinance/MCP 的开关、API keys、超时
- **分析参数**：风险阈值、推荐置信度、标的选择规则
- **UI 配置**：Dashboard 主题、默认视图
- **环境变量**：敏感信息通过 `.env` 注入
