from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "ReefConnect API"
    debug: bool = True
    database_url: str = "postgresql://user:password@localhost/reefconnect"

    class Config:
        env_file = ".env"

settings = Settings()