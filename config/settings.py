"""
Configuration settings for the Customer Support Desk application.
Handles environment variables and application configuration securely.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings class with security-focused configuration."""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Security Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./customer_support.db")
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/customer_support.log")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    # CrewAI Configuration
    CREWAI_VERBOSE: bool = os.getenv("CREWAI_VERBOSE", "True").lower() == "true"
    CREWAI_MEMORY: bool = os.getenv("CREWAI_MEMORY", "True").lower() == "true"
    
    # Security Validation
    @classmethod
    def validate_configuration(cls) -> bool:
        """Validate that all required configuration is present."""
        required_fields = ["OPENAI_API_KEY", "SECRET_KEY"]
        
        for field in required_fields:
            if not getattr(cls, field):
                raise ValueError(f"Missing required configuration: {field}")
        
        return True

# Create settings instance
settings = Settings()

# Validate configuration on import
try:
    settings.validate_configuration()
except ValueError as e:
    print(f"Configuration Error: {e}")
    print("Please check your environment variables or .env file.") 