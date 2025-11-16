"""
Configuration management for GitHub Enterprise AI Agents.

This module loads configuration from environment variables and provides
a centralized settings object for the entire application.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    """Application settings loaded from environment variables."""
    
    # Google Gemini API Configuration
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    # GitHub Configuration
    GITHUB_TOKEN: Optional[str] = os.getenv("GITHUB_TOKEN")
    
    # Google Cloud Configuration
    GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "KaggleStudy2025")
    GCP_REGION: str = os.getenv("GCP_REGION", "us-central1")
    
    # Service Configuration
    MAIN_SERVICE_PORT: int = int(os.getenv("MAIN_SERVICE_PORT", "8000"))
    KNOWLEDGE_SERVICE_PORT: int = int(os.getenv("KNOWLEDGE_SERVICE_PORT", "8001"))
    DASHBOARD_PORT: int = int(os.getenv("DASHBOARD_PORT", "3000"))
    
    # Database Configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///data/sessions.db"
    )
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/agents.log")
    
    # Project paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent
    DATA_DIR: Path = PROJECT_ROOT / "data"
    LOGS_DIR: Path = PROJECT_ROOT / "logs"
    
    def __init__(self):
        """Initialize settings and create necessary directories."""
        self.DATA_DIR.mkdir(exist_ok=True)
        self.LOGS_DIR.mkdir(exist_ok=True)
    
    def validate(self) -> bool:
        """
        Validate that required configuration is present.
        
        Returns:
            bool: True if configuration is valid, False otherwise.
        """
        if not self.GOOGLE_API_KEY:
            print("❌ Error: GOOGLE_API_KEY not found in environment variables.")
            print("   Please create a .env file and add your API key.")
            return False
        
        return True
    
    def __repr__(self) -> str:
        """Return string representation of settings (without secrets)."""
        return (
            f"Settings("
            f"GCP_PROJECT={self.GCP_PROJECT_ID}, "
            f"REGION={self.GCP_REGION}, "
            f"MAIN_PORT={self.MAIN_SERVICE_PORT}, "
            f"KNOWLEDGE_PORT={self.KNOWLEDGE_SERVICE_PORT}"
            f")"
        )


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """
    Get the global settings instance.
    
    Returns:
        Settings: The global settings object.
    """
    return settings


if __name__ == "__main__":
    # Test configuration
    settings = get_settings()
    print("Configuration loaded:")
    print(f"  Project Root: {settings.PROJECT_ROOT}")
    print(f"  GCP Project: {settings.GCP_PROJECT_ID}")
    print(f"  Main Service Port: {settings.MAIN_SERVICE_PORT}")
    print(f"  Database URL: {settings.DATABASE_URL}")
    print(f"  Log Level: {settings.LOG_LEVEL}")
    
    if settings.validate():
        print("\n✅ Configuration is valid!")
    else:
        print("\n❌ Configuration is invalid!")

