# Context: Portfolio Management

## Domain

用户持仓和关注列表的管理模块。负责数据导入、收益跟踪、再平衡提醒。

## Key Concepts

- **持仓 (Position)**：标的代码、名称、类型（ETF/基金）、持有份额、成本价、当前市值
- **关注列表 (Watchlist)**：用户关注的标的高低，含优先级标记
- **数据导入 (Loader)**：支持 CSV 导入、手动输入、API 同步
- **收益跟踪 (Tracker)**：持仓收益/亏损、累计收益、浮动盈亏
- **再平衡提醒 (Rebalance Alert)**：偏离目标配置时自动提醒
