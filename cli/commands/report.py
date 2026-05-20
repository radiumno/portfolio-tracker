"""report 子命令 — 导出分析报告（JSON / 文本）"""

import json
from typing import Optional
from portfolio.loader import load_positions_from_csv
from portfolio.models import Portfolio
from analysis.pipeline import AnalysisPipeline


def _serialize(obj):
    """JSON 序列化辅助，处理非标准类型"""
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    return str(obj)


def report_cmd(csv_path: str, output: Optional[str] = None, fmt: str = "json") -> None:
    """加载持仓、运行全流水线分析、导出报告"""
    positions = load_positions_from_csv(csv_path)
    portfolio = Portfolio(positions=positions)
    portfolio.recalc()

    pipeline = AnalysisPipeline()
    ctx = pipeline.run(portfolio)

    report = {
        "portfolio": {
            "total_value": portfolio.total_value,
            "position_count": len(portfolio.positions),
            "positions": [
                {
                    "symbol": p.symbol,
                    "name": p.name,
                    "asset_type": p.asset_type.value,
                    "market": p.market.value,
                    "market_value": p.market_value,
                    "unrealized_pnl_pct": round(p.unrealized_pnl_pct * 100, 2),
                }
                for p in portfolio.positions
            ],
        },
        "phases": {},
    }

    # 各阶段结果
    for phase_name in ("P2", "P3", "P4", "P5", "P6", "P7"):
        output_data = ctx.phase_outputs.get(phase_name, {})
        # 过滤不可序列化的数据
        clean = {}
        for k, v in output_data.items():
            try:
                json.dumps(v)
                clean[k] = v
            except (TypeError, ValueError):
                clean[k] = str(v)
        report["phases"][phase_name] = clean

    # 理论评分汇总
    theory_scores = {}
    for theory_name, results in ctx.theory_results.items():
        theory_scores[theory_name] = [
            {"symbol": _extract_symbol(r.details), "score": r.overall_score, "summary": r.summary}
            for r in results
        ]
    report["theory_scores"] = theory_scores

    # 风险摘要
    if ctx.risk_result:
        report["risk"] = {
            "portfolio_volatility": ctx.risk_result.portfolio_volatility,
            "diversification_ratio": ctx.risk_result.diversification_ratio,
        }

    # 相关性摘要
    if ctx.correlation_result:
        report["correlation"] = {
            "asset_count": len(ctx.correlation_result.symbols),
            "avg_correlation": ctx.correlation_result.avg_correlation,
        }

    # 压力测试摘要
    if ctx.stress_test_result:
        report["stress_test"] = {
            "worst_case_loss": ctx.stress_test_result.worst_case_loss,
            "resilient_assets": ctx.stress_test_result.resilient_assets,
            "vulnerable_assets": ctx.stress_test_result.vulnerable_assets,
        }

    # 输出
    json_str = json.dumps(report, ensure_ascii=False, indent=2, default=_serialize)

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(json_str)
    else:
        # 直接打印
        import sys
        sys.stdout.reconfigure(encoding="utf-8")
        print(json_str)


def _extract_symbol(details: dict) -> str:
    """从理论结果的 details 中尝试提取标的代码"""
    if not details:
        return "?"
    for key in ("symbol", "代码", "标的"):
        if key in details:
            return str(details[key])
    return "?"
