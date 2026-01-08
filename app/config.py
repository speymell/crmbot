from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = Field(validation_alias="DATABASE_URL")

    jwt_secret: str = Field(validation_alias="JWT_SECRET")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    webhook_base_url: str | None = None
    auto_set_webhook: bool = False

    log_level: str = "INFO"

    # CORS configuration
    cors_origins: str = Field(default="", validation_alias="CORS_ORIGINS")
    environment: str = Field(default="development", validation_alias="ENVIRONMENT")

    def get_cors_origins_list(self) -> list[str]:
        """
        Parse CORS origins from environment variable and provide defaults based on environment.
        
        Returns:
            List of allowed CORS origins
        """
        # Development default origins
        dev_defaults = [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ]
        
        # Parse configured origins from comma-separated string
        configured_origins = []
        if self.cors_origins:
            configured_origins = [
                origin.strip() 
                for origin in self.cors_origins.split(",") 
                if origin.strip()
            ]
        
        # In development mode, merge configured origins with defaults
        if self.environment.lower() == "development":
            # Combine and deduplicate
            all_origins = list(set(dev_defaults + configured_origins))
            return all_origins
        
        # In production mode, use only configured origins (or empty list if none configured)
        return configured_origins


settings = Settings()
