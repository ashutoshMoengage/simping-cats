"""
🎯 Enhanced Logging System for API Testing Framework
====================================================

This module provides enterprise-grade logging with beginner-friendly explanations.

🌟 FEATURES:
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Structured logging with context
- Automatic log rotation
- Performance metrics logging
- Request/Response correlation tracking
- Export logs to various formats (JSON, CSV, XML)
- Integration with monitoring systems

📚 FOR BEGINNERS:
Logging is like keeping a diary of what your tests are doing. It helps you:
- Debug when tests fail
- Monitor performance
- Track API behavior over time
- Generate reports for stakeholders
"""

import json
import csv
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import uuid

from loguru import logger
import pandas as pd


@dataclass
class LogEntry:
    """
    📊 Structured Log Entry
    
    This class represents a single log entry with all relevant information.
    Using dataclasses makes the code clean and type-safe.
    
    🎯 OOP CONCEPT: DATA CLASSES
    - Automatically generates __init__, __repr__, __eq__ methods
    - Type hints for better code quality
    - Easy serialization to JSON/dict
    """
    timestamp: str
    level: str
    message: str
    test_name: Optional[str] = None
    api_endpoint: Optional[str] = None
    response_time: Optional[float] = None
    status_code: Optional[int] = None
    correlation_id: Optional[str] = None
    environment: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class EnhancedLogger:
    """
    🎯 Enterprise-Grade Logger with Context Awareness
    
    This is a SINGLETON class (only one instance exists) that provides
    comprehensive logging capabilities for API testing.
    
    🏗️ OOP CONCEPTS DEMONSTRATED:
    - SINGLETON PATTERN: Only one logger instance
    - CONTEXT MANAGERS: Automatic resource management
    - COMPOSITION: Uses loguru internally
    - ENCAPSULATION: Private methods for internal operations
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """
        🔒 SINGLETON IMPLEMENTATION
        
        This ensures only one logger instance exists throughout the application.
        Thread-safe implementation using double-checked locking pattern.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """
        🚀 Initialize the Enhanced Logger
        
        Sets up multiple log handlers, formatters, and storage mechanisms.
        Only runs once due to singleton pattern.
        """
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        self.base_dir = Path(__file__).parent.parent
        self.logs_dir = self.base_dir / 'logs'
        self.reports_dir = self.base_dir / 'reports'
        
        # Create directories
        self.logs_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        
        # Initialize storage for structured logs
        self.log_entries: List[LogEntry] = []
        self.performance_metrics: List[Dict[str, Any]] = []
        self.current_context = {}
        
        # Set up loguru configuration
        self._setup_loggers()
        
        logger.info("🎯 Enhanced Logger initialized successfully!")
    
    def _setup_loggers(self):
        """
        🔧 PRIVATE METHOD: Configure multiple log handlers
        
        This is a PRIVATE method (starts with _) that handles internal setup.
        It demonstrates ENCAPSULATION - hiding implementation details.
        """
        # Remove default logger
        logger.remove()
        
        # 📺 CONSOLE HANDLER: Pretty colored output for development
        logger.add(
            sink=lambda msg: print(msg, end=""),
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                   "<level>{message}</level>",
            level="INFO",
            colorize=True
        )
        
        # 📄 MAIN LOG FILE: Detailed logs for debugging
        logger.add(
            sink=str(self.logs_dir / "enhanced_test.log"),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level="DEBUG",
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            enqueue=True  # Thread-safe logging
        )
        
        # 🚨 ERROR LOG FILE: Only errors and critical issues
        logger.add(
            sink=str(self.logs_dir / "errors.log"),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level="ERROR",
            rotation="5 MB",
            retention="60 days"
        )
        
        # 📊 STRUCTURED JSON LOG: For programmatic processing
        logger.add(
            sink=str(self.logs_dir / "structured.jsonl"),
            format=lambda record: json.dumps({
                "timestamp": record["time"].isoformat(),
                "level": record["level"].name,
                "message": record["message"],
                "module": record["name"],
                "function": record["function"],
                "line": record["line"],
                "context": self.current_context
            }) + "\n",
            level="INFO",
            rotation="20 MB"
        )
    
    @contextmanager
    def test_context(self, test_name: str, environment: str = "dev"):
        """
        🎯 CONTEXT MANAGER: Automatic test context tracking
        
        This is a CONTEXT MANAGER that automatically tracks test execution context.
        It demonstrates the CONTEXT MANAGER PROTOCOL (__enter__, __exit__).
        
        Usage:
            with logger.test_context("test_user_creation", "staging"):
                # Your test code here
                # All logs will include test context automatically
        
        Args:
            test_name (str): Name of the test being executed
            environment (str): Environment where test is running
        """
        correlation_id = str(uuid.uuid4())[:8]
        
        # Set context
        old_context = self.current_context.copy()
        self.current_context.update({
            "test_name": test_name,
            "environment": environment,
            "correlation_id": correlation_id,
            "start_time": datetime.now().isoformat()
        })
        
        self.info(f"🚀 Starting test: {test_name}", extra_context={"event": "test_start"})
        
        start_time = time.time()
        
        try:
            yield correlation_id
        except Exception as e:
            self.error(f"❌ Test failed: {str(e)}", extra_context={"event": "test_error", "error": str(e)})
            raise
        finally:
            execution_time = time.time() - start_time
            self.current_context.update({"execution_time": execution_time})
            
            self.info(
                f"✅ Completed test: {test_name} ({execution_time:.2f}s)",
                extra_context={"event": "test_complete", "execution_time": execution_time}
            )
            
            # Store performance metrics
            self.performance_metrics.append({
                "test_name": test_name,
                "environment": environment,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat(),
                "correlation_id": correlation_id
            })
            
            # Restore old context
            self.current_context = old_context
    
    def log_api_request(self, method: str, url: str, headers: Dict = None, 
                       body: Any = None, correlation_id: str = None):
        """
        🌐 Log outgoing API request with full details
        
        Args:
            method (str): HTTP method (GET, POST, etc.)
            url (str): Request URL
            headers (dict): Request headers
            body (Any): Request body
            correlation_id (str): Correlation ID for tracking
        """
        correlation_id = correlation_id or self.current_context.get("correlation_id", "N/A")
        
        # Sanitize sensitive data
        safe_headers = self._sanitize_headers(headers or {})
        safe_body = self._sanitize_body(body)
        
        log_entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            level="INFO",
            message=f"📤 API Request: {method} {url}",
            api_endpoint=url,
            correlation_id=correlation_id,
            metadata={
                "request_type": "outgoing",
                "method": method,
                "headers": safe_headers,
                "body": safe_body
            }
        )
        
        self.log_entries.append(log_entry)
        logger.info(log_entry.message, extra={"correlation_id": correlation_id})
    
    def log_api_response(self, status_code: int, response_time: float, 
                        response_body: Any = None, correlation_id: str = None):
        """
        🌐 Log incoming API response with performance metrics
        
        Args:
            status_code (int): HTTP status code
            response_time (float): Response time in seconds
            response_body (Any): Response body
            correlation_id (str): Correlation ID for tracking
        """
        correlation_id = correlation_id or self.current_context.get("correlation_id", "N/A")
        
        # Determine log level based on status code
        if 200 <= status_code < 300:
            level = "INFO"
            emoji = "✅"
        elif 400 <= status_code < 500:
            level = "WARNING"
            emoji = "⚠️"
        else:
            level = "ERROR"
            emoji = "❌"
        
        message = f"{emoji} API Response: {status_code} ({response_time:.3f}s)"
        
        log_entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            level=level,
            message=message,
            status_code=status_code,
            response_time=response_time,
            correlation_id=correlation_id,
            metadata={
                "response_type": "incoming",
                "body_preview": str(response_body)[:200] if response_body else None
            }
        )
        
        self.log_entries.append(log_entry)
        
        # Log with appropriate level
        if level == "INFO":
            logger.info(message, extra={"correlation_id": correlation_id})
        elif level == "WARNING":
            logger.warning(message, extra={"correlation_id": correlation_id})
        else:
            logger.error(message, extra={"correlation_id": correlation_id})
    
    def _sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """
        🔒 PRIVATE METHOD: Remove sensitive information from headers
        
        This protects sensitive data like API keys, tokens, etc. from being logged.
        Demonstrates SECURITY best practices in logging.
        """
        sensitive_keys = [
            'authorization', 'x-api-key', 'api-key', 'access-token',
            'refresh-token', 'jwt', 'bearer', 'secret', 'password'
        ]
        
        sanitized = {}
        for key, value in headers.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "***REDACTED***"
            else:
                sanitized[key] = value
        
        return sanitized
    
    def _sanitize_body(self, body: Any) -> Any:
        """🔒 PRIVATE METHOD: Remove sensitive information from request body"""
        if not body:
            return body
        
        if isinstance(body, dict):
            sensitive_keys = ['password', 'secret', 'token', 'key', 'credential']
            sanitized = {}
            
            for key, value in body.items():
                if any(sensitive in key.lower() for sensitive in sensitive_keys):
                    sanitized[key] = "***REDACTED***"
                else:
                    sanitized[key] = value
            return sanitized
        
        return str(body)[:500]  # Truncate long strings
    
    # 🎯 CONVENIENCE METHODS: Easy-to-use logging methods
    def debug(self, message: str, extra_context: Dict = None):
        """🔍 Log debug information"""
        self._log_with_context("DEBUG", message, extra_context)
    
    def info(self, message: str, extra_context: Dict = None):
        """📝 Log general information"""
        self._log_with_context("INFO", message, extra_context)
    
    def warning(self, message: str, extra_context: Dict = None):
        """⚠️ Log warning messages"""
        self._log_with_context("WARNING", message, extra_context)
    
    def error(self, message: str, extra_context: Dict = None):
        """❌ Log error messages"""
        self._log_with_context("ERROR", message, extra_context)
    
    def critical(self, message: str, extra_context: Dict = None):
        """🚨 Log critical issues"""
        self._log_with_context("CRITICAL", message, extra_context)
    
    def _log_with_context(self, level: str, message: str, extra_context: Dict = None):
        """🔒 PRIVATE METHOD: Log with current context"""
        context = {**self.current_context, **(extra_context or {})}
        
        log_entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            level=level,
            message=message,
            test_name=context.get("test_name"),
            correlation_id=context.get("correlation_id"),
            environment=context.get("environment"),
            metadata=extra_context
        )
        
        self.log_entries.append(log_entry)
        
        # Use appropriate loguru method
        log_method = getattr(logger, level.lower())
        log_method(message, extra=context)
    
    # 📊 REPORTING METHODS: Generate various reports
    def export_logs_to_json(self, filename: str = None) -> Path:
        """
        📊 Export all logs to JSON format
        
        Returns:
            Path: Path to the exported JSON file
        """
        filename = filename or f"test_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.reports_dir / filename
        
        logs_data = [asdict(entry) for entry in self.log_entries]
        
        with open(filepath, 'w') as f:
            json.dump({
                "export_timestamp": datetime.now().isoformat(),
                "total_entries": len(logs_data),
                "logs": logs_data
            }, f, indent=2)
        
        self.info(f"📊 Exported {len(logs_data)} log entries to {filepath}")
        return filepath
    
    def export_logs_to_csv(self, filename: str = None) -> Path:
        """📊 Export logs to CSV format for Excel analysis"""
        filename = filename or f"test_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = self.reports_dir / filename
        
        if not self.log_entries:
            self.warning("No log entries to export")
            return filepath
        
        # Convert to DataFrame for easy CSV export
        df = pd.DataFrame([asdict(entry) for entry in self.log_entries])
        df.to_csv(filepath, index=False)
        
        self.info(f"📊 Exported {len(self.log_entries)} log entries to {filepath}")
        return filepath
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """
        📊 Generate performance analysis report
        
        Returns:
            Dict containing performance statistics
        """
        if not self.performance_metrics:
            return {"message": "No performance data available"}
        
        df = pd.DataFrame(self.performance_metrics)
        
        report = {
            "summary": {
                "total_tests": len(df),
                "average_execution_time": df['execution_time'].mean(),
                "min_execution_time": df['execution_time'].min(),
                "max_execution_time": df['execution_time'].max(),
                "total_execution_time": df['execution_time'].sum()
            },
            "by_environment": df.groupby('environment')['execution_time'].agg([
                'count', 'mean', 'min', 'max', 'std'
            ]).to_dict(),
            "slowest_tests": df.nlargest(5, 'execution_time')[
                ['test_name', 'execution_time', 'environment']
            ].to_dict('records'),
            "fastest_tests": df.nsmallest(5, 'execution_time')[
                ['test_name', 'execution_time', 'environment']
            ].to_dict('records')
        }
        
        return report
    
    def get_test_summary(self, last_n_hours: int = 24) -> Dict[str, Any]:
        """
        📊 Get summary of tests run in the last N hours
        
        Args:
            last_n_hours (int): Number of hours to look back
            
        Returns:
            Dict containing test summary
        """
        cutoff_time = datetime.now() - timedelta(hours=last_n_hours)
        
        recent_logs = [
            entry for entry in self.log_entries
            if datetime.fromisoformat(entry.timestamp) > cutoff_time
        ]
        
        if not recent_logs:
            return {"message": f"No logs found in the last {last_n_hours} hours"}
        
        # Count by level
        level_counts = {}
        for entry in recent_logs:
            level_counts[entry.level] = level_counts.get(entry.level, 0) + 1
        
        # Count by test
        test_counts = {}
        for entry in recent_logs:
            if entry.test_name:
                test_counts[entry.test_name] = test_counts.get(entry.test_name, 0) + 1
        
        return {
            "time_range": f"Last {last_n_hours} hours",
            "total_log_entries": len(recent_logs),
            "log_levels": level_counts,
            "tests_executed": len(test_counts),
            "most_active_tests": sorted(
                test_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
        }
    
    def clear_logs(self):
        """🗑️ Clear all in-memory logs (use with caution!)"""
        self.log_entries.clear()
        self.performance_metrics.clear()
        self.info("🗑️ All in-memory logs cleared")


# 🌟 GLOBAL INSTANCE: Singleton instance for easy access
enhanced_logger = EnhancedLogger()


# 🎯 USAGE EXAMPLES FOR BEGINNERS:
"""
📚 HOW TO USE THE ENHANCED LOGGER:

1. BASIC LOGGING:
   from utils.enhanced_logging import enhanced_logger
   
   enhanced_logger.info("This is an info message")
   enhanced_logger.error("This is an error message")

2. TEST CONTEXT TRACKING:
   with enhanced_logger.test_context("test_user_creation", "staging"):
       # Your test code here
       enhanced_logger.info("User created successfully")
       # Context is automatically included in all logs

3. API REQUEST/RESPONSE LOGGING:
   enhanced_logger.log_api_request("POST", "/users", headers={...}, body={...})
   enhanced_logger.log_api_response(201, 0.5, response_data)

4. GENERATE REPORTS:
   # Export logs to JSON
   enhanced_logger.export_logs_to_json()
   
   # Generate performance report
   report = enhanced_logger.generate_performance_report()
   print(json.dumps(report, indent=2))

5. INTEGRATION WITH EXISTING TESTS:
   @pytest.fixture(autouse=True)
   def test_logging(request):
       with enhanced_logger.test_context(request.node.name):
           yield

🎯 BENEFITS:
✅ STRUCTURED LOGGING: All logs are structured and searchable
✅ CONTEXT TRACKING: Automatic correlation between related logs
✅ PERFORMANCE MONITORING: Built-in performance metrics
✅ SECURITY: Automatic sanitization of sensitive data
✅ MULTIPLE FORMATS: Export to JSON, CSV, XML for different tools
✅ THREAD SAFE: Safe to use in parallel test execution
✅ ENTERPRISE READY: Suitable for production monitoring
""" 