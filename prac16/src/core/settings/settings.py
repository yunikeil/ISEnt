from pathlib import Path

from pydantic import RedisDsn, PostgresDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(dotenv_path=env_path, override=True)


class __Settings(BaseSettings):
    DEBUG: bool
    ECHO_SQL: bool
    RELOAD: bool

    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_NAME: str
    DATABASE_CONNECTION_APP_NAME: str
    DATABASE_USERNAME: str
    DATABASE_PASSWORD: SecretStr

    _PGADMIN_DEFAULT_EMAIL: str
    _PGADMIN_DEFAULT_PASSWORD: SecretStr

    REDIS_HOST: str

    SMTP_ADRESS: str
    SMTP_SSL_PORT: int
    USER_VERIFY_LOGIN: str
    USER_VERIFY_PASSWORD: SecretStr

    SMTP_ADRESS: str
    SMTP_SSL_PORT: int
    PASSWORD_RESET_LOGIN: str
    PASSWORD_RESET_PASSWORD: SecretStr

    @property
    def DATABASE_URL(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.DATABASE_USERNAME,
            password=self.DATABASE_PASSWORD.get_secret_value(),
            host=self.DATABASE_HOST,
            port=self.DATABASE_PORT,
            path=self.DATABASE_NAME,
        )

    @property
    def REDIS_URL(self) -> RedisDsn:
        return  RedisDsn.build(
            scheme="redis",
            host=self.REDIS_HOST,
        )

    model_config = SettingsConfigDict(
        env_file=env_path, env_file_encoding='utf-8', extra="allow")


config = __Settings()
