"""成长投资理论 — Fisher / Lynch 成长股框架"""

from typing import Optional
from portfolio.models import Position, AssetType
from analysis.theories import BaseTheory
from analysis.models.theory import TheoryResult, TheorySignal


class GrowthTheory(BaseTheory):
    """成长投资理论

    核心指标：
    - 营收/利润增长率
    - PEG 比率
    - 盈利能力趋势
    - 市场空间
    """

    @property
    def name(self) -> str:
        return "growth"

    @property
    def label(self) -> str:
        return "成长投资"

    def analyze(self, positions: list[Position], **kwargs) -> list[TheoryResult]:
        results: list[TheoryResult] = []

        for pos in positions:
            score = 50.0
            details: dict = {}
            signals: list[TheorySignal] = []
            notes: list[str] = []

            # 成本 vs 市值 判断成长信号
            if pos.cost_price > 0 and pos.market_price > 0:
                pnl_pct = (pos.market_price - pos.cost_price) / pos.cost_price * 100
                details["涨幅"] = round(pnl_pct, 2)

                if pnl_pct > 20:
                    signals.append(TheorySignal(
                        direction="buy" if pnl_pct < 50 else "hold",
                        reason=f"价格上涨 {pnl_pct:.1f}%，可能是成长动能的体现",
                        confidence=0.35,
                    ))
                    score += 10
                    notes.append("价格正增长，关注成长持续性")
                elif pnl_pct < -10:
                    signals.append(TheorySignal(
                        direction="buy",
                        reason=f"价格下跌 {abs(pnl_pct):.1f}%，如果是暂时性回调可能是成长股买入机会",
                        confidence=0.25,
                    ))
                    notes.append("回调中，需判断是暂时性还是结构性")
                else:
                    signals.append(TheorySignal(
                        direction="hold",
                        reason="价格变动不大，等待更多成长信号",
                        confidence=0.3,
                    ))
                    notes.append("价格平稳")

            # ETF — 追踪成长指数
            if pos.asset_type == AssetType.ETF:
                growth_keywords = ["成长", "创新", "科创", "创业", "新兴", "科技", "消费"]
                if any(kw in pos.name for kw in growth_keywords):
                    score += 15
                    notes.append("成长风格 ETF，符合成长投资框架")
                    signals.append(TheorySignal(
                        direction="buy",
                        reason="标的属于成长风格资产，符合成长投资偏好",
                        confidence=0.4,
                    ))
                else:
                    score += 3
                    notes.append("非成长风格 ETF")

            # 主动基金 — 关注经理的成长风格
            elif pos.asset_type == AssetType.FUND:
                score += 5
                notes.append("主动管理基金，成长潜力依赖经理选股能力")

            # REIT — 稳定增长
            elif pos.asset_type == AssetType.REIT:
                score += 3
                notes.append("REIT 有稳定现金流增长")

            results.append(TheoryResult(
                theory_name=self.name,
                theory_label=self.label,
                overall_score=max(0, min(100, int(round(score)))),
                signals=signals,
                summary="; ".join(notes) if notes else "基础成长分析完成",
                details=details,
            ))

        return results
