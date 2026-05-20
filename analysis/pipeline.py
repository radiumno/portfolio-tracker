"""LangGraph 7 阶段分析流水线 — Phase 2 增强版"""

from typing import Optional
from portfolio.models import Portfolio, Position
from analysis.models.analysis import ETFAnalysisResult, FundAnalysisResult
from analysis.models.risk import PortfolioRiskResult, RiskMetrics
from analysis.models.correlation import CorrelationMatrix
from analysis.models.theory import TheoryResult, StressTestResult
from analysis.agents.etf_analyzer import analyze_etf, calc_concentration
from analysis.agents.fund_analyzer import analyze_fund
from analysis.agents.risk_analyzer import analyze_risk_single, analyze_portfolio_risk
from analysis.agents.correlation import calc_correlation_matrix
from analysis.agents.concentration import (
    calc_portfolio_hhi, calc_effective_n, calc_top_n_concentration,
    calc_sector_concentration, detect_concentration_risks,
)
from analysis.agents.stress_test import run_stress_test
from analysis.theories import create_registry


class AnalysisContext:
    """贯穿流水线的上下文"""

    def __init__(self, portfolio: Portfolio):
        self.portfolio = portfolio
        self.etf_results: dict[str, ETFAnalysisResult] = {}
        self.fund_results: dict[str, FundAnalysisResult] = {}
        self.risk_result: Optional[PortfolioRiskResult] = None
        self.correlation_result: Optional[CorrelationMatrix] = None
        self.stress_test_result: Optional[StressTestResult] = None
        self.theory_results: dict[str, list[TheoryResult]] = {}
        self.phase_outputs: dict[str, dict] = {}

    @property
    def positions(self) -> list[Position]:
        return self.portfolio.positions


class AnalysisPipeline:
    """7 阶段分析流水线（数据采集→标的体检→组合分析→理论评估→辩论→风险评估→操作推荐）"""

    def __init__(self):
        self.phases = {
            "P1": self._phase_data_collection,
            "P2": self._phase_asset_checkup,
            "P3": self._phase_portfolio_analysis,
            "P4": self._phase_theory_evaluation,
            "P5": self._phase_debate,
            "P6": self._phase_risk_assessment,
            "P7": self._phase_recommendation,
        }

    def run(self, portfolio: Portfolio, stages: Optional[list[str]] = None) -> AnalysisContext:
        """运行指定阶段的分析流水线。"""
        ctx = AnalysisContext(portfolio)
        target_phases = stages or list(self.phases.keys())

        for phase_name in target_phases:
            if phase_name not in self.phases:
                continue
            phase_fn = self.phases[phase_name]
            ctx.phase_outputs[phase_name] = phase_fn(ctx) or {}

        return ctx

    def _phase_data_collection(self, ctx: AnalysisContext) -> dict:
        """P1: 并行获取所有标的数据"""
        # Phase 2 中仍为桩，完全实现需要 akshare/yfinance 运行时
        return {"status": "not_implemented", "note": "需要 akshare/yfinance 运行时环境"}

    def _phase_asset_checkup(self, ctx: AnalysisContext) -> dict:
        """P2: 每个标的分独立分析 — ETF 和基金分析"""
        results: dict[str, str] = {}
        for pos in ctx.positions:
            try:
                if pos.asset_type.value == "etf":
                    result = analyze_etf(
                        symbol=pos.symbol, name=pos.name,
                        data_source="持仓导入",
                    )
                    ctx.etf_results[pos.symbol] = result
                    results[pos.symbol] = "ok"
                elif pos.asset_type.value == "fund":
                    result = analyze_fund(
                        symbol=pos.symbol, name=pos.name,
                        data_source="持仓导入",
                    )
                    ctx.fund_results[pos.symbol] = result
                    results[pos.symbol] = "ok"
                else:
                    results[pos.symbol] = "skipped: 不支持的类型"
            except Exception as e:
                results[pos.symbol] = f"error: {e}"

        analyzed = len([v for v in results.values() if v == "ok"])
        return {
            "status": "done",
            "total": len(ctx.positions),
            "analyzed": analyzed,
            "details": results,
        }

    def _phase_portfolio_analysis(self, ctx: AnalysisContext) -> dict:
        """P3: 组合级别的相关性、集中度、压力测试"""
        positions = ctx.positions
        if not positions:
            return {"status": "skipped", "reason": "无持仓数据"}

        total_value = sum(p.market_value for p in positions)

        # 集中度分析
        hhi = calc_portfolio_hhi(positions)
        effective_n = calc_effective_n(positions)
        top5 = calc_top_n_concentration(positions)
        sector_conc = calc_sector_concentration(positions)
        risks = detect_concentration_risks(hhi, top5)

        # 压力测试
        ctx.stress_test_result = run_stress_test(positions)

        # 相关性（需要净值数据，P1 未实现时跳过）
        ctx.correlation_result = calc_correlation_matrix({}) if len(positions) < 2 else None

        return {
            "status": "done",
            "concentration": {
                "hhi": hhi,
                "effective_n": effective_n,
                "top5_pct": top5,
            },
            "risk_flags": risks,
            "sectors": [s.sector for s in sector_conc[:5]],
            "stress_test_scenarios": len(ctx.stress_test_result.scenarios) if ctx.stress_test_result else 0,
        }

    def _phase_theory_evaluation(self, ctx: AnalysisContext) -> dict:
        """P4: 投资理论并行评估"""
        registry = create_registry()
        ctx.theory_results = registry.run_all(ctx.positions)

        return {
            "status": "done",
            "theories": list(ctx.theory_results.keys()),
            "scores": {
                name: [r.overall_score for r in results]
                for name, results in ctx.theory_results.items()
            },
        }

    def _phase_debate(self, ctx: AnalysisContext) -> dict:
        """P5: 多智能体辩论（预留）"""
        return {"status": "not_implemented", "note": "需要 LLM 集成"}

    def _phase_risk_assessment(self, ctx: AnalysisContext) -> dict:
        """P6: 综合风险评估"""
        positions = ctx.positions
        if not positions:
            return {"status": "skipped", "reason": "无持仓数据"}

        # 使用集中度+压力测试结果进行风险评估
        hhi = calc_portfolio_hhi(positions)
        top5 = calc_top_n_concentration(positions)
        risk_flags = detect_concentration_risks(hhi, top5)

        stress = ctx.stress_test_result
        worst_loss = stress.worst_case_loss if stress else 0.0

        # 风险评级
        risk_level = "低"
        score_deduction = 0
        if worst_loss > 25:
            risk_level = "高"
            score_deduction += 20
        elif worst_loss > 15:
            risk_level = "中"
            score_deduction += 10

        if hhi > 2000:
            risk_level = "高"
            score_deduction += 15
        elif hhi > 1000:
            score_deduction += 5

        risk_score = max(0, 100 - score_deduction)

        return {
            "status": "done",
            "risk_score": risk_score,
            "risk_level": risk_level,
            "worst_case_loss_pct": worst_loss,
            "risk_flags": risk_flags,
            "concentration_hhi": hhi,
        }

    def _phase_recommendation(self, ctx: AnalysisContext) -> dict:
        """P7: 操作推荐（基于前 6 阶段结果）"""
        return {"status": "not_implemented", "note": "需要完整的前 6 阶段结果"}
