from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

class BasecampConfig(BaseSettings):
    """Configuration for Basecamp credentials."""

    account_id: int
    client_id: str
    client_secret: str
    redirect_uri: str
    refresh_token: str | None = None

    model_config = SettingsConfigDict(env_prefix="BASECAMP_", env_file=".env", extra="ignore")
