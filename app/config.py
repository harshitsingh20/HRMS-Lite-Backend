import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "postgres"
    db_password: str = ""
    db_name: str = "hrms_lite_db"
    database_url: str = ""
    app_name: str = "HRMS Lite"
    debug: bool = True
    host: str = "localhost"
    port: int = 3001

    class Config:
        env_file = ".env"

    def get_database_url(self):
        if self.database_url:
            return self.database_url
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


settings = Settings()
