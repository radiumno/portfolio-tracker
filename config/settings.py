from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env.

    YAML configuration (``config/default.yaml``) is kept as reference
    documentation for future phases; it is **not** read by this class yet.
    """

    # Project paths
    project_root: Path = Path(__file__).resolve().parent.parent
    data_cache_dir: Path = project_root / ".cache"

    # Data providers
    data_provider_cn: str = "akshare"
    data_provider_global: str = "yfinance"

    # Analysis defaults
    risk_free_rate: float = 0.03
    confidence_threshold: float = 0.6
    max_debate_rounds: int = 2

    # Cache
    cache_ttl_hours: int = 4

    model_config = SettingsConfigDict(env_prefix="FUND_", env_file=".env")


settings = Settings()
