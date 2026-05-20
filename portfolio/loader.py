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
            market_str = row.get("market", "cn").lower()
            # 映射常见的市场名称
            market_map = {
                "china": "cn",
                "us": "us",
                "usa": "us",
                "hongkong": "hk",
                "hong kong": "hk",
            }
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
            raise ValueError(f"解析行 '{row.get('symbol', '?')}' 失败: {e}") from e

    return positions
