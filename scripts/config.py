"""
Configuration file for Google Search API application
"""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class Config:
 # Google API Configuration
 GOOGLE_API_KEY: str = ""
 GOOGLE_SEARCH_ENGINE_ID: str = ""
 
 # MySQL Database Configuration
 DB_HOST: str = "localhost"
 DB_PORT: int = 3306
 DB_USER: str = "root"
 DB_PASSWORD: str = ""
 DB_NAME: str = "google_search_app"
 
 # API Rate Limiting
 MAX_DAILY_REQUESTS: int = 50
 DEFAULT_RESULTS_PER_QUERY: int = 10
 
 # Logging Configuration
 LOG_LEVEL: str = "INFO"
 LOG_FILE: str = "google_search_app.log"
 
 @classmethod
 def from_env(cls) -> 'Config':
     """Load configuration from environment variables"""
     return cls(
         GOOGLE_API_KEY=os.getenv('GOOGLE_API_KEY', ''),
         GOOGLE_SEARCH_ENGINE_ID=os.getenv('GOOGLE_SEARCH_ENGINE_ID', ''),
         DB_HOST=os.getenv('DB_HOST', 'localhost'),
         DB_PORT=int(os.getenv('DB_PORT', '3306')),
         DB_USER=os.getenv('DB_USER', 'root'),
         DB_PASSWORD=os.getenv('DB_PASSWORD', ''),
         DB_NAME=os.getenv('DB_NAME', 'google_search_app'),
         MAX_DAILY_REQUESTS=int(os.getenv('MAX_DAILY_REQUESTS', '50')),
         DEFAULT_RESULTS_PER_QUERY=int(os.getenv('DEFAULT_RESULTS_PER_QUERY', '10')),
         LOG_LEVEL=os.getenv('LOG_LEVEL', 'INFO'),
         LOG_FILE=os.getenv('LOG_FILE', 'google_search_app.log')
     )
 
 def validate(self) -> tuple[bool, list[str]]:
     """Validate configuration and return status and error messages"""
     errors = []
     
     if not self.GOOGLE_API_KEY:
         errors.append("GOOGLE_API_KEY is required")
     
     if not self.GOOGLE_SEARCH_ENGINE_ID:
         errors.append("GOOGLE_SEARCH_ENGINE_ID is required")
     
     if not self.DB_USER:
         errors.append("DB_USER is required")
     
     return len(errors) == 0, errors

# Global configuration instance
config = Config.from_env()
