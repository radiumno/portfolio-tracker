"""测试持仓 CSV 加载器"""

import io
import os
import tempfile

import pytest
from portfolio.models import Position, AssetType, MarketType
from portfolio.loader import load_positions_from_csv


SAMPLE_CSV = """symbol,name,asset_type,shares,cost_price,market,currency
510050,华夏上证50ETF,etf,1000,2.5,cn,CNY
SPY,SPDR S&P 500,etf,50,400.0,us,USD
"""


def test_load_basic_csv():
    buf = io.StringIO(SAMPLE_CSV)
    positions = load_positions_from_csv(buf)
    assert len(positions) == 2
    assert positions[0].symbol == "510050"
    assert positions[0].asset_type == AssetType.ETF
    assert positions[0].market == MarketType.CN
    assert positions[1].symbol == "SPY"
    assert positions[1].market == MarketType.US


def test_load_empty_csv():
    buf = io.StringIO("symbol,name,asset_type,shares,cost_price,market,currency\n")
    positions = load_positions_from_csv(buf)
    assert positions == []


def test_load_file_path():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
        f.write(SAMPLE_CSV)
        tmp_path = f.name
    try:
        positions = load_positions_from_csv(tmp_path)
        assert len(positions) == 2
    finally:
        os.unlink(tmp_path)


def test_load_missing_required_column():
    bad_csv = "symbol,name,shares,cost_price\n510050,test,100,1.0\n"
    buf = io.StringIO(bad_csv)
    with pytest.raises(ValueError, match="缺少必需列"):
        load_positions_from_csv(buf)


def test_load_chinese_headers():
    """CSV 使用中文列名时应通过 COLUMN_MAP 正常加载"""
    csv_data = "代码,名称,类型,份额,成本价,市场,币种\n510050,华夏上证50ETF,etf,1000,2.5,cn,CNY\n"
    buf = io.StringIO(csv_data)
    positions = load_positions_from_csv(buf)
    assert len(positions) == 1
    assert positions[0].symbol == "510050"
