from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """从环境变量 /.env 文件加载的应用配置。

    YAML 配置（``config/default.yaml``）保留作为参考文档，
    当前阶段暂未由此类读取。
    """

    # 项目路径
    project_root: Path = Path(__file__).resolve().parent.parent
    data_cache_dir: Path = project_root / ".cache"

    # 数据提供者
    data_provider_cn: str = "akshare"
    data_provider_global: str = "yfinance"

    # 分析默认值
    risk_free_rate: float = 0.03
    confidence_threshold: float = 0.6
    max_debate_rounds: int = 2

    # 缓存
    cache_ttl_hours: int = 4

    model_config = SettingsConfigDict(env_prefix="FUND_", env_file=".env")


settings = Settings()
