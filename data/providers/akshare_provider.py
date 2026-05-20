"""A股/中国基金数据提供者 — 基于 akshare"""

from typing import Optional
import pandas as pd
from data.base import BaseDataProvider, DataProviderError


class AkshareProvider(BaseDataProvider):
    """通过 akshare 获取中国市场数据"""

    def __init__(self):
        self._akshare = None

    def _get_akshare(self):
        if self._akshare is None:
            try:
                import akshare as ak
                self._akshare = ak
            except ImportError:
                raise DataProviderError("需要安装 akshare: pip install akshare")
        return self._akshare

    def get_etf_nav(self, symbol: str) -> Optional[pd.Series]:
        try:
            ak = self._get_akshare()
            df = ak.fund_etf_hist_em(symbol=symbol, period="daily", start_date="", end_date="", adjust="")
            if df.empty:
                return None
            latest = df.iloc[-1]
            return pd.Series({
                "nav": float(latest.get("收盘价", 0)),
                "date": str(latest.get("日期", "")),
            }, name=symbol)
        except Exception as e:
            raise DataProviderError(f"获取 ETF 净值失败 {symbol}: {e}")

    def get_etf_daily(self, symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
        try:
            ak = self._get_akshare()
            df = ak.fund_etf_hist_em(symbol=symbol, period="daily", start_date="", end_date="", adjust="")
            if df.empty:
                return None
            df = df.rename(columns={
                "日期": "date", "开盘": "open", "收盘": "close",
                "最高": "high", "最低": "low", "成交量": "volume",
            })
            df["date"] = pd.to_datetime(df["date"])
            return df[["date", "open", "close", "high", "low", "volume"]]
        except Exception as e:
            raise DataProviderError(f"获取 ETF 日线失败 {symbol}: {e}")

    def get_fund_nav(self, symbol: str) -> Optional[pd.Series]:
        try:
            ak = self._get_akshare()
            df = ak.fund_open_fund_info_em(symbol=symbol, indicator="单位净值走势")
            if df.empty:
                return None
            latest = df.iloc[-1]
            return pd.Series({
                "nav": float(latest.get("单位净值", 0)),
                "date": str(latest.get("净值日期", "")),
                "accum_nav": float(latest.get("累计净值", 0)),
            }, name=symbol)
        except Exception as e:
            raise DataProviderError(f"获取基金净值失败 {symbol}: {e}")

    def get_fund_info(self, symbol: str) -> dict:
        try:
            ak = self._get_akshare()
            df = ak.fund_open_fund_info_em(symbol=symbol, indicator="基金概况")
            result = {}
            for _, row in df.iterrows():
                item = row.get("item", "")
                value = row.get("value", "")
                if "基金经理" in item:
                    result["manager"] = str(value)
                elif "管理费率" in item:
                    result["management_fee"] = str(value)
                elif "基金规模" in item:
                    result["scale"] = str(value)
                elif "成立日期" in item:
                    result["inception_date"] = str(value)
            result.setdefault("manager", "")
            return result
        except Exception as e:
            raise DataProviderError(f"获取基金信息失败 {symbol}: {e}")

    def get_fund_holdings(self, symbol: str) -> Optional[pd.DataFrame]:
        try:
            ak = self._get_akshare()
            df = ak.fund_portfolio_hold_em(symbol=symbol, date="")
            if df.empty:
                return None
            df = df.rename(columns={
                "股票代码": "stock_code", "股票名称": "stock_name",
                "占净值比例": "weight",
            })
            df["weight"] = pd.to_numeric(df["weight"], errors="coerce")
            return df[["stock_code", "stock_name", "weight"]]
        except Exception as e:
            raise DataProviderError(f"获取基金持仓失败 {symbol}: {e}")
