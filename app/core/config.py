import os
from pydantic import BaseModel
from typing import Optional, List
import secrets
from urllib.parse import quote_plus


class Settings(BaseModel):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "E-commerce Admin API"
    
    # Database settings
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")  # Set your MySQL password here or in .env
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: str = os.getenv("MYSQL_PORT", "3306")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "ecommerce_admin")
    
    # JWT settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        # URL encode the password to handle special characters
        encoded_password = quote_plus(self.MYSQL_PASSWORD)
        return f"mysql+pymysql://{self.MYSQL_USER}:{encoded_password}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings() 