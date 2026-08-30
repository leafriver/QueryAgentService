"""全局配置。

从环境变量 / .env 文件读取，未设置时使用默认值。
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    PROJECT_NAME: str = "QueryAgentService"
    API_V1_STR: str = "/api/v1"

    # 允许跨域的来源，逗号分隔，例如: http://localhost:5173
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    # 数据库连接地址
    DATABASE_URL: str = "sqlite:///./queryagent.db"

    # JWT 相关配置
    SECRET_KEY: str = "change-me-in-production-please-generate-a-random-64-chars-string"
    ALGORITHM: str = "HS256"
    # 令牌有效期（分钟），默认 24 小时
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # 大模型配置（OpenAI 兼容接口，默认 DeepSeek）
    # 在 server/.env 中设置 LLM_API_KEY，切勿提交到代码库
    LLM_BASE_URL: str = "https://api.deepseek.com"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "deepseek-chat"
    # 采样温度，0~2，越高越发散
    LLM_TEMPERATURE: float = 0.7
    # 单次回复最大 token 数
    LLM_MAX_TOKENS: int = 2048
    # 请求超时（秒），大模型生成较慢，需留足余量
    LLM_TIMEOUT: float = 90.0


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
