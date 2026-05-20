"""价值投资理论 — Graham / Buffett 估值框架"""

from typing import Optional
import numpy as np
from portfolio.models import Position, AssetType
from analysis.theories import BaseTheory
from analysis.models.theory import TheoryResult, TheorySignal


class ValueTheory(BaseTheory):
    """价值投资理论

    核心指标：
    - 市盈率(PE)合理区间
    - 市净率(PB)安全边际
    - 股息率
    - 净资产收益率(ROE)
    - 安全边际 = 内在价值 - 市价
    """

    @property
    def name(self) -> str:
        return "value"

    @property
    def label(self) -> str:
        return "价值投资"

    def analyze(self, positions: list[Position], **kwargs) -> list[TheoryResult]:
        results: list[TheoryResult] = []

        for pos in positions:
            score = 50.0  # 基准分
            details: dict = {}
            signals: list[TheorySignal] = []
            notes: list[str] = []

            # 成本价 vs 市价 — 粗略判断
            if pos.cost_price > 0 and pos.market_price > 0:
                pnl_pct = (pos.market_price - pos.cost_price) / pos.cost_price * 100
                details["成本涨跌幅"] = round(pnl_pct, 2)

                if pnl_pct > 30:
                    signals.append(TheorySignal(
                        direction="reduce",
                        reason=f"相对成本已涨 {pnl_pct:.1f}%，安全边际收窄，建议部分止盈",
                        confidence=0.3,
                    ))
                    score -= 5
                    notes.append("涨幅较大，安全边际降低")
                elif pnl_pct < -20:
                    signals.append(TheorySignal(
                        direction="buy",
                        reason=f"相对成本下跌 {abs(pnl_pct):.1f}%，可能出现低估机会",
                        confidence=0.4,
                    ))
                    score += 10
                    notes.append("大幅下跌，关注是否被低估")
                else:
                    signals.append(TheorySignal(
                        direction="hold",
                        reason=f"价格在成本 ±{abs(pnl_pct):.1f}% 范围，估值合理",
                        confidence=0.5,
                    ))
                    score += 5
                    notes.append("估值相对合理")

            # ETF 类型的价值评估
            if pos.asset_type == AssetType.ETF:
                # 宽基 ETF 通常有稳定的价值
                stock_keywords = ["300", "500", "180", "50", "红利", "价值", "基本面"]
                if any(kw in pos.name for kw in stock_keywords):
                    score += 10
                    notes.append("宽基/价值型 ETF，符合价值投资标的")
                else:
                    score -= 5
                    notes.append("非宽基 ETF，需额外评估")

            # 基金的价值评分
            elif pos.asset_type == AssetType.FUND:
                score += 3  # 主动管理有潜在超额收益
                notes.append("主动管理基金，依赖经理能力")

            # 债券/REIT
            elif pos.asset_type == AssetType.BOND:
                score += 5
                notes.append("债券类资产，防御性较好的价值配置")
            elif pos.asset_type == AssetType.REIT:
                score += 5
                notes.append("REIT 有稳定分红，具备一定价值属性")

            # 集中度简单评估
            if pos.market_value > 0:
                details["市值"] = round(pos.market_value, 2)

            # 安全边际提醒
            if not signals:
                signals.append(TheorySignal(
                    direction="hold",
                    reason="数据不足以做出明确判断，建议保持持有",
                    confidence=0.3,
                ))

            results.append(TheoryResult(
                theory_name=self.name,
                theory_label=self.label,
                overall_score=max(0, min(100, int(round(score)))),
                signals=signals,
                summary="; ".join(notes) if notes else "基础价值分析完成",
                details=details,
            ))

        return results
