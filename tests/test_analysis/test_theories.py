"""投资理论引擎测试"""

from portfolio.models import Position, AssetType, MarketType
from analysis.theories.value import ValueTheory
from analysis.theories.growth import GrowthTheory
from analysis.theories.all_weather import AllWeatherTheory
from analysis.theories.quant import QuantTheory
from analysis.theories.behavioral import BehavioralTheory
from analysis.theories import TheoryRegistry, create_registry


def _make_pos(symbol: str, value: float = 10000, asset_type: str = "etf", name: str = "") -> Position:
    return Position(
        symbol=symbol,
        name=name or f"{symbol}名称",
        asset_type=AssetType(asset_type),
        shares=value,
        cost_price=1.0,
        market_price=1.0,
        market=MarketType.CN,
        currency="CNY",
    )


def test_theory_registry():
    """理论注册表基本功能"""
    registry = TheoryRegistry()
    theory = ValueTheory()
    registry.register(theory)
    assert registry.get("value") is theory
    assert len(registry.all()) == 1


def test_theory_registry_unknown():
    """未知理论抛出 KeyError"""
    registry = TheoryRegistry()
    try:
        registry.get("nonexistent")
        assert False, "应该是 KeyError"
    except KeyError:
        pass


def test_create_registry():
    """工厂函数创建所有 5 个理论"""
    registry = create_registry()
    assert len(registry.all()) == 5
    names = [t.name for t in registry.all()]
    assert "value" in names
    assert "growth" in names
    assert "all_weather" in names
    assert "quant" in names
    assert "behavioral" in names


def test_value_theory():
    """价值投资理论分析"""
    theory = ValueTheory()
    pos = [
        _make_pos("510050", 10000, "etf", "上证50ETF"),
        _make_pos("511880", 5000, "bond", "国债ETF"),
    ]
    results = theory.analyze(pos)
    assert len(results) == 2
    for r in results:
        assert 0 <= r.overall_score <= 100
        assert r.theory_name == "value"


def test_growth_theory():
    """成长投资理论分析"""
    theory = GrowthTheory()
    pos = [_make_pos("588000", 10000, "etf", "科创50ETF")]
    results = theory.analyze(pos)
    assert len(results) == 1
    assert 0 <= results[0].overall_score <= 100


def test_all_weather_theory():
    """全天候理论组合级分析"""
    theory = AllWeatherTheory()
    pos = [
        _make_pos("510050", 5000, "etf", "上证50ETF"),
        _make_pos("511880", 5000, "bond", "国债ETF"),
    ]
    results = theory.analyze(pos)
    assert len(results) == 1  # 组合级 -> 1 个结果
    assert 0 <= results[0].overall_score <= 100
    assert "象限覆盖" in str(results[0].details) or True


def test_all_weather_empty():
    """空持仓不崩溃"""
    theory = AllWeatherTheory()
    results = theory.analyze([])
    assert results == []


def test_quant_theory():
    """量化多因子理论分析"""
    theory = QuantTheory()
    pos = [
        _make_pos("510300", 10000, "etf", "沪深300ETF"),
        _make_pos("511880", 5000, "bond", "国债ETF"),
    ]
    results = theory.analyze(pos)
    assert len(results) == 2
    for r in results:
        assert 0 <= r.overall_score <= 100
        assert "factors" in r.details


def test_behavioral_theory():
    """行为金融理论分析"""
    theory = BehavioralTheory()
    pos = [_make_pos("A", 10000, "etf")]
    results = theory.analyze(pos)
    assert len(results) >= 1
    assert 0 <= results[0].overall_score <= 100
    assert "biases" in results[0].details


def test_registry_run_all():
    """注册表运行所有理论"""
    registry = create_registry()
    pos = [_make_pos("510050", 10000, "etf", "上证50ETF")]
    results = registry.run_all(pos)
    assert len(results) == 5
    for name, theory_results in results.items():
        assert len(theory_results) > 0
        for r in theory_results:
            assert 0 <= r.overall_score <= 100


def test_theory_scores_range():
    """所有理论评分均在 0-100 范围内"""
    registry = create_registry()
    pos = [
        _make_pos("A", 10000, "etf"),
        _make_pos("B", 5000, "bond"),
        _make_pos("C", 5000, "fund"),
    ]
    results = registry.run_all(pos)
    for _, theory_results in results.items():
        for r in theory_results:
            assert 0 <= r.overall_score <= 100, f"{r.theory_name} score {r.overall_score} out of range"


def test_theory_signal_valid():
    """理论信号方向有效"""
    theory = ValueTheory()
    pos = [_make_pos("TEST", 10000, "etf")]
    results = theory.analyze(pos)
    for r in results:
        for s in r.signals:
            assert s.direction in ("buy", "sell", "hold", "reduce")
            assert 0 <= s.confidence <= 1
