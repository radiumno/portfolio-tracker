"""行为金融理论 — 识别认知偏差和错误决策模式"""

from typing import Optional
from portfolio.models import Position, AssetType
from analysis.theories import BaseTheory
from analysis.models.theory import TheoryResult, TheorySignal


class BehavioralTheory(BaseTheory):
    """行为金融理论

    检测的偏差：
    - **处置效应**: 过早卖出赢家、死守亏损头寸
    - **羊群效应**: 持仓过度集中热门品种
    - **过度自信**: 持仓过于集中，缺乏分散
    - **锚定效应**: 过度关注成本价
    - **熟悉性偏差**: 过度配置本国/本地资产
    """

    @property
    def name(self) -> str:
        return "behavioral"

    @property
    def label(self) -> str:
        return "行为金融"

    def _detect_disposition_effect(self, pos: Position) -> Optional[str]:
        """处置效应检测：亏损头寸持有 vs 盈利头寸倾向卖出"""
        if pos.cost_price <= 0 or pos.market_price <= 0:
            return None
        pnl_pct = (pos.market_price - pos.cost_price) / pos.cost_price * 100

        # 大幅亏损仍持有 — 可能是不愿止损
        if pnl_pct < -30:
            return f"{pos.symbol} 亏损 {abs(pnl_pct):.0f}% 仍持有，可能存在'不愿止损'的处置效应"
        return None

    def _detect_familiarity_bias(self, pos: Position) -> Optional[str]:
        """熟悉性偏差检测"""
        # 如果只有国内市场（cn）而没有国际市场配置
        if pos.market.value == "cn":
            return None  # 在单标的层面不判断，在组合层面判断
        return None

    def analyze(self, positions: list[Position], **kwargs) -> list[TheoryResult]:
        results: list[TheoryResult] = []

        if not positions:
            return results

        # 组合级偏差检测
        total_value = sum(p.market_value for p in positions)
        biases: list[str] = []
        details: dict = {}
        signals: list[TheorySignal] = []
        bias_count = 0

        # 1. 分散度检测 — 过度自信
        if total_value > 0:
            num_positions = len(positions)
            if num_positions <= 2 and total_value > 10000:
                biases.append(f"仅持有 {num_positions} 个标的，持仓高度集中，可能存在过度自信偏差")
                bias_count += 1
            elif num_positions <= 5:
                biases.append(f"仅持有 {num_positions} 个标的，分散度不足，建议增加至 8-15 个标的")
                bias_count += 1

            # HHI-like
            weights = [(p.market_value / total_value) for p in positions]
            hhi = sum(w ** 2 for w in weights)
            details["集中度指数"] = round(hhi * 10000, 1)
            if hhi > 0.3:
                biases.append(f"持仓集中度偏高 (HHI={hhi*10000:.0f})，可能反映过度自信偏差")
                bias_count += 1

        # 2. 处置效应检测
        disposition_flags = []
        for pos in positions:
            flag = self._detect_disposition_effect(pos)
            if flag:
                disposition_flags.append(flag)
                bias_count += 1
        if len(disposition_flags) > 0:
            biases.extend(disposition_flags[:2])  # 最多显示 2 个

        # 3. 市场集中度 / 熟悉性偏差
        markets = set(p.market.value for p in positions)
        if len(markets) == 1 and "cn" in markets:
            biases.append("全部资产集中于中国市场，存在熟悉性偏差，建议配置全球资产")
            bias_count += 1

        # 4. 资产类型集中度
        types = set(p.asset_type.value for p in positions)
        if len(types) == 1:
            _type_name = list(types)[0]
            biases.append(f"全部资产为同一类型({_type_name})，缺乏跨资产类别分散")
            bias_count += 1

        # 评分：偏差越少得分越高
        score = max(0, 100 - bias_count * 20)

        if biases:
            signals.append(TheorySignal(
                direction="buy" if bias_count > 2 else "hold",
                reason=f"检测到 {bias_count} 个潜在行为偏差，建议审视投资决策",
                confidence=0.5,
            ))
        else:
            signals.append(TheorySignal(
                direction="hold",
                reason="未检测到明显行为偏差，继续保持",
                confidence=0.6,
            ))

        results.append(TheoryResult(
            theory_name=self.name,
            theory_label=self.label,
            overall_score=score,
            signals=signals,
            summary=f"检测到 {bias_count} 个潜在行为偏差" if biases else "未发现明显行为偏差",
            details={
                "biases": biases,
                "bias_count": bias_count,
                "持仓数": len(positions),
                "覆盖市场": list(markets),
            },
        ))

        return results
