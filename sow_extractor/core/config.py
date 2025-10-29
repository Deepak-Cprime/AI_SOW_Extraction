from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    openai_api_key: str
    openai_model: str = "gpt-4-1106-preview"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    tesseract_path: Optional[str] = None
    targetprocess_domain: Optional[str] = None
    targetprocess_access_token: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False

_settings = None

def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings