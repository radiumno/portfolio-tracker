"""基金/ETF 分析系统 CLI"""

from typing import Optional
import typer
from cli.commands.analyze import analyze_cmd
from cli.commands.report import report_cmd

app = typer.Typer(
    name="fund",
    help="基金/ETF 智能分析系统",
)


@app.callback()
def main():
    """基金/ETF 分析系统 CLI"""


@app.command()
def analyze(
    csv_path: str = typer.Argument(..., help="持仓 CSV 文件路径"),
    stages: Optional[str] = typer.Option(None, "--stages", help="指定阶段(逗号分隔), 如 P1,P2"),
):
    """分析持仓并输出分析结果"""
    analyze_cmd(csv_path, stages)


@app.command()
def report(
    csv_path: str = typer.Argument(..., help="持仓 CSV 文件路径"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="输出文件路径(默认 stdout)"),
):
    """导出 JSON 格式分析报告"""
    report_cmd(csv_path, output)


if __name__ == "__main__":
    app()
