"""Test portfolio data models."""

from portfolio.models import Position, Portfolio, WatchlistItem, AssetType


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


def test_portfolio_add_position():
    p = Position(symbol="510050", name="上证50", asset_type=AssetType.ETF,
                 shares=1000, cost_price=2.5, market_price=2.8, market="cn")
    portfolio = Portfolio()
    portfolio.add_position(p)
    assert len(portfolio.positions) == 1
    assert portfolio.total_value == 2800.0


def test_portfolio_add_multiple():
    p1 = Position(symbol="A", name="A", asset_type=AssetType.ETF,
                  shares=100, cost_price=10, market_price=12, market="cn")
    p2 = Position(symbol="B", name="B", asset_type=AssetType.ETF,
                  shares=200, cost_price=20, market_price=22, market="us")
    portfolio = Portfolio(positions=[p1, p2])
    portfolio.add_position(p1)
    # After recalc: p1(1200) + p2(4400) + p1 again(1200) = 6800
    assert portfolio.total_value == 6800.0


def test_watchlist_defaults():
    w = WatchlistItem(symbol="QQQ", name="QQQ Trust", asset_type=AssetType.ETF, market="us")
    assert w.priority == 5
    assert w.note == ""


def test_unrealized_pnl_pct_zero_cost():
    p = Position(symbol="X", name="X", asset_type=AssetType.ETF,
                 shares=100, cost_price=0, market_price=10, market="cn")
    assert p.unrealized_pnl_pct == 0.0
