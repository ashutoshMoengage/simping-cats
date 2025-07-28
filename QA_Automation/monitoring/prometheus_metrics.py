"""
🎯 Prometheus Metrics Integration for API Testing Framework
===========================================================

This module provides comprehensive metrics collection for monitoring the
API testing framework using Prometheus - the industry standard monitoring system.

📚 FOR BEGINNERS:
Prometheus is like a "health monitor" for your applications. It collects metrics
(numbers) about how your app is performing and stores them over time.

🌟 REAL-WORLD EXAMPLES:
- Netflix: Monitors millions of API requests per second
- Google: Uses Prometheus for internal service monitoring  
- Spotify: Tracks API performance and user experience
- Uber: Monitors ride request APIs in real-time

🎯 METRICS WE COLLECT:
- Test execution counts and durations
- API response times and error rates
- System resource usage (CPU, memory)
- Test success/failure rates
- Framework health status
"""

import time
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import defaultdict
import psutil
import json

from prometheus_client import (
    Counter, Histogram, Gauge, Info, Enum, 
    CollectorRegistry, generate_latest, 
    start_http_server, CONTENT_TYPE_LATEST
)
from flask import Flask, Response, jsonify

from utils.enhanced_logging import enhanced_logger


class PrometheusMetrics:
    """
    🎯 Prometheus Metrics Collector for API Testing Framework
    
    This class provides comprehensive monitoring metrics for production environments.
    
    🏗️ OOP CONCEPTS:
    - SINGLETON PATTERN: Only one metrics instance across the application
    - COMPOSITION: Uses prometheus_client internally
    - ENCAPSULATION: Private methods for internal metric management
    
    📊 METRICS TYPES:
    - COUNTER: Things that only increase (total requests, errors)
    - HISTOGRAM: Measurements with buckets (response times, request sizes)
    - GAUGE: Values that go up and down (active connections, memory usage)
    - INFO: Static information (version, configuration)
    - ENUM: State information (health status)
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """🔒 Singleton implementation for metrics collector"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """🚀 Initialize Prometheus metrics collector"""
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        
        # Create custom registry for better organization
        self.registry = CollectorRegistry()
        
        # 📊 TEST EXECUTION METRICS
        self.test_executions_total = Counter(
            'api_test_executions_total',
            'Total number of API tests executed',
            ['test_name', 'test_type', 'environment', 'status'],
            registry=self.registry
        )
        
        self.test_duration_seconds = Histogram(
            'api_test_duration_seconds',
            'Time spent executing API tests',
            ['test_name', 'test_type', 'environment'],
            buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, float('inf')),
            registry=self.registry
        )
        
        # 🌐 API REQUEST METRICS
        self.api_requests_total = Counter(
            'api_requests_total',
            'Total number of API requests made',
            ['method', 'endpoint', 'status_code', 'environment'],
            registry=self.registry
        )
        
        self.api_request_duration_seconds = Histogram(
            'api_request_duration_seconds',
            'Time spent on API requests',
            ['method', 'endpoint', 'environment'],
            buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, float('inf')),
            registry=self.registry
        )
        
        self.api_request_size_bytes = Histogram(
            'api_request_size_bytes',
            'Size of API request payloads',
            ['method', 'endpoint'],
            buckets=(64, 256, 1024, 4096, 16384, 65536, 262144, 1048576, float('inf')),
            registry=self.registry
        )
        
        self.api_response_size_bytes = Histogram(
            'api_response_size_bytes',
            'Size of API response payloads',
            ['method', 'endpoint'],
            buckets=(64, 256, 1024, 4096, 16384, 65536, 262144, 1048576, float('inf')),
            registry=self.registry
        )
        
        # 📈 PERFORMANCE METRICS
        self.active_tests_gauge = Gauge(
            'api_tests_active',
            'Number of currently running tests',
            ['environment'],
            registry=self.registry
        )
        
        self.test_queue_size = Gauge(
            'api_test_queue_size',
            'Number of tests waiting to be executed',
            ['environment'],
            registry=self.registry
        )
        
        # 🖥️ SYSTEM RESOURCE METRICS
        self.cpu_usage_percent = Gauge(
            'system_cpu_usage_percent',
            'Current CPU usage percentage',
            registry=self.registry
        )
        
        self.memory_usage_bytes = Gauge(
            'system_memory_usage_bytes',
            'Current memory usage in bytes',
            registry=self.registry
        )
        
        self.memory_usage_percent = Gauge(
            'system_memory_usage_percent',
            'Current memory usage percentage',
            registry=self.registry
        )
        
        self.disk_usage_bytes = Gauge(
            'system_disk_usage_bytes',
            'Current disk usage in bytes',
            ['path'],
            registry=self.registry
        )
        
        # 🌐 NETWORK METRICS
        self.network_bytes_sent = Counter(
            'network_bytes_sent_total',
            'Total bytes sent over network',
            registry=self.registry
        )
        
        self.network_bytes_received = Counter(
            'network_bytes_received_total',
            'Total bytes received over network',
            registry=self.registry
        )
        
        # ❌ ERROR METRICS
        self.test_errors_total = Counter(
            'api_test_errors_total',
            'Total number of test errors',
            ['test_name', 'error_type', 'environment'],
            registry=self.registry
        )
        
        self.assertion_failures_total = Counter(
            'api_assertion_failures_total',
            'Total number of assertion failures',
            ['assertion_type', 'test_name', 'environment'],
            registry=self.registry
        )
        
        # 🏥 HEALTH METRICS
        self.framework_health = Enum(
            'api_framework_health',
            'Overall health status of the testing framework',
            ['environment'],
            states=['healthy', 'degraded', 'unhealthy'],
            registry=self.registry
        )
        
        self.database_connections_active = Gauge(
            'database_connections_active',
            'Number of active database connections',
            ['database_type'],
            registry=self.registry
        )
        
        # 📊 FRAMEWORK INFO
        self.framework_info = Info(
            'api_framework_info',
            'Information about the API testing framework',
            registry=self.registry
        )
        
        # Set framework information
        self.framework_info.info({
            'version': '2.0.0',
            'python_version': '3.11',
            'pytest_version': '7.4.3',
            'environment': 'production',
            'build_date': datetime.now().isoformat(),
        })
        
        # 🔄 Background monitoring
        self._start_system_monitoring()
        
        enhanced_logger.info("🎯 Prometheus metrics collector initialized")
    
    def _start_system_monitoring(self):
        """🔄 Start background thread for system resource monitoring"""
        def monitor_system_resources():
            while True:
                try:
                    # CPU usage
                    cpu_percent = psutil.cpu_percent(interval=1)
                    self.cpu_usage_percent.set(cpu_percent)
                    
                    # Memory usage
                    memory = psutil.virtual_memory()
                    self.memory_usage_bytes.set(memory.used)
                    self.memory_usage_percent.set(memory.percent)
                    
                    # Disk usage
                    disk = psutil.disk_usage('/')
                    self.disk_usage_bytes.labels(path='/').set(disk.used)
                    
                    # Network I/O
                    network = psutil.net_io_counters()
                    self.network_bytes_sent._value._value = network.bytes_sent
                    self.network_bytes_received._value._value = network.bytes_recv
                    
                except Exception as e:
                    enhanced_logger.error(f"❌ Error monitoring system resources: {str(e)}")
                
                time.sleep(10)  # Update every 10 seconds
        
        monitor_thread = threading.Thread(target=monitor_system_resources, daemon=True)
        monitor_thread.start()
    
    # 🎯 METRIC RECORDING METHODS
    
    def record_test_execution(self, test_name: str, test_type: str, 
                            environment: str, status: str, duration: float):
        """
        📊 Record test execution metrics
        
        Args:
            test_name: Name of the test
            test_type: Type of test (unit, integration, e2e)
            environment: Environment (dev, staging, prod)
            status: Test status (passed, failed, skipped)
            duration: Test execution time in seconds
            
        Real Example:
            metrics.record_test_execution(
                "test_user_creation",
                "integration", 
                "staging",
                "passed",
                2.5
            )
        """
        self.test_executions_total.labels(
            test_name=test_name,
            test_type=test_type,
            environment=environment,
            status=status
        ).inc()
        
        self.test_duration_seconds.labels(
            test_name=test_name,
            test_type=test_type,
            environment=environment
        ).observe(duration)
        
        enhanced_logger.info(
            f"📊 Recorded test execution: {test_name} ({status}) in {duration:.3f}s",
            extra_context={
                "metric_type": "test_execution",
                "test_name": test_name,
                "status": status,
                "duration": duration
            }
        )
    
    def record_api_request(self, method: str, endpoint: str, environment: str,
                          status_code: int, duration: float, 
                          request_size: int = 0, response_size: int = 0):
        """
        🌐 Record API request metrics
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            environment: Environment name
            status_code: HTTP status code
            duration: Request duration in seconds
            request_size: Request payload size in bytes
            response_size: Response payload size in bytes
            
        Real Example:
            metrics.record_api_request(
                "POST",
                "/users",
                "production", 
                201,
                0.5,
                request_size=256,
                response_size=512
            )
        """
        self.api_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code),
            environment=environment
        ).inc()
        
        self.api_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint,
            environment=environment
        ).observe(duration)
        
        if request_size > 0:
            self.api_request_size_bytes.labels(
                method=method,
                endpoint=endpoint
            ).observe(request_size)
        
        if response_size > 0:
            self.api_response_size_bytes.labels(
                method=method,
                endpoint=endpoint
            ).observe(response_size)
    
    def record_test_error(self, test_name: str, error_type: str, 
                         environment: str, error_message: str = None):
        """
        ❌ Record test error metrics
        
        Args:
            test_name: Name of the failing test
            error_type: Type of error (timeout, assertion, connection)
            environment: Environment name
            error_message: Optional error message
            
        Real Example:
            metrics.record_test_error(
                "test_user_login",
                "assertion_error",
                "staging",
                "Expected status 200, got 500"
            )
        """
        self.test_errors_total.labels(
            test_name=test_name,
            error_type=error_type,
            environment=environment
        ).inc()
        
        enhanced_logger.error(
            f"❌ Recorded test error: {test_name} ({error_type})",
            extra_context={
                "metric_type": "test_error",
                "test_name": test_name,
                "error_type": error_type,
                "error_message": error_message
            }
        )
    
    def record_assertion_failure(self, assertion_type: str, test_name: str, 
                                environment: str):
        """
        🔍 Record assertion failure metrics
        
        Args:
            assertion_type: Type of assertion (status_code, json_schema, etc.)
            test_name: Name of the test
            environment: Environment name
        """
        self.assertion_failures_total.labels(
            assertion_type=assertion_type,
            test_name=test_name,
            environment=environment
        ).inc()
    
    def set_active_tests(self, count: int, environment: str):
        """📈 Set number of currently active tests"""
        self.active_tests_gauge.labels(environment=environment).set(count)
    
    def set_test_queue_size(self, size: int, environment: str):
        """📋 Set test queue size"""
        self.test_queue_size.labels(environment=environment).set(size)
    
    def set_framework_health(self, status: str, environment: str):
        """
        🏥 Set framework health status
        
        Args:
            status: Health status ('healthy', 'degraded', 'unhealthy')
            environment: Environment name
        """
        self.framework_health.labels(environment=environment).state(status)
        
        enhanced_logger.info(
            f"🏥 Framework health updated: {status}",
            extra_context={"health_status": status, "environment": environment}
        )
    
    def set_database_connections(self, count: int, database_type: str):
        """🗄️ Set active database connections"""
        self.database_connections_active.labels(database_type=database_type).set(count)
    
    def get_metrics(self) -> str:
        """
        📊 Get all metrics in Prometheus format
        
        Returns:
            str: Metrics in Prometheus exposition format
        """
        return generate_latest(self.registry).decode('utf-8')
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        📈 Get human-readable metrics summary
        
        Returns:
            dict: Summary of key metrics
        """
        try:
            # Get current metric values
            summary = {
                "timestamp": datetime.now().isoformat(),
                "system": {
                    "cpu_usage_percent": psutil.cpu_percent(),
                    "memory_usage_percent": psutil.virtual_memory().percent,
                    "disk_usage_gb": psutil.disk_usage('/').used / (1024**3),
                },
                "framework": {
                    "health_status": "healthy",  # This would be dynamically determined
                    "active_tests": 0,  # This would be the current gauge value
                    "test_queue_size": 0,
                },
                "totals": {
                    "total_tests_executed": 0,  # Sum of all test counters
                    "total_api_requests": 0,    # Sum of all API request counters
                    "total_errors": 0,          # Sum of all error counters
                }
            }
            
            return summary
            
        except Exception as e:
            enhanced_logger.error(f"❌ Error generating metrics summary: {str(e)}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}


class MetricsServer:
    """
    🌐 HTTP Server for Prometheus Metrics Endpoint
    
    This provides an HTTP endpoint that Prometheus can scrape to collect metrics.
    
    📚 FOR BEGINNERS:
    Prometheus works by "scraping" (reading) metrics from HTTP endpoints.
    This server provides that endpoint at /metrics.
    """
    
    def __init__(self, metrics: PrometheusMetrics, port: int = 9090):
        """
        🚀 Initialize metrics server
        
        Args:
            metrics: PrometheusMetrics instance
            port: Port to serve metrics on (default: 9090)
        """
        self.metrics = metrics
        self.port = port
        self.app = Flask(__name__)
        
        # Configure Flask routes
        self._setup_routes()
        
        enhanced_logger.info(f"🌐 Metrics server initialized on port {port}")
    
    def _setup_routes(self):
        """🔧 Setup Flask routes for metrics endpoints"""
        
        @self.app.route('/metrics')
        def metrics_endpoint():
            """📊 Prometheus metrics endpoint"""
            return Response(
                self.metrics.get_metrics(),
                mimetype=CONTENT_TYPE_LATEST
            )
        
        @self.app.route('/health')
        def health_endpoint():
            """🏥 Health check endpoint"""
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": "2.0.0"
            })
        
        @self.app.route('/ready')
        def readiness_endpoint():
            """✅ Readiness check endpoint"""
            return jsonify({
                "ready": True,
                "timestamp": datetime.now().isoformat()
            })
        
        @self.app.route('/metrics/summary')
        def metrics_summary_endpoint():
            """📈 Human-readable metrics summary"""
            return jsonify(self.metrics.get_metrics_summary())
        
        @self.app.route('/')
        def root_endpoint():
            """🏠 Root endpoint with information"""
            return jsonify({
                "service": "API Testing Framework Metrics",
                "version": "2.0.0",
                "endpoints": {
                    "/metrics": "Prometheus metrics",
                    "/health": "Health check",
                    "/ready": "Readiness check",
                    "/metrics/summary": "Human-readable summary"
                },
                "timestamp": datetime.now().isoformat()
            })
    
    def start(self, debug: bool = False):
        """
        🚀 Start the metrics server
        
        Args:
            debug: Whether to run in debug mode
        """
        enhanced_logger.info(f"🚀 Starting metrics server on port {self.port}")
        
        try:
            self.app.run(
                host='0.0.0.0',
                port=self.port,
                debug=debug,
                threaded=True,
                use_reloader=False  # Disable reloader to avoid duplicate metrics
            )
        except Exception as e:
            enhanced_logger.error(f"❌ Failed to start metrics server: {str(e)}")
            raise
    
    def start_in_background(self):
        """🔄 Start metrics server in background thread"""
        def server_worker():
            self.start(debug=False)
        
        server_thread = threading.Thread(target=server_worker, daemon=True)
        server_thread.start()
        
        enhanced_logger.info(f"🔄 Metrics server started in background on port {self.port}")


# 🌟 GLOBAL INSTANCES
prometheus_metrics = PrometheusMetrics()
metrics_server = MetricsServer(prometheus_metrics)


# 🎯 INTEGRATION DECORATORS
def track_test_execution(test_type: str = "integration", environment: str = "dev"):
    """
    🎯 Decorator to automatically track test execution metrics
    
    Args:
        test_type: Type of test (unit, integration, e2e)
        environment: Environment name
        
    Usage:
        @track_test_execution("integration", "staging")
        def test_user_creation():
            # Your test code here
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            test_name = func.__name__
            start_time = time.time()
            status = "failed"  # Default to failed
            
            try:
                # Execute the test
                result = func(*args, **kwargs)
                status = "passed"
                return result
                
            except Exception as e:
                status = "failed"
                prometheus_metrics.record_test_error(
                    test_name, 
                    type(e).__name__,
                    environment,
                    str(e)
                )
                raise
                
            finally:
                # Record execution metrics
                duration = time.time() - start_time
                prometheus_metrics.record_test_execution(
                    test_name,
                    test_type,
                    environment,
                    status,
                    duration
                )
        
        return wrapper
    return decorator


# 🎯 USAGE EXAMPLES FOR BEGINNERS:
"""
📚 HOW TO USE PROMETHEUS METRICS:

1. BASIC METRIC RECORDING:
   
   from monitoring.prometheus_metrics import prometheus_metrics
   
   def test_api_endpoint():
       start_time = time.time()
       
       # Make API call
       response = api_client.get("/users")
       
       # Record metrics
       prometheus_metrics.record_api_request(
           method="GET",
           endpoint="/users",
           environment="staging",
           status_code=response.status_code,
           duration=time.time() - start_time,
           response_size=len(response.content)
       )

2. USING DECORATORS (Easiest way):
   
   from monitoring.prometheus_metrics import track_test_execution
   
   @track_test_execution("integration", "production")
   def test_user_registration():
       # Your test code here
       # Metrics are automatically recorded!
       response = api_client.post("/register", json=user_data)
       assert response.status_code == 201

3. CUSTOM METRICS FOR YOUR API:
   
   # Record business-specific metrics
   prometheus_metrics.record_test_execution(
       test_name="checkout_process_test",
       test_type="e2e",
       environment="production",
       status="passed",
       duration=5.2
   )
   
   # Set health status
   prometheus_metrics.set_framework_health("healthy", "production")

4. START METRICS SERVER:
   
   from monitoring.prometheus_metrics import metrics_server
   
   # Start in background (recommended for tests)
   metrics_server.start_in_background()
   
   # OR start in foreground (for dedicated metrics service)
   metrics_server.start()

5. VIEW METRICS:
   
   # Prometheus format (for Prometheus server)
   curl http://localhost:9090/metrics
   
   # Human-readable summary (for debugging)
   curl http://localhost:9090/metrics/summary
   
   # Health check (for Kubernetes)
   curl http://localhost:9090/health

🎯 PROMETHEUS CONFIGURATION:
Add this to your prometheus.yml:

scrape_configs:
  - job_name: 'api-testing-framework'
    static_configs:
      - targets: ['localhost:9090']
    scrape_interval: 15s
    metrics_path: /metrics

🎯 GRAFANA DASHBOARDS:
Create dashboards with queries like:
- Test success rate: rate(api_test_executions_total{status="passed"}[5m])
- API response time: histogram_quantile(0.95, api_request_duration_seconds_bucket)
- Error rate: rate(api_test_errors_total[5m])
- System CPU: system_cpu_usage_percent

🎯 ALERTING RULES:
Create alerts in Prometheus:
- High error rate: rate(api_test_errors_total[5m]) > 0.1
- Slow API responses: histogram_quantile(0.95, api_request_duration_seconds_bucket) > 2
- Framework unhealthy: api_framework_health != 1

📊 BENEFITS:
✅ REAL-TIME MONITORING: See test performance as it happens
✅ HISTORICAL ANALYSIS: Track trends over time
✅ ALERTING: Get notified when things go wrong
✅ CAPACITY PLANNING: Understand resource usage
✅ DEBUGGING: Identify performance bottlenecks
✅ SLA MONITORING: Track service level objectives
✅ BUSINESS INSIGHTS: Understand test impact on business metrics
""" 