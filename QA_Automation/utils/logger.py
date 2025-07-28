"""
Advanced logging configuration for API testing framework
"""
import sys
import os
from pathlib import Path
from loguru import logger
from typing import Optional


class TestLogger:
    """
    Centralized logging configuration with multiple handlers
    """
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.logs_dir = self.base_dir / 'logs'
        self.logs_dir.mkdir(exist_ok=True)
        self._setup_logger()
    
    def _setup_logger(self):
        """Configure loguru logger with multiple handlers"""
        # Remove default handler
        logger.remove()
        
        # Console handler with colors
        logger.add(
            sys.stdout,
            level="INFO",
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            colorize=True,
            enqueue=True
        )
        
        # Main log file
        logger.add(
            self.logs_dir / "api_tests.log",
            level="DEBUG",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            enqueue=True
        )
        
        # Error log file
        logger.add(
            self.logs_dir / "errors.log",
            level="ERROR",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="5 MB",
            retention="30 days",
            compression="zip",
            enqueue=True
        )
        
        # API requests log file
        logger.add(
            self.logs_dir / "api_requests.log",
            level="DEBUG",
            format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
            filter=lambda record: "API_REQUEST" in record["message"],
            rotation="20 MB",
            retention="15 days",
            enqueue=True
        )
    
    def log_request(self, method: str, url: str, headers: dict = None, body: dict = None):
        """Log API request details"""
        log_msg = f"API_REQUEST | {method.upper()} {url}"
        if headers:
            log_msg += f" | Headers: {headers}"
        if body:
            log_msg += f" | Body: {body}"
        logger.info(log_msg)
    
    def log_response(self, status_code: int, response_time: float, response_body: str = None):
        """Log API response details"""
        log_msg = f"API_RESPONSE | Status: {status_code} | Time: {response_time:.3f}s"
        if response_body:
            log_msg += f" | Body: {response_body[:500]}{'...' if len(response_body) > 500 else ''}"
        logger.info(log_msg)
    
    def log_test_start(self, test_name: str):
        """Log test start"""
        logger.info(f"🚀 Starting test: {test_name}")
    
    def log_test_end(self, test_name: str, status: str):
        """Log test end"""
        emoji = "✅" if status.lower() == "passed" else "❌"
        logger.info(f"{emoji} Test {status}: {test_name}")
    
    def log_assertion(self, assertion: str, result: bool):
        """Log assertion details"""
        status = "PASS" if result else "FAIL"
        logger.info(f"Assertion {status}: {assertion}")


# Global logger instance
test_logger = TestLogger()
api_logger = logger.bind(component="api_client") 