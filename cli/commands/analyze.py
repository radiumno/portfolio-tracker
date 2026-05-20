"""analyze 子命令逻辑"""

from typing import Optional
from rich.console import Console
from rich.table import Table
from portfolio.loader import load_positions_from_csv
from portfolio.models import Portfolio
from analysis.pipeline import AnalysisPipeline

console = Console()


def analyze_cmd(
    csv_path: str,
    stages: Optional[str] = None,
) -> None:
    """加载持仓、显示摘要、运行分析流水线"""
    positions = load_positions_from_csv(csv_path)
    portfolio = Portfolio(positions=positions)
    portfolio.recalc()

    # 显示持仓摘要
    table = Table(title=f"持仓分析 ({len(positions)} 只标的)")
    table.add_column("代码", style="cyan")
    table.add_column("名称")
    table.add_column("类型")
    table.add_column("市值", justify="right")
    table.add_column("盈亏%", justify="right")

    for p in positions:
        pnl_str = f"{p.unrealized_pnl_pct*100:.1f}%"
        table.add_row(p.symbol, p.name, p.asset_type.value,
                      f"{p.market_value:,.0f}", pnl_str)

    console.print(table)
    console.print(f"\n组合总市值: [bold]{portfolio.total_value:,.0f}[/bold]")

    # 运行分析
    target_stages = stages.split(",") if stages else None
    pipeline = AnalysisPipeline()
    ctx = pipeline.run(portfolio, stages=target_stages)

    console.print("\n[green]分析完成[/green]")
    for phase, output in ctx.phase_outputs.items():
        console.print(f"  {phase}: {output.get('status', 'done')}")
