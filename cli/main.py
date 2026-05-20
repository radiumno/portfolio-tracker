"""Fund Analyzer CLI"""

from typing import Optional
import typer
from cli.commands.analyze import analyze_cmd

app = typer.Typer(
    name="fund",
    help="基金/ETF 智能分析系统",
)


@app.callback()
def main():
    """Fund Analyzer CLI - 基金/ETF 智能分析系统"""


@app.command()
def analyze(
    csv_path: str = typer.Argument(..., help="持仓 CSV 文件路径"),
    stages: Optional[str] = typer.Option(None, "--stages", help="指定阶段(逗号分隔), 如 P1,P2"),
):
    """分析持仓并输出结果"""
    analyze_cmd(csv_path, stages)


if __name__ == "__main__":
    app()
