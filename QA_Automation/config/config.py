"""
Configuration management for API testing framework
"""
import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
from decouple import config
from loguru import logger


class Config:
    """
    Centralized configuration management
    """
    
    def __init__(self, environment: str = None):
        self.base_dir = Path(__file__).parent.parent
        self.environment = environment or config('ENVIRONMENT', default='dev')
        self.config_data = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environments.json"""
        config_file = self.base_dir / 'config' / 'environments.json'
        
        try:
            with open(config_file, 'r') as f:
                all_configs = json.load(f)
                return all_configs.get(self.environment, all_configs.get('dev', {}))
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_file}")
            return self._default_config()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration values"""
        return {
            "base_url": "https://jsonplaceholder.typicode.com",
            "timeout": 30,
            "retry_count": 3,
            "retry_delay": 1,
            "headers": {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        }
    
    @property
    def base_url(self) -> str:
        """Get base URL for API"""
        return self.config_data.get('base_url', 'https://jsonplaceholder.typicode.com')
    
    @property
    def timeout(self) -> int:
        """Get request timeout"""
        return self.config_data.get('timeout', 30)
    
    @property
    def retry_count(self) -> int:
        """Get retry count for failed requests"""
        return self.config_data.get('retry_count', 3)
    
    @property
    def retry_delay(self) -> int:
        """Get delay between retries"""
        return self.config_data.get('retry_delay', 1)
    
    @property
    def headers(self) -> Dict[str, str]:
        """Get default headers"""
        return self.config_data.get('headers', {
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    @property
    def auth_token(self) -> Optional[str]:
        """Get authentication token"""
        return config('AUTH_TOKEN', default=self.config_data.get('auth_token'))
    
    @property
    def database_url(self) -> Optional[str]:
        """Get database URL if configured"""
        return config('DATABASE_URL', default=self.config_data.get('database_url'))
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        return self.config_data.get(key, default)
    
    def update(self, key: str, value: Any) -> None:
        """Update configuration value"""
        self.config_data[key] = value
        logger.info(f"Updated config: {key} = {value}")


# Global config instance
config_instance = Config() 