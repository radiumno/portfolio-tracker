"""全球市场数据提供者 — 基于 yfinance"""

from typing import Optional
import pandas as pd
from data.base import BaseDataProvider, DataProviderError


class YFinanceProvider(BaseDataProvider):
    """通过 yfinance 获取全球市场数据"""

    def __init__(self):
        self._yf = None

    def _get_yf(self):
        if self._yf is None:
            try:
                import yfinance as yf
                self._yf = yf
            except ImportError:
                raise DataProviderError("需要安装 yfinance: pip install yfinance")
        return self._yf

    def get_etf_nav(self, symbol: str) -> Optional[pd.Series]:
        try:
            yf = self._get_yf()
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")
            if hist.empty:
                return None
            latest = hist.iloc[-1]
            return pd.Series({
                "nav": float(latest["Close"]),
                "date": str(latest.name.date()),
            }, name=symbol)
        except Exception as e:
            raise DataProviderError(f"获取 ETF 净值失败 {symbol}: {e}")

    def get_etf_daily(self, symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
        try:
            yf = self._get_yf()
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
            if df.empty:
                return None
            df = df.reset_index()
            df = df.rename(columns={
                "Date": "date", "Open": "open", "Close": "close",
                "High": "high", "Low": "low", "Volume": "volume",
            })
            df["date"] = pd.to_datetime(df["date"])
            return df[["date", "open", "close", "high", "low", "volume"]]
        except Exception as e:
            raise DataProviderError(f"获取 ETF 日线失败 {symbol}: {e}")

    def get_fund_nav(self, symbol: str) -> Optional[pd.Series]:
        # yfinance 对主动基金支持有限，回退到 ETF 接口获取
        return self.get_etf_nav(symbol)

    def get_fund_info(self, symbol: str) -> dict:
        try:
            yf = self._get_yf()
            ticker = yf.Ticker(symbol)
            info = ticker.info or {}
            return {
                "name": info.get("longName", info.get("shortName", "")),
                "manager": info.get("fundManager", info.get("managementInfo", "")),
                "management_fee": str(info.get("expenseRatio", "")),
                "inception_date": str(info.get("fundInceptionDate", "")),
                "category": info.get("category", ""),
            }
        except Exception as e:
            raise DataProviderError(f"获取基金信息失败 {symbol}: {e}")

    def get_fund_holdings(self, symbol: str) -> Optional[pd.DataFrame]:
        try:
            yf = self._get_yf()
            ticker = yf.Ticker(symbol)
            holdings = ticker.major_holders
            if holdings is None or holdings.empty:
                # 尝试获取前十大持仓
                top = ticker.top_holdings
                if top is None or top.empty:
                    top = ticker.institutional_holders
                if top is None or top.empty:
                    return None
                holdings = top
            df = holdings.reset_index()
            df.columns = ["holder", "weight"] if len(df.columns) >= 2 else ["weight"]
            return df
        except Exception as e:
            raise DataProviderError(f"获取基金持仓失败 {symbol}: {e}")
