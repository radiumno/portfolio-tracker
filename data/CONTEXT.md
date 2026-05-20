# Context: Data Layer

## Domain

统一数据抽象层，屏蔽不同市场的差异，提供一致的持仓/行情/基本面数据接口。

## Key Concepts

- **数据提供者（DataProvider）**：实现 `BaseDataProvider` 接口的具体数据源
- **适配器（Adapter）**：将不同数据源（akshare/yfinance/MCP）转换为统一格式
- **中国市场数据**：通过 akshare 获取 A 股基金、港股通 ETF 数据
- **全球市场数据**：通过 yfinance 获取美股 ETF、全球基金数据
- **机构数据**：通过 MCP 连接 Morningstar/Daloopa 等专业数据源
- **缓存（Cache）**：SQLite 本地缓存减少重复请求

## Data Providers

| Provider | Market | Data Types |
|----------|--------|------------|
| AkshareProvider | China (A-shares, HK) | Fund NAV, holdings, sector |
| YFinanceProvider | Global (US, World) | ETF price, holdings, fundamentals |
| MCPProvider | Institutional | Morningstar/Daloopa ratings, analysis |
