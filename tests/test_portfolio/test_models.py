"""Test portfolio data models."""

from portfolio.models import Position, WatchlistItem, AssetType


def test_position_creation():
    p = Position(
        symbol="510050",
        name="华夏上证50ETF",
        asset_type=AssetType.ETF,
        shares=1000,
        cost_price=2.5,
        market_price=2.8,
        market="cn",
    )
    assert p.market_value == 2800.0
    assert p.cost_basis == 2500.0
    assert p.unrealized_pnl == 300.0
    assert p.unrealized_pnl_pct == 0.12


def test_position_zero_shares():
    p = Position(
        symbol="SPY",
        name="SPDR S&P 500 ETF",
        asset_type=AssetType.ETF,
        shares=0,
        cost_price=400.0,
        market_price=420.0,
        market="us",
    )
    assert p.market_value == 0.0
    assert p.unrealized_pnl == 0.0


def test_watchlist_item():
    w = WatchlistItem(symbol="QQQ", name="Invesco QQQ Trust", asset_type=AssetType.ETF, market="us")
    assert w.symbol == "QQQ"


def test_position_invalid_type():
    from pydantic import ValidationError
    import pytest

    with pytest.raises(ValidationError):
        Position(
            symbol="XXX",
            name="Test",
            asset_type="invalid",  # type: ignore
            shares=100,
            cost_price=10.0,
            market_price=11.0,
            market="cn",
        )
