"""全天候投资理论 — Ray Dalio 风险平价框架"""

from portfolio.models import Position, AssetType, MarketType
from analysis.theories import BaseTheory
from analysis.models.theory import TheoryResult, TheorySignal


class AllWeatherTheory(BaseTheory):
    """全天候投资理论

    Dalio 四大经济象限：
    - 增长 + 通胀（繁荣）：股票、商品
    - 增长 + 通缩（衰退）：债券、TIPS
    - 不增长 + 通胀（滞胀）：通胀挂钩债券、商品
    - 不增长 + 通缩（萧条）：国债、黄金

    评估组合是否在所有宏观象限中都有配置。
    """

    # 各资产对应的经济象限
    _QUADRANT_MAP: dict[str, list[str]] = {
        "growth_inflation": ["stock", "commodity", "reit"],
        "growth_deflation": ["stock", "bond"],
        "stagnation_inflation": ["bond", "reit"],
        "stagnation_deflation": ["bond"],
    }

    @property
    def name(self) -> str:
        return "all_weather"

    @property
    def label(self) -> str:
        return "全天候投资"

    def _classify_asset(self, pos: Position) -> list[str]:
        """将资产归类到经济象限"""
        quadrants = []

        if pos.asset_type in (AssetType.STOCK, AssetType.ETF):
            # 股票/EFF 覆盖增长象限
            quadrants.append("growth_inflation")
            quadrants.append("growth_deflation")
            # 偏债 ETF
            bond_keywords = ["债", "国债", "信用", "纯债"]
            if any(kw in pos.name for kw in bond_keywords):
                quadrants.append("stagnation_deflation")

        elif pos.asset_type == AssetType.BOND:
            quadrants.append("growth_deflation")
            quadrants.append("stagnation_deflation")
            quadrants.append("stagnation_inflation")

        elif pos.asset_type == AssetType.FUND:
            # 偏股基金在增长象限，偏债基金在通缩象限
            stock_keywords = ["股", "混合", "成长", "价值"]
            bond_keywords = ["债", "货币", "纯债", "理财"]
            if any(kw in pos.name for kw in stock_keywords):
                quadrants.append("growth_inflation")
                quadrants.append("growth_deflation")
            elif any(kw in pos.name for kw in bond_keywords):
                quadrants.append("stagnation_deflation")
                quadrants.append("growth_deflation")
            else:
                quadrants.extend(["growth_inflation", "growth_deflation", "stagnation_deflation"])

        elif pos.asset_type == AssetType.REIT:
            quadrants.append("growth_inflation")
            quadrants.append("stagnation_inflation")

        return quadrants

    def analyze(self, positions: list[Position], **kwargs) -> list[TheoryResult]:
        results: list[TheoryResult] = []

        if not positions:
            return results

        # 组合级分析
        total_value = sum(p.market_value for p in positions)
        if total_value == 0:
            for pos in positions:
                results.append(TheoryResult(
                    theory_name=self.name, theory_label=self.label,
                    overall_score=50, summary="组合市值为零，无法评估",
                ))
            return results

        # 统计各象限配置
        quadrant_weights: dict[str, float] = {q: 0.0 for q in self._QUADRANT_MAP}
        for pos in positions:
            if pos.market_value == 0:
                continue
            weight = pos.market_value / total_value
            quadrants = self._classify_asset(pos)
            for q in quadrants:
                quadrant_weights[q] = quadrant_weights.get(q, 0) + weight

        # 理想情况下每个象限应有约 25%
        ideal = 25.0
        coverage_penalty = 0.0
        quadrant_notes: list[str] = []
        for q_name, q_weight in quadrant_weights.items():
            pct = q_weight * 100
            diff = abs(pct - ideal)
            if pct < 5:
                quadrant_notes.append(f"象限 '{q_name}' 配置不足 ({pct:.0f}%)")
                coverage_penalty += 15
            elif pct > 50:
                quadrant_notes.append(f"象限 '{q_name}' 过度集中 ({pct:.0f}%)")
                coverage_penalty += 10

        base_score = 100 - coverage_penalty
        base_score = max(0, min(100, base_score))

        signals: list[TheorySignal] = []
        if coverage_penalty > 30:
            signals.append(TheorySignal(
                direction="buy",
                reason="组合对某些宏观象限覆盖不足，建议补充配置以平衡风险",
                confidence=0.6,
            ))

        signals.append(TheorySignal(
            direction="hold" if coverage_penalty < 30 else "reduce",
            reason=f"全天候评分 {base_score:.0f}/100，{'组合较为均衡' if coverage_penalty < 30 else '需优化象限配置'}",
            confidence=0.5,
        ))

        # 逐标的回报
        results.append(TheoryResult(
            theory_name=self.name,
            theory_label=self.label,
            overall_score=int(round(base_score)),
            signals=signals,
            summary=f"组合覆盖 {sum(1 for v in quadrant_weights.values() if v > 0.05)}/4 个宏观经济象限{'，' + '；'.join(quadrant_notes[:3]) if quadrant_notes else '，配置均衡'}",
            details={
                "象限权重": {k: round(v * 100, 1) for k, v in quadrant_weights.items()},
                "覆盖象限数": sum(1 for v in quadrant_weights.values() if v > 0.05),
            },
        ))

        return results
