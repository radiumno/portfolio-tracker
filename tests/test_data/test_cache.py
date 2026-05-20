# tests/test_data/test_cache.py
"""测试数据提供者接口"""

from data.base import BaseDataProvider, DataProviderError, ProviderRegistry


class MockProvider(BaseDataProvider):
    def get_etf_nav(self, symbol):
        import pandas as pd
        return pd.Series({"nav": 1.0}, name=symbol)

    def get_etf_daily(self, symbol, period="1y"):
        import pandas as pd
        return pd.DataFrame({"close": [1.0, 1.1]})

    def get_fund_nav(self, symbol):
        import pandas as pd
        return pd.Series({"nav": 1.0}, name=symbol)

    def get_fund_info(self, symbol):
        return {"name": "Test", "manager": "Test Mgr"}

    def get_fund_holdings(self, symbol):
        import pandas as pd
        return pd.DataFrame({"stock": ["A"], "weight": [50.0]})


def test_provider_registry():
    registry = ProviderRegistry()
    provider = MockProvider()
    registry.register("mock", provider)
    assert registry.get("mock") is provider


def test_provider_registry_unknown():
    registry = ProviderRegistry()
    try:
        registry.get("nonexistent")
        assert False, "应该抛出异常"
    except DataProviderError:
        pass


def test_mock_provider_interface():
    provider = MockProvider()
    nav = provider.get_etf_nav("510050")
    assert nav is not None
    info = provider.get_fund_info("000001")
    assert info["manager"] == "Test Mgr"
    assert provider.name() == "MockProvider"
