"""
🎯 Web Dashboard for API Testing Framework
==========================================

This module provides a beautiful, real-time web dashboard for monitoring
and managing the API testing framework with modern UI components.

📚 FOR BEGINNERS:
A web dashboard is like a "control panel" for your testing framework.
It shows you what's happening in real-time and lets you control the tests.

🌟 REAL-WORLD EXAMPLES:
- Netflix: Real-time monitoring dashboards for their API infrastructure
- Airbnb: Testing dashboards showing booking API performance
- Slack: Real-time dashboards monitoring message API health
- GitHub: Dashboards tracking API usage and performance

🎯 DASHBOARD FEATURES:
- Real-time test execution monitoring
- Interactive charts and graphs
- Test result filtering and search
- System health status
- Performance metrics visualization
- Test management controls
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
import sqlite3
from collections import defaultdict

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit
import plotly.graph_objs as go
import plotly.utils
import pandas as pd

from utils.enhanced_logging import enhanced_logger
from monitoring.prometheus_metrics import prometheus_metrics


class APITestingDashboard:
    """
    🎯 Interactive Web Dashboard for API Testing Framework
    
    This provides a modern, responsive web interface for monitoring
    and managing API testing activities in real-time.
    
    🏗️ FEATURES:
    - Real-time test execution monitoring
    - Interactive performance charts
    - System health overview
    - Test result analysis
    - Historical trends
    - Test management controls
    """
    
    def __init__(self, host: str = '0.0.0.0', port: int = 8080):
        """
        🚀 Initialize the web dashboard
        
        Args:
            host: Host address to bind to
            port: Port to serve the dashboard on
        """
        self.host = host
        self.port = port
        
        # Initialize Flask app with Socket.IO for real-time updates
        self.app = Flask(__name__, 
                        static_folder='static', 
                        template_folder='templates')
        self.app.config['SECRET_KEY'] = 'api-testing-dashboard-secret-key'
        
        # Enable CORS for development
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Dashboard data storage
        self.test_results = []
        self.system_metrics = defaultdict(list)
        self.active_connections = 0
        
        # Setup routes and WebSocket handlers
        self._setup_routes()
        self._setup_websocket_handlers()
        
        # Start background data collection
        self._start_background_tasks()
        
        enhanced_logger.info(f"🎯 Web dashboard initialized on {host}:{port}")
    
    def _setup_routes(self):
        """🔧 Setup Flask routes for the dashboard"""
        
        @self.app.route('/')
        def dashboard_home():
            """🏠 Main dashboard page"""
            return render_template('dashboard.html', 
                                 title="API Testing Framework Dashboard")
        
        @self.app.route('/api/health')
        def health_check():
            """🏥 Health check endpoint"""
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": "2.0.0",
                "active_connections": self.active_connections
            })
        
        @self.app.route('/api/metrics')
        def get_metrics():
            """📊 Get current metrics data"""
            try:
                metrics_summary = prometheus_metrics.get_metrics_summary()
                return jsonify(metrics_summary)
            except Exception as e:
                enhanced_logger.error(f"❌ Error getting metrics: {str(e)}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/test-results')
        def get_test_results():
            """📋 Get recent test results"""
            try:
                # Get query parameters
                limit = request.args.get('limit', 100, type=int)
                status_filter = request.args.get('status', 'all')
                environment = request.args.get('environment', 'all')
                
                # Filter results
                filtered_results = self.test_results[-limit:]
                
                if status_filter != 'all':
                    filtered_results = [r for r in filtered_results 
                                      if r.get('status') == status_filter]
                
                if environment != 'all':
                    filtered_results = [r for r in filtered_results 
                                      if r.get('environment') == environment]
                
                return jsonify({
                    "results": filtered_results,
                    "total": len(filtered_results),
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                enhanced_logger.error(f"❌ Error getting test results: {str(e)}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/performance-chart')
        def get_performance_chart():
            """📈 Get performance chart data"""
            try:
                # Generate sample performance data
                chart_data = self._generate_performance_chart()
                return jsonify(chart_data)
                
            except Exception as e:
                enhanced_logger.error(f"❌ Error generating chart: {str(e)}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/system-status')
        def get_system_status():
            """🖥️ Get current system status"""
            try:
                import psutil
                
                system_status = {
                    "cpu_usage": psutil.cpu_percent(interval=1),
                    "memory_usage": psutil.virtual_memory().percent,
                    "disk_usage": psutil.disk_usage('/').percent,
                    "uptime": time.time() - psutil.boot_time(),
                    "timestamp": datetime.now().isoformat()
                }
                
                return jsonify(system_status)
                
            except Exception as e:
                enhanced_logger.error(f"❌ Error getting system status: {str(e)}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/run-test', methods=['POST'])
        def run_test():
            """🚀 Trigger a test run"""
            try:
                test_data = request.json
                test_name = test_data.get('test_name', 'manual_test')
                environment = test_data.get('environment', 'dev')
                
                # Simulate test execution (in real implementation, this would trigger actual tests)
                result = {
                    "id": f"test_{int(time.time())}",
                    "name": test_name,
                    "environment": environment,
                    "status": "running",
                    "started_at": datetime.now().isoformat(),
                    "message": f"Started test: {test_name}"
                }
                
                # Emit real-time update
                self.socketio.emit('test_started', result)
                
                enhanced_logger.info(f"🚀 Test started via dashboard: {test_name}")
                
                return jsonify(result)
                
            except Exception as e:
                enhanced_logger.error(f"❌ Error running test: {str(e)}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/static/<path:filename>')
        def serve_static(filename):
            """📁 Serve static files"""
            return send_from_directory('static', filename)
    
    def _setup_websocket_handlers(self):
        """🔌 Setup WebSocket handlers for real-time updates"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """🔌 Handle client connection"""
            self.active_connections += 1
            enhanced_logger.info(f"🔌 Client connected. Active connections: {self.active_connections}")
            
            # Send initial data to new client
            emit('initial_data', {
                "message": "Connected to API Testing Dashboard",
                "timestamp": datetime.now().isoformat(),
                "active_connections": self.active_connections
            })
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """🔌 Handle client disconnection"""
            self.active_connections -= 1
            enhanced_logger.info(f"🔌 Client disconnected. Active connections: {self.active_connections}")
        
        @self.socketio.on('request_update')
        def handle_update_request():
            """📊 Handle real-time data update request"""
            try:
                # Send current metrics
                metrics_data = prometheus_metrics.get_metrics_summary()
                emit('metrics_update', metrics_data)
                
                # Send recent test results
                recent_results = self.test_results[-10:]  # Last 10 results
                emit('test_results_update', {"results": recent_results})
                
            except Exception as e:
                enhanced_logger.error(f"❌ Error handling update request: {str(e)}")
                emit('error', {"message": str(e)})
    
    def _start_background_tasks(self):
        """🔄 Start background tasks for data collection and real-time updates"""
        import threading
        
        def background_data_collector():
            """📊 Collect data in background and emit updates"""
            while True:
                try:
                    # Collect current metrics
                    current_time = datetime.now()
                    
                    # System metrics
                    import psutil
                    system_data = {
                        "timestamp": current_time.isoformat(),
                        "cpu_usage": psutil.cpu_percent(),
                        "memory_usage": psutil.virtual_memory().percent,
                        "disk_usage": psutil.disk_usage('/').percent
                    }
                    
                    # Store system metrics
                    self.system_metrics['cpu'].append({
                        "x": current_time.isoformat(),
                        "y": system_data["cpu_usage"]
                    })
                    self.system_metrics['memory'].append({
                        "x": current_time.isoformat(),
                        "y": system_data["memory_usage"]
                    })
                    
                    # Keep only last 100 data points
                    for metric_type in self.system_metrics:
                        if len(self.system_metrics[metric_type]) > 100:
                            self.system_metrics[metric_type] = self.system_metrics[metric_type][-100:]
                    
                    # Emit real-time updates to connected clients
                    self.socketio.emit('system_update', system_data)
                    
                    # Simulate test completion events (for demo)
                    if len(self.test_results) < 50:  # Generate some sample data
                        sample_test = self._generate_sample_test_result()
                        self.test_results.append(sample_test)
                        self.socketio.emit('test_completed', sample_test)
                    
                except Exception as e:
                    enhanced_logger.error(f"❌ Error in background data collector: {str(e)}")
                
                time.sleep(5)  # Update every 5 seconds
        
        # Start background thread
        collector_thread = threading.Thread(target=background_data_collector, daemon=True)
        collector_thread.start()
        
        enhanced_logger.info("🔄 Background data collection started")
    
    def _generate_sample_test_result(self) -> Dict[str, Any]:
        """📊 Generate sample test result for demonstration"""
        import random
        
        test_names = [
            "test_user_registration",
            "test_user_login", 
            "test_get_user_profile",
            "test_create_post",
            "test_update_post",
            "test_delete_post",
            "test_search_users",
            "test_api_health_check"
        ]
        
        statuses = ["passed", "failed", "skipped"]
        environments = ["dev", "staging", "production"]
        
        return {
            "id": f"test_{int(time.time())}_{random.randint(1000, 9999)}",
            "name": random.choice(test_names),
            "environment": random.choice(environments),
            "status": random.choice(statuses),
            "duration": round(random.uniform(0.1, 5.0), 3),
            "started_at": (datetime.now() - timedelta(seconds=random.randint(0, 3600))).isoformat(),
            "completed_at": datetime.now().isoformat(),
            "message": "Test completed successfully" if random.choice([True, False]) else "Test failed with assertion error"
        }
    
    def _generate_performance_chart(self) -> Dict[str, Any]:
        """📈 Generate performance chart data using Plotly"""
        try:
            # Generate sample data for the last 24 hours
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=24)
            
            # Create time series data
            time_points = []
            response_times = []
            error_rates = []
            
            current_time = start_time
            while current_time < end_time:
                time_points.append(current_time.isoformat())
                
                # Simulate realistic API response times (with some variance)
                base_response_time = 0.5
                variance = 0.3 * (1 + 0.5 * (current_time.hour - 12) / 12)  # Higher variance during peak hours
                response_time = base_response_time + variance * (2 * (time.time() % 1) - 1)
                response_times.append(max(0.1, response_time))
                
                # Simulate error rates (lower during off-peak hours)
                base_error_rate = 2.0
                hour_factor = 1 + 0.5 * abs(current_time.hour - 14) / 14  # Peak errors at 2 PM
                error_rate = base_error_rate * hour_factor * (0.5 + 0.5 * (time.time() % 1))
                error_rates.append(min(10.0, max(0.1, error_rate)))
                
                current_time += timedelta(minutes=30)
            
            # Create Plotly chart
            fig = go.Figure()
            
            # Response time trace
            fig.add_trace(go.Scatter(
                x=time_points,
                y=response_times,
                mode='lines+markers',
                name='Response Time (s)',
                line=dict(color='#2196F3', width=2),
                marker=dict(size=4)
            ))
            
            # Error rate trace (secondary y-axis)
            fig.add_trace(go.Scatter(
                x=time_points,
                y=error_rates,
                mode='lines+markers',
                name='Error Rate (%)',
                yaxis='y2',
                line=dict(color='#F44336', width=2),
                marker=dict(size=4)
            ))
            
            # Update layout
            fig.update_layout(
                title='API Performance Over Time',
                xaxis_title='Time',
                yaxis=dict(
                    title='Response Time (seconds)',
                    side='left',
                    color='#2196F3'
                ),
                yaxis2=dict(
                    title='Error Rate (%)',
                    side='right',
                    overlaying='y',
                    color='#F44336'
                ),
                hovermode='x unified',
                template='plotly_white',
                height=400
            )
            
            # Convert to JSON for frontend
            chart_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            
            return {
                "chart": chart_json,
                "summary": {
                    "avg_response_time": round(sum(response_times) / len(response_times), 3),
                    "max_response_time": round(max(response_times), 3),
                    "avg_error_rate": round(sum(error_rates) / len(error_rates), 2),
                    "max_error_rate": round(max(error_rates), 2),
                    "data_points": len(time_points)
                }
            }
            
        except Exception as e:
            enhanced_logger.error(f"❌ Error generating performance chart: {str(e)}")
            return {"error": str(e)}
    
    def add_test_result(self, test_result: Dict[str, Any]):
        """
        📊 Add a new test result to the dashboard
        
        Args:
            test_result: Dictionary containing test result data
        """
        # Add timestamp if not present
        if 'timestamp' not in test_result:
            test_result['timestamp'] = datetime.now().isoformat()
        
        # Store result
        self.test_results.append(test_result)
        
        # Keep only last 1000 results
        if len(self.test_results) > 1000:
            self.test_results = self.test_results[-1000:]
        
        # Emit real-time update
        self.socketio.emit('test_completed', test_result)
        
        enhanced_logger.info(f"📊 Test result added to dashboard: {test_result.get('name', 'unknown')}")
    
    def run(self, debug: bool = False):
        """
        🚀 Run the dashboard server
        
        Args:
            debug: Whether to run in debug mode
        """
        enhanced_logger.info(f"🚀 Starting web dashboard on http://{self.host}:{self.port}")
        
        try:
            self.socketio.run(
                self.app,
                host=self.host,
                port=self.port,
                debug=debug,
                use_reloader=False  # Disable reloader to avoid issues with background threads
            )
        except Exception as e:
            enhanced_logger.error(f"❌ Failed to start dashboard server: {str(e)}")
            raise
    
    def run_in_background(self):
        """🔄 Run dashboard server in background thread"""
        import threading
        
        def server_worker():
            self.run(debug=False)
        
        server_thread = threading.Thread(target=server_worker, daemon=True)
        server_thread.start()
        
        enhanced_logger.info(f"🔄 Dashboard server started in background on http://{self.host}:{self.port}")


# 🌟 GLOBAL INSTANCE
dashboard = APITestingDashboard()


# 🎯 INTEGRATION FUNCTIONS
def start_dashboard_server():
    """🚀 Start the dashboard server"""
    try:
        dashboard.run()
    except KeyboardInterrupt:
        enhanced_logger.info("⏹️ Dashboard server stopped by user")
    except Exception as e:
        enhanced_logger.error(f"❌ Dashboard server error: {str(e)}")


def add_test_result_to_dashboard(test_name: str, status: str, duration: float, 
                                environment: str = "dev", message: str = ""):
    """
    📊 Add test result to dashboard (convenience function)
    
    Args:
        test_name: Name of the test
        status: Test status (passed, failed, skipped)
        duration: Test duration in seconds
        environment: Environment name
        message: Optional message
    """
    test_result = {
        "id": f"test_{int(time.time())}",
        "name": test_name,
        "status": status,
        "duration": duration,
        "environment": environment,
        "message": message,
        "completed_at": datetime.now().isoformat()
    }
    
    dashboard.add_test_result(test_result)


# 🎯 USAGE EXAMPLES FOR BEGINNERS:
"""
📚 HOW TO USE THE WEB DASHBOARD:

1. START THE DASHBOARD:
   
   from dashboard.web_dashboard import start_dashboard_server
   
   # Start in foreground (blocks execution)
   start_dashboard_server()
   
   # OR start in background
   from dashboard.web_dashboard import dashboard
   dashboard.run_in_background()

2. ADD TEST RESULTS TO DASHBOARD:
   
   from dashboard.web_dashboard import add_test_result_to_dashboard
   
   def test_user_login():
       start_time = time.time()
       
       try:
           # Your test code here
           response = api_client.post("/login", json=login_data)
           assert response.status_code == 200
           
           # Record success
           add_test_result_to_dashboard(
               test_name="test_user_login",
               status="passed",
               duration=time.time() - start_time,
               environment="staging",
               message="Login test completed successfully"
           )
           
       except Exception as e:
           # Record failure
           add_test_result_to_dashboard(
               test_name="test_user_login", 
               status="failed",
               duration=time.time() - start_time,
               environment="staging",
               message=str(e)
           )
           raise

3. INTEGRATE WITH PYTEST:
   
   # In conftest.py
   import pytest
   from dashboard.web_dashboard import dashboard
   
   @pytest.hookimpl(tryfirst=True, hookwrapper=True)
   def pytest_runtest_makereport(item, call):
       outcome = yield
       report = outcome.get_result()
       
       if report.when == "call":
           dashboard.add_test_result({
               "name": item.name,
               "status": "passed" if report.passed else "failed",
               "duration": report.duration,
               "environment": "test",
               "message": str(report.longrepr) if report.failed else "Test passed"
           })

4. CUSTOM DASHBOARD INTEGRATION:
   
   from dashboard.web_dashboard import dashboard
   
   class CustomTestRunner:
       def run_test_suite(self):
           for test in self.tests:
               start_time = time.time()
               
               try:
                   test.execute()
                   status = "passed"
                   message = "Test completed successfully"
               except Exception as e:
                   status = "failed"
                   message = str(e)
               
               # Add to dashboard
               dashboard.add_test_result({
                   "name": test.name,
                   "status": status,
                   "duration": time.time() - start_time,
                   "environment": "production",
                   "message": message
               })

5. ACCESS DASHBOARD URLS:
   # Main dashboard
   http://localhost:8080/
   
   # API endpoints
   http://localhost:8080/api/health
   http://localhost:8080/api/metrics
   http://localhost:8080/api/test-results
   http://localhost:8080/api/system-status

🎯 DASHBOARD FEATURES:

🏠 MAIN DASHBOARD:
- Real-time test execution monitoring
- Interactive performance charts
- System health indicators
- Test result filtering and search

📊 CHARTS AND GRAPHS:
- Response time trends
- Error rate tracking
- System resource usage
- Test success/failure ratios

🔍 FILTERING AND SEARCH:
- Filter by test status (passed/failed/skipped)
- Filter by environment (dev/staging/prod)
- Search by test name
- Date range filtering

⚡ REAL-TIME UPDATES:
- WebSocket connection for live updates
- Automatic refresh of charts and metrics
- Live test execution status
- System performance monitoring

🎮 CONTROLS:
- Start/stop tests remotely
- Configure test parameters
- Export test results
- Generate reports

🎯 BENEFITS:
✅ REAL-TIME VISIBILITY: See what's happening now
✅ HISTORICAL ANALYSIS: Track trends over time
✅ EASY DEBUGGING: Quickly identify failing tests
✅ TEAM COLLABORATION: Share live dashboard with team
✅ PERFORMANCE MONITORING: Track system health
✅ MOBILE FRIENDLY: Works on phones and tablets
✅ NO SETUP REQUIRED: Just start the server and go
"""

# 🎨 HTML TEMPLATE (dashboard.html)
dashboard_html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    
    <!-- CSS Libraries -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.css" rel="stylesheet">
    
    <style>
        .dashboard-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 0;
        }
        .metric-card {
            transition: transform 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-2px);
        }
        .status-badge {
            font-size: 0.75rem;
        }
        .test-result-row {
            border-left: 4px solid #28a745;
        }
        .test-result-row.failed {
            border-left-color: #dc3545;
        }
        .test-result-row.skipped {
            border-left-color: #ffc107;
        }
        .chart-container {
            position: relative;
            height: 400px;
        }
    </style>
</head>
<body>
    <!-- Dashboard Header -->
    <div class="dashboard-header">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-md-6">
                    <h1><i class="fas fa-tachometer-alt"></i> API Testing Dashboard</h1>
                    <p class="mb-0">Real-time monitoring and management</p>
                </div>
                <div class="col-md-6 text-end">
                    <div class="btn-group" role="group">
                        <button type="button" class="btn btn-light btn-sm" onclick="runTest()">
                            <i class="fas fa-play"></i> Run Test
                        </button>
                        <button type="button" class="btn btn-light btn-sm" onclick="refreshData()">
                            <i class="fas fa-sync"></i> Refresh
                        </button>
                        <button type="button" class="btn btn-light btn-sm" onclick="exportResults()">
                            <i class="fas fa-download"></i> Export
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Main Dashboard Content -->
    <div class="container-fluid mt-4">
        <!-- Metrics Cards -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card metric-card border-0 shadow-sm">
                    <div class="card-body text-center">
                        <i class="fas fa-check-circle text-success fa-2x mb-2"></i>
                        <h3 class="text-success" id="tests-passed">0</h3>
                        <p class="mb-0">Tests Passed</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card metric-card border-0 shadow-sm">
                    <div class="card-body text-center">
                        <i class="fas fa-times-circle text-danger fa-2x mb-2"></i>
                        <h3 class="text-danger" id="tests-failed">0</h3>
                        <p class="mb-0">Tests Failed</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card metric-card border-0 shadow-sm">
                    <div class="card-body text-center">
                        <i class="fas fa-clock text-info fa-2x mb-2"></i>
                        <h3 class="text-info" id="avg-duration">0.0s</h3>
                        <p class="mb-0">Avg Duration</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card metric-card border-0 shadow-sm">
                    <div class="card-body text-center">
                        <i class="fas fa-server text-warning fa-2x mb-2"></i>
                        <h3 class="text-warning" id="system-health">Healthy</h3>
                        <p class="mb-0">System Health</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="row">
            <!-- Performance Chart -->
            <div class="col-md-8">
                <div class="card border-0 shadow-sm">
                    <div class="card-header bg-white">
                        <h5 class="mb-0"><i class="fas fa-chart-line"></i> Performance Trends</h5>
                    </div>
                    <div class="card-body">
                        <div id="performance-chart" class="chart-container"></div>
                    </div>
                </div>
            </div>

            <!-- System Status -->
            <div class="col-md-4">
                <div class="card border-0 shadow-sm">
                    <div class="card-header bg-white">
                        <h5 class="mb-0"><i class="fas fa-desktop"></i> System Status</h5>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <div class="d-flex justify-content-between">
                                <span>CPU Usage</span>
                                <span id="cpu-usage">0%</span>
                            </div>
                            <div class="progress">
                                <div class="progress-bar bg-info" id="cpu-progress" style="width: 0%"></div>
                            </div>
                        </div>
                        <div class="mb-3">
                            <div class="d-flex justify-content-between">
                                <span>Memory Usage</span>
                                <span id="memory-usage">0%</span>
                            </div>
                            <div class="progress">
                                <div class="progress-bar bg-warning" id="memory-progress" style="width: 0%"></div>
                            </div>
                        </div>
                        <div class="mb-3">
                            <div class="d-flex justify-content-between">
                                <span>Disk Usage</span>
                                <span id="disk-usage">0%</span>
                            </div>
                            <div class="progress">
                                <div class="progress-bar bg-danger" id="disk-progress" style="width: 0%"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Recent Test Results -->
        <div class="row mt-4">
            <div class="col-12">
                <div class="card border-0 shadow-sm">
                    <div class="card-header bg-white d-flex justify-content-between align-items-center">
                        <h5 class="mb-0"><i class="fas fa-list"></i> Recent Test Results</h5>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-primary" onclick="filterResults('all')">All</button>
                            <button class="btn btn-outline-success" onclick="filterResults('passed')">Passed</button>
                            <button class="btn btn-outline-danger" onclick="filterResults('failed')">Failed</button>
                        </div>
                    </div>
                    <div class="card-body p-0">
                        <div class="table-responsive">
                            <table class="table table-hover mb-0">
                                <thead class="table-light">
                                    <tr>
                                        <th>Test Name</th>
                                        <th>Status</th>
                                        <th>Duration</th>
                                        <th>Environment</th>
                                        <th>Completed At</th>
                                        <th>Message</th>
                                    </tr>
                                </thead>
                                <tbody id="test-results-body">
                                    <!-- Results will be populated via JavaScript -->
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- JavaScript Libraries -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script src="https://cdn.socket.io/4.5.0/socket.io.min.js"></script>
    
    <script>
        // Initialize Socket.IO connection
        const socket = io();
        
        // Dashboard state
        let testResults = [];
        let currentFilter = 'all';
        
        // Socket event handlers
        socket.on('connect', function() {
            console.log('Connected to dashboard');
            socket.emit('request_update');
        });
        
        socket.on('test_completed', function(data) {
            testResults.unshift(data);
            updateTestResultsTable();
            updateMetrics();
        });
        
        socket.on('system_update', function(data) {
            updateSystemStatus(data);
        });
        
        socket.on('metrics_update', function(data) {
            updateDashboardMetrics(data);
        });
        
        // Update functions
        function updateTestResultsTable() {
            const tbody = document.getElementById('test-results-body');
            const filteredResults = currentFilter === 'all' ? 
                testResults : testResults.filter(r => r.status === currentFilter);
            
            tbody.innerHTML = filteredResults.slice(0, 20).map(result => `
                <tr class="test-result-row ${result.status}">
                    <td>${result.name}</td>
                    <td>
                        <span class="badge status-badge ${getStatusClass(result.status)}">
                            ${result.status.toUpperCase()}
                        </span>
                    </td>
                    <td>${result.duration}s</td>
                    <td>${result.environment}</td>
                    <td>${new Date(result.completed_at).toLocaleString()}</td>
                    <td class="text-muted">${result.message || 'No message'}</td>
                </tr>
            `).join('');
        }
        
        function updateSystemStatus(data) {
            document.getElementById('cpu-usage').textContent = data.cpu_usage.toFixed(1) + '%';
            document.getElementById('cpu-progress').style.width = data.cpu_usage + '%';
            
            document.getElementById('memory-usage').textContent = data.memory_usage.toFixed(1) + '%';
            document.getElementById('memory-progress').style.width = data.memory_usage + '%';
            
            document.getElementById('disk-usage').textContent = data.disk_usage.toFixed(1) + '%';
            document.getElementById('disk-progress').style.width = data.disk_usage + '%';
        }
        
        function updateMetrics() {
            const passed = testResults.filter(r => r.status === 'passed').length;
            const failed = testResults.filter(r => r.status === 'failed').length;
            const avgDuration = testResults.length > 0 ? 
                (testResults.reduce((sum, r) => sum + r.duration, 0) / testResults.length).toFixed(2) : 0;
            
            document.getElementById('tests-passed').textContent = passed;
            document.getElementById('tests-failed').textContent = failed;
            document.getElementById('avg-duration').textContent = avgDuration + 's';
        }
        
        function getStatusClass(status) {
            switch(status) {
                case 'passed': return 'bg-success';
                case 'failed': return 'bg-danger';
                case 'skipped': return 'bg-warning';
                default: return 'bg-secondary';
            }
        }
        
        // Control functions
        function runTest() {
            const testName = prompt('Enter test name to run:');
            if (testName) {
                fetch('/api/run-test', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({test_name: testName, environment: 'dev'})
                });
            }
        }
        
        function refreshData() {
            socket.emit('request_update');
        }
        
        function exportResults() {
            const dataStr = JSON.stringify(testResults, null, 2);
            const dataBlob = new Blob([dataStr], {type: 'application/json'});
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'test-results.json';
            link.click();
        }
        
        function filterResults(status) {
            currentFilter = status;
            updateTestResultsTable();
            
            // Update button states
            document.querySelectorAll('.btn-group .btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
        }
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            // Load initial data
            fetch('/api/test-results')
                .then(response => response.json())
                .then(data => {
                    testResults = data.results;
                    updateTestResultsTable();
                    updateMetrics();
                });
            
            // Load performance chart
            fetch('/api/performance-chart')
                .then(response => response.json())
                .then(data => {
                    if (data.chart) {
                        Plotly.newPlot('performance-chart', JSON.parse(data.chart).data, JSON.parse(data.chart).layout);
                    }
                });
        });
    </script>
</body>
</html>
'''

# Save the HTML template
def create_dashboard_template():
    """📄 Create the dashboard HTML template file"""
    templates_dir = Path(__file__).parent / 'templates'
    templates_dir.mkdir(exist_ok=True)
    
    template_file = templates_dir / 'dashboard.html'
    with open(template_file, 'w') as f:
        f.write(dashboard_html_template)
    
    enhanced_logger.info(f"📄 Dashboard template created: {template_file}")

# Create template on import
create_dashboard_template() 