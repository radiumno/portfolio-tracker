"""量化多因子投资理论 — 动量/质量/低波/规模因子"""

from typing import Optional
import numpy as np
from portfolio.models import Position, AssetType
from analysis.theories import BaseTheory
from analysis.models.theory import TheoryResult, TheorySignal


class QuantTheory(BaseTheory):
    """量化多因子投资理论

    评估因子：
    - **动量因子**: 近期价格趋势
    - **质量因子**: 盈利能力、稳定性
    - **低波因子**: 波动率越低得分越高
    - **规模因子**: 中小盘溢价（ETF/基金通过类型判断）

    综合评分 = 各因子加权得分
    """

    _FACTOR_WEIGHTS = {
        "momentum": 0.30,
        "quality": 0.25,
        "low_vol": 0.25,
        "size": 0.20,
    }

    @property
    def name(self) -> str:
        return "quant"

    @property
    def label(self) -> str:
        return "量化多因子"

    def _score_momentum(self, pos: Position) -> tuple[float, str]:
        """动量因子评分"""
        if pos.cost_price <= 0 or pos.market_price <= 0:
            return 50, "价格数据不足"
        pnl = (pos.market_price - pos.cost_price) / pos.cost_price * 100

        if pnl > 20:
            return 80, f"价格涨幅 {pnl:.1f}%，动量较强"
        elif pnl > 5:
            return 65, f"价格温和上涨 {pnl:.1f}%，动量中等"
        elif pnl > -5:
            return 50, f"价格平稳 (涨跌 {pnl:.1f}%)，动量中性"
        elif pnl > -20:
            return 35, f"价格下跌 {abs(pnl):.1f}%，动量偏弱"
        else:
            return 20, f"价格大幅下跌 {abs(pnl):.1f}%，动量极弱"

    def _score_quality(self, pos: Position) -> tuple[float, str]:
        """质量因子评分"""
        # 基于资产类型估算
        if pos.asset_type == AssetType.BOND:
            return 75, "债券资产，信用质量较高"
        elif pos.asset_type == AssetType.ETF:
            stock_keywords = ["300", "500", "50", "红利", "质量", "基本面"]
            if any(kw in pos.name for kw in stock_keywords):
                return 70, "宽基指数 ETF，成分股质量较好"
            elif any(kw in pos.name for kw in ["债", "国债"]):
                return 80, "债券 ETF，信用风险低"
            return 60, "ETF 资产，质量中等"
        elif pos.asset_type == AssetType.FUND:
            return 55, "主动基金，质量依赖经理能力"
        elif pos.asset_type == AssetType.REIT:
            return 60, "REIT，质量取决于底层资产"
        return 50, "质量无法准确评估"

    def _score_low_vol(self, pos: Position) -> tuple[float, str]:
        """低波动因子评分"""
        if pos.asset_type == AssetType.BOND:
            return 80, "债券通常波动较低"
        elif pos.asset_type == AssetType.REIT:
            return 45, "REIT 波动率中等偏高"
        elif pos.asset_type == AssetType.ETF:
            low_vol_keywords = ["债", "红利", "价值", "低波"]
            high_vol_keywords = ["科创", "创业", "成长", "杠杆"]
            if any(kw in pos.name for kw in low_vol_keywords):
                return 75, "低波动风格 ETF"
            elif any(kw in pos.name for kw in high_vol_keywords):
                return 30, "高波动风格 ETF"
            return 50, "ETF 波动率中等"
        elif pos.asset_type == AssetType.FUND:
            bond_kw = ["债", "货币"]
            if any(kw in pos.name for kw in bond_kw):
                return 70, "债券型基金波动较低"
            return 40, "偏股基金波动较高"
        return 50, "波动率未知"

    def _score_size(self, pos: Position) -> tuple[float, str]:
        """规模因子评分 — 中小盘溢价"""
        if pos.asset_type == AssetType.ETF:
            small_kw = ["500", "1000", "2000", "科创", "创业", "中小"]
            large_kw = ["50", "100", "300", "大盘"]
            if any(kw in pos.name for kw in small_kw):
                return 70, "中小盘风格，规模因子正暴露"
            elif any(kw in pos.name for kw in large_kw):
                return 40, "大盘风格，规模因子负暴露"
            return 50, "规模因子中性"
        elif pos.asset_type == AssetType.FUND:
            return 55, "主动管理可能有中小盘暴露"
        elif pos.asset_type == AssetType.BOND:
            return 50, "债券与规模因子不相关"
        return 50, "规模因子中性"

    def analyze(self, positions: list[Position], **kwargs) -> list[TheoryResult]:
        results: list[TheoryResult] = []

        for pos in positions:
            factors: dict[str, tuple[float, str]] = {
                "momentum": self._score_momentum(pos),
                "quality": self._score_quality(pos),
                "low_vol": self._score_low_vol(pos),
                "size": self._score_size(pos),
            }

            weighted = sum(
                factors[f][0] * self._FACTOR_WEIGHTS[f]
                for f in self._FACTOR_WEIGHTS
            )
            overall = int(round(weighted))

            factor_details = {
                name: {"score": round(score, 1), "note": note}
                for name, (score, note) in factors.items()
            }

            signals: list[TheorySignal] = []
            momentum_score, _ = factors["momentum"]
            low_vol_score, _ = factors["low_vol"]

            if momentum_score > 65 and overall > 60:
                signals.append(TheorySignal(
                    direction="buy", reason="量化和趋势向好，多因子共振",
                    confidence=0.5,
                ))
            elif overall > 50:
                signals.append(TheorySignal(
                    direction="hold", reason="量化评估中性偏正面",
                    confidence=0.4,
                ))
            else:
                signals.append(TheorySignal(
                    direction="reduce", reason="多因子评分偏低，建议减仓评估",
                    confidence=0.3,
                ))

            results.append(TheoryResult(
                theory_name=self.name,
                theory_label=self.label,
                overall_score=overall,
                signals=signals,
                summary=f"多因子综合评分 {overall}/100，{self._summary_by_score(overall)}",
                details={"factors": factor_details, "weights": self._FACTOR_WEIGHTS},
            ))

        return results

    @staticmethod
    def _summary_by_score(score: int) -> str:
        if score >= 75:
            return "量化指标优秀"
        elif score >= 60:
            return "量化指标良好"
        elif score >= 40:
            return "量化指标一般"
        else:
            return "量化指标偏弱"
