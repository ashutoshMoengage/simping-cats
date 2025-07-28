"""
🎯 Performance Benchmarking Tools
=================================

This module provides comprehensive performance testing and benchmarking tools
for API testing with REAL examples and industry-standard metrics.

📚 FOR BEGINNERS:
Performance testing ensures your API can handle:
- Expected user load (how many users can use it simultaneously)
- Response time requirements (how fast it responds)
- Resource usage (CPU, memory, network)
- Breaking points (when does it start to fail)

🌟 REAL-WORLD EXAMPLES:
- E-commerce: Black Friday traffic spikes
- Social Media: Viral content load spikes  
- Banking: End-of-month transaction volumes
- Gaming: New game release server load
- News: Breaking news traffic surges

🎯 PERFORMANCE METRICS WE MEASURE:
- Response Time (Latency)
- Throughput (Requests per second)  
- Error Rate (Failed requests %)
- Concurrent Users (Simultaneous users)
- Resource Utilization (CPU, Memory)
"""

import time
import threading
import statistics
import concurrent.futures
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable, Tuple
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
import json

import requests
import psutil
import matplotlib.pyplot as plt
import pandas as pd

from utils.enhanced_logging import enhanced_logger
from utils.api_client import APIClient


@dataclass
class PerformanceMetrics:
    """
    📊 Performance Metrics Data Structure
    
    This represents comprehensive performance measurements for a single test.
    """
    test_name: str
    start_time: str
    end_time: str
    duration_seconds: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    requests_per_second: float
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p50_response_time: float  # 50th percentile (median)
    p90_response_time: float  # 90th percentile
    p95_response_time: float  # 95th percentile
    p99_response_time: float  # 99th percentile
    error_rate: float
    concurrent_users: int
    cpu_usage_percent: float
    memory_usage_mb: float
    network_sent_mb: float
    network_received_mb: float


@dataclass
class LoadTestRequest:
    """📋 Single request result in load testing"""
    timestamp: float
    response_time: float
    status_code: int
    success: bool
    error_message: Optional[str] = None
    request_size_bytes: int = 0
    response_size_bytes: int = 0


class PerformanceBenchmark:
    """
    🎯 Performance Benchmarking Engine
    
    This class provides comprehensive performance testing capabilities:
    - Load testing with multiple concurrent users
    - Stress testing to find breaking points
    - Spike testing for traffic surges
    - Endurance testing for long-term stability
    
    📚 BEGINNER EXPLANATION:
    Think of this like testing how many people can use an elevator:
    - Load Test: Normal capacity (10 people)
    - Stress Test: Beyond capacity (15 people) 
    - Spike Test: Sudden rush (20 people at once)
    - Endurance Test: All day usage
    """
    
    def __init__(self, api_client: APIClient = None):
        """
        🚀 Initialize performance benchmarking engine
        
        Args:
            api_client: APIClient instance for making requests
        """
        self.api_client = api_client
        self.results_history: List[PerformanceMetrics] = []
        
        # System monitoring
        self.initial_cpu = psutil.cpu_percent()
        self.initial_memory = psutil.virtual_memory().used / 1024 / 1024  # MB
        self.initial_network = psutil.net_io_counters()
        
        enhanced_logger.info("🎯 Performance benchmarking engine initialized")
    
    def run_load_test(self, 
                     endpoint: str,
                     method: str = "GET",
                     concurrent_users: int = 10,
                     duration_seconds: int = 30,
                     request_data: Dict[str, Any] = None,
                     headers: Dict[str, str] = None,
                     test_name: str = None) -> PerformanceMetrics:
        """
        🚀 LOAD TESTING: Test API under normal expected load
        
        Args:
            endpoint: API endpoint to test
            method: HTTP method (GET, POST, etc.)
            concurrent_users: Number of simulated concurrent users
            duration_seconds: How long to run the test
            request_data: Request payload for POST/PUT
            headers: Custom headers
            test_name: Name for this test
            
        Returns:
            PerformanceMetrics: Comprehensive performance results
            
        Real Example - E-commerce Product API:
            metrics = benchmark.run_load_test(
                endpoint="/products",
                concurrent_users=50,
                duration_seconds=60,
                test_name="Product_Listing_Normal_Load"
            )
        """
        test_name = test_name or f"LoadTest_{endpoint}_{concurrent_users}users"
        start_time = datetime.now()
        
        enhanced_logger.info(
            f"🚀 Starting load test: {test_name}",
            extra_context={
                "endpoint": endpoint,
                "concurrent_users": concurrent_users,
                "duration": duration_seconds
            }
        )
        
        # Results collection
        results_queue = queue.Queue()
        stop_event = threading.Event()
        
        # Start system monitoring
        monitor_thread = threading.Thread(
            target=self._monitor_system_resources,
            args=(stop_event, results_queue)
        )
        monitor_thread.start()
        
        # Worker function for making requests
        def worker():
            """Worker thread that makes continuous requests"""
            while not stop_event.is_set():
                try:
                    request_start = time.time()
                    
                    # Make the API request
                    if method.upper() == "GET":
                        response = self.api_client.get(endpoint, headers=headers)
                    elif method.upper() == "POST":
                        response = self.api_client.post(endpoint, json_data=request_data, headers=headers)
                    elif method.upper() == "PUT":
                        response = self.api_client.put(endpoint, json_data=request_data, headers=headers)
                    else:
                        response = self.api_client.request(method, endpoint, json=request_data, headers=headers)
                    
                    request_end = time.time()
                    response_time = request_end - request_start
                    
                    # Record result
                    result = LoadTestRequest(
                        timestamp=request_start,
                        response_time=response_time,
                        status_code=response.status_code,
                        success=200 <= response.status_code < 400,
                        request_size_bytes=len(json.dumps(request_data).encode()) if request_data else 0,
                        response_size_bytes=len(response.content)
                    )
                    
                    results_queue.put(result)
                    
                except Exception as e:
                    result = LoadTestRequest(
                        timestamp=time.time(),
                        response_time=0.0,
                        status_code=0,
                        success=False,
                        error_message=str(e)
                    )
                    results_queue.put(result)
        
        # Start worker threads
        threads = []
        for _ in range(concurrent_users):
            thread = threading.Thread(target=worker)
            thread.start()
            threads.append(thread)
        
        # Let the test run for specified duration
        time.sleep(duration_seconds)
        
        # Stop all threads
        stop_event.set()
        
        # Wait for threads to finish
        for thread in threads:
            thread.join(timeout=5)
        
        # Stop system monitoring
        monitor_thread.join(timeout=5)
        
        # Collect results
        request_results = []
        system_stats = []
        
        while not results_queue.empty():
            item = results_queue.get()
            if isinstance(item, LoadTestRequest):
                request_results.append(item)
            else:
                system_stats.append(item)
        
        # Calculate metrics
        end_time = datetime.now()
        metrics = self._calculate_performance_metrics(
            test_name, start_time, end_time, request_results, 
            concurrent_users, system_stats
        )
        
        self.results_history.append(metrics)
        
        enhanced_logger.info(
            f"✅ Load test completed: {test_name}",
            extra_context={
                "total_requests": metrics.total_requests,
                "success_rate": f"{(100 - metrics.error_rate):.1f}%",
                "avg_response_time": f"{metrics.avg_response_time:.3f}s",
                "requests_per_second": f"{metrics.requests_per_second:.1f}"
            }
        )
        
        return metrics
    
    def run_stress_test(self,
                       endpoint: str,
                       method: str = "GET",
                       max_users: int = 100,
                       ramp_up_seconds: int = 60,
                       hold_duration_seconds: int = 120,
                       request_data: Dict[str, Any] = None,
                       test_name: str = None) -> PerformanceMetrics:
        """
        💪 STRESS TESTING: Find the breaking point of your API
        
        Args:
            endpoint: API endpoint to test
            method: HTTP method
            max_users: Maximum concurrent users to reach
            ramp_up_seconds: Time to gradually increase load
            hold_duration_seconds: Time to hold at max load
            request_data: Request payload
            test_name: Name for this test
            
        Returns:
            PerformanceMetrics: Performance results under stress
            
        Real Example - Banking API Stress Test:
            # Find when the payment API starts failing
            metrics = benchmark.run_stress_test(
                endpoint="/payments/process",
                method="POST",
                max_users=200,
                ramp_up_seconds=300,  # 5 minute ramp-up
                hold_duration_seconds=600,  # 10 minute hold
                request_data={"amount": 100.00, "currency": "USD"},
                test_name="Payment_API_Stress_Test"
            )
        """
        test_name = test_name or f"StressTest_{endpoint}_{max_users}users"
        start_time = datetime.now()
        
        enhanced_logger.info(
            f"💪 Starting stress test: {test_name}",
            extra_context={
                "endpoint": endpoint,
                "max_users": max_users,
                "ramp_up_time": ramp_up_seconds,
                "hold_time": hold_duration_seconds
            }
        )
        
        results_queue = queue.Queue()
        stop_event = threading.Event()
        active_threads = []
        
        # Start system monitoring
        monitor_thread = threading.Thread(
            target=self._monitor_system_resources,
            args=(stop_event, results_queue)
        )
        monitor_thread.start()
        
        # Gradual ramp-up of users
        ramp_up_interval = ramp_up_seconds / max_users
        
        def worker():
            """Worker thread for making requests during stress test"""
            while not stop_event.is_set():
                try:
                    request_start = time.time()
                    
                    if method.upper() == "GET":
                        response = self.api_client.get(endpoint)
                    elif method.upper() == "POST":
                        response = self.api_client.post(endpoint, json_data=request_data)
                    else:
                        response = self.api_client.request(method, endpoint, json=request_data)
                    
                    response_time = time.time() - request_start
                    
                    result = LoadTestRequest(
                        timestamp=request_start,
                        response_time=response_time,
                        status_code=response.status_code,
                        success=200 <= response.status_code < 400,
                        response_size_bytes=len(response.content)
                    )
                    
                    results_queue.put(result)
                    
                    # Brief pause to prevent overwhelming
                    time.sleep(0.1)
                    
                except Exception as e:
                    result = LoadTestRequest(
                        timestamp=time.time(),
                        response_time=0.0,
                        status_code=0,
                        success=False,
                        error_message=str(e)
                    )
                    results_queue.put(result)
        
        # Ramp up users gradually
        for user_num in range(max_users):
            thread = threading.Thread(target=worker)
            thread.start()
            active_threads.append(thread)
            
            enhanced_logger.info(f"📈 Ramping up: {user_num + 1}/{max_users} users active")
            time.sleep(ramp_up_interval)
        
        # Hold at maximum load
        enhanced_logger.info(f"💪 Holding at maximum load: {max_users} users for {hold_duration_seconds}s")
        time.sleep(hold_duration_seconds)
        
        # Stop test
        stop_event.set()
        
        # Wait for threads to finish
        for thread in active_threads:
            thread.join(timeout=5)
        
        monitor_thread.join(timeout=5)
        
        # Collect and analyze results
        request_results = []
        system_stats = []
        
        while not results_queue.empty():
            item = results_queue.get()
            if isinstance(item, LoadTestRequest):
                request_results.append(item)
            else:
                system_stats.append(item)
        
        end_time = datetime.now()
        metrics = self._calculate_performance_metrics(
            test_name, start_time, end_time, request_results,
            max_users, system_stats
        )
        
        self.results_history.append(metrics)
        
        # Log stress test results
        enhanced_logger.info(
            f"💪 Stress test completed: {test_name}",
            extra_context={
                "breaking_point_analysis": {
                    "max_concurrent_users": max_users,
                    "error_rate": f"{metrics.error_rate:.1f}%",
                    "avg_response_time": f"{metrics.avg_response_time:.3f}s",
                    "system_survived": metrics.error_rate < 50.0
                }
            }
        )
        
        return metrics
    
    def run_spike_test(self,
                      endpoint: str,
                      normal_users: int = 10,
                      spike_users: int = 100,
                      spike_duration_seconds: int = 30,
                      total_duration_seconds: int = 300,
                      test_name: str = None) -> PerformanceMetrics:
        """
        ⚡ SPIKE TESTING: Test sudden traffic spikes
        
        Args:
            endpoint: API endpoint to test
            normal_users: Normal baseline load
            spike_users: Peak spike load
            spike_duration_seconds: How long the spike lasts
            total_duration_seconds: Total test duration
            test_name: Name for this test
            
        Returns:
            PerformanceMetrics: Performance during traffic spike
            
        Real Example - News Website Breaking News:
            # Simulate viral news article traffic spike
            metrics = benchmark.run_spike_test(
                endpoint="/articles/breaking-news",
                normal_users=20,
                spike_users=500,
                spike_duration_seconds=60,
                total_duration_seconds=600,
                test_name="Breaking_News_Traffic_Spike"
            )
        """
        test_name = test_name or f"SpikeTest_{endpoint}_{spike_users}users"
        start_time = datetime.now()
        
        enhanced_logger.info(
            f"⚡ Starting spike test: {test_name}",
            extra_context={
                "normal_load": normal_users,
                "spike_load": spike_users,
                "spike_duration": spike_duration_seconds
            }
        )
        
        results_queue = queue.Queue()
        stop_event = threading.Event()
        
        # Start system monitoring
        monitor_thread = threading.Thread(
            target=self._monitor_system_resources,
            args=(stop_event, results_queue)
        )
        monitor_thread.start()
        
        # Worker function
        def worker():
            while not stop_event.is_set():
                try:
                    request_start = time.time()
                    response = self.api_client.get(endpoint)
                    response_time = time.time() - request_start
                    
                    result = LoadTestRequest(
                        timestamp=request_start,
                        response_time=response_time,
                        status_code=response.status_code,
                        success=200 <= response.status_code < 400,
                        response_size_bytes=len(response.content)
                    )
                    
                    results_queue.put(result)
                    time.sleep(0.1)  # Brief pause
                    
                except Exception as e:
                    result = LoadTestRequest(
                        timestamp=time.time(),
                        response_time=0.0,
                        status_code=0,
                        success=False,
                        error_message=str(e)
                    )
                    results_queue.put(result)
        
        # Phase 1: Normal load
        normal_threads = []
        for _ in range(normal_users):
            thread = threading.Thread(target=worker)
            thread.start()
            normal_threads.append(thread)
        
        enhanced_logger.info(f"📊 Running normal load: {normal_users} users")
        
        # Wait for normal phase
        normal_phase_duration = (total_duration_seconds - spike_duration_seconds) // 2
        time.sleep(normal_phase_duration)
        
        # Phase 2: Traffic spike
        spike_threads = []
        for _ in range(spike_users - normal_users):
            thread = threading.Thread(target=worker)
            thread.start()
            spike_threads.append(thread)
        
        enhanced_logger.info(f"⚡ Traffic spike started: {spike_users} total users")
        time.sleep(spike_duration_seconds)
        
        # Phase 3: Return to normal (stop spike threads)
        for thread in spike_threads:
            thread.join(timeout=1)  # Quick cleanup
        
        enhanced_logger.info(f"📉 Spike ended, returning to normal: {normal_users} users")
        time.sleep(normal_phase_duration)
        
        # Stop all threads
        stop_event.set()
        for thread in normal_threads:
            thread.join(timeout=5)
        
        monitor_thread.join(timeout=5)
        
        # Collect results
        request_results = []
        system_stats = []
        
        while not results_queue.empty():
            item = results_queue.get()
            if isinstance(item, LoadTestRequest):
                request_results.append(item)
            else:
                system_stats.append(item)
        
        end_time = datetime.now()
        metrics = self._calculate_performance_metrics(
            test_name, start_time, end_time, request_results,
            spike_users, system_stats
        )
        
        self.results_history.append(metrics)
        
        enhanced_logger.info(
            f"⚡ Spike test completed: {test_name}",
            extra_context={
                "spike_analysis": {
                    "peak_users": spike_users,
                    "error_rate_during_spike": f"{metrics.error_rate:.1f}%",
                    "spike_handled_successfully": metrics.error_rate < 25.0
                }
            }
        )
        
        return metrics
    
    def _monitor_system_resources(self, stop_event: threading.Event, 
                                results_queue: queue.Queue):
        """🔍 Monitor system resources during testing"""
        while not stop_event.is_set():
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                network = psutil.net_io_counters()
                
                system_stats = {
                    "timestamp": time.time(),
                    "cpu_percent": cpu_percent,
                    "memory_used_mb": memory.used / 1024 / 1024,
                    "memory_percent": memory.percent,
                    "network_sent_mb": network.bytes_sent / 1024 / 1024,
                    "network_recv_mb": network.bytes_recv / 1024 / 1024
                }
                
                results_queue.put(system_stats)
                
            except Exception as e:
                enhanced_logger.error(f"❌ Error monitoring system resources: {str(e)}")
            
            time.sleep(2)  # Monitor every 2 seconds
    
    def _calculate_performance_metrics(self,
                                     test_name: str,
                                     start_time: datetime,
                                     end_time: datetime,
                                     request_results: List[LoadTestRequest],
                                     concurrent_users: int,
                                     system_stats: List[Dict[str, Any]]) -> PerformanceMetrics:
        """📊 Calculate comprehensive performance metrics"""
        
        if not request_results:
            enhanced_logger.warning("⚠️ No request results to analyze")
            return PerformanceMetrics(
                test_name=test_name,
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                duration_seconds=0,
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                requests_per_second=0,
                avg_response_time=0,
                min_response_time=0,
                max_response_time=0,
                p50_response_time=0,
                p90_response_time=0,
                p95_response_time=0,
                p99_response_time=0,
                error_rate=0,
                concurrent_users=concurrent_users,
                cpu_usage_percent=0,
                memory_usage_mb=0,
                network_sent_mb=0,
                network_received_mb=0
            )
        
        # Basic metrics
        duration = (end_time - start_time).total_seconds()
        total_requests = len(request_results)
        successful_requests = sum(1 for r in request_results if r.success)
        failed_requests = total_requests - successful_requests
        
        # Response time analysis
        response_times = [r.response_time for r in request_results if r.response_time > 0]
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            
            # Percentiles
            sorted_times = sorted(response_times)
            p50_response_time = statistics.median(sorted_times)
            p90_response_time = sorted_times[int(0.90 * len(sorted_times))] if sorted_times else 0
            p95_response_time = sorted_times[int(0.95 * len(sorted_times))] if sorted_times else 0
            p99_response_time = sorted_times[int(0.99 * len(sorted_times))] if sorted_times else 0
        else:
            avg_response_time = min_response_time = max_response_time = 0
            p50_response_time = p90_response_time = p95_response_time = p99_response_time = 0
        
        # Throughput and error rate
        requests_per_second = total_requests / duration if duration > 0 else 0
        error_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0
        
        # System resource analysis
        if system_stats:
            avg_cpu = statistics.mean([s.get('cpu_percent', 0) for s in system_stats])
            avg_memory = statistics.mean([s.get('memory_used_mb', 0) for s in system_stats])
            
            # Network usage (difference from start to end)
            if len(system_stats) >= 2:
                first_net = system_stats[0]
                last_net = system_stats[-1]
                network_sent = last_net.get('network_sent_mb', 0) - first_net.get('network_sent_mb', 0)
                network_received = last_net.get('network_recv_mb', 0) - first_net.get('network_recv_mb', 0)
            else:
                network_sent = network_received = 0
        else:
            avg_cpu = avg_memory = network_sent = network_received = 0
        
        return PerformanceMetrics(
            test_name=test_name,
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            duration_seconds=duration,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            requests_per_second=requests_per_second,
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            p50_response_time=p50_response_time,
            p90_response_time=p90_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            error_rate=error_rate,
            concurrent_users=concurrent_users,
            cpu_usage_percent=avg_cpu,
            memory_usage_mb=avg_memory,
            network_sent_mb=network_sent,
            network_received_mb=network_received
        )
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """📊 Generate comprehensive performance analysis report"""
        if not self.results_history:
            return {"message": "No performance test results available"}
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(self.results_history),
            "summary": {
                "best_performance": None,
                "worst_performance": None,
                "average_rps": 0,
                "average_response_time": 0,
                "overall_error_rate": 0
            },
            "test_results": [],
            "recommendations": []
        }
        
        # Convert metrics to dict for analysis
        test_data = [asdict(metrics) for metrics in self.results_history]
        
        # Find best and worst performing tests
        if test_data:
            best_test = min(test_data, key=lambda x: x['avg_response_time'])
            worst_test = max(test_data, key=lambda x: x['avg_response_time'])
            
            report["summary"]["best_performance"] = {
                "test_name": best_test["test_name"],
                "avg_response_time": best_test["avg_response_time"],
                "requests_per_second": best_test["requests_per_second"]
            }
            
            report["summary"]["worst_performance"] = {
                "test_name": worst_test["test_name"],
                "avg_response_time": worst_test["avg_response_time"],
                "requests_per_second": worst_test["requests_per_second"]
            }
            
            # Calculate averages
            report["summary"]["average_rps"] = statistics.mean([t["requests_per_second"] for t in test_data])
            report["summary"]["average_response_time"] = statistics.mean([t["avg_response_time"] for t in test_data])
            report["summary"]["overall_error_rate"] = statistics.mean([t["error_rate"] for t in test_data])
        
        report["test_results"] = test_data
        
        # Generate recommendations
        recommendations = []
        for metrics in self.results_history:
            if metrics.error_rate > 5.0:
                recommendations.append(f"High error rate ({metrics.error_rate:.1f}%) in {metrics.test_name}")
            
            if metrics.avg_response_time > 2.0:
                recommendations.append(f"Slow response time ({metrics.avg_response_time:.3f}s) in {metrics.test_name}")
            
            if metrics.cpu_usage_percent > 80:
                recommendations.append(f"High CPU usage ({metrics.cpu_usage_percent:.1f}%) during {metrics.test_name}")
        
        report["recommendations"] = recommendations
        
        return report
    
    def export_results_to_csv(self, filename: str = None) -> str:
        """📊 Export performance results to CSV for analysis"""
        if not self.results_history:
            enhanced_logger.warning("⚠️ No performance results to export")
            return ""
        
        filename = filename or f"performance_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Convert to DataFrame for easy CSV export
        df = pd.DataFrame([asdict(metrics) for metrics in self.results_history])
        df.to_csv(filename, index=False)
        
        enhanced_logger.info(f"📊 Performance results exported to {filename}")
        return filename


# 🌟 GLOBAL INSTANCE for easy access
def create_performance_benchmark(api_client: APIClient = None) -> PerformanceBenchmark:
    """Factory function to create performance benchmark instance"""
    return PerformanceBenchmark(api_client)


# 🎯 USAGE EXAMPLES FOR BEGINNERS:
"""
📚 HOW TO USE PERFORMANCE BENCHMARKING:

1. BASIC LOAD TEST (Perfect for beginners):
   
   from utils.performance_benchmarking import create_performance_benchmark
   from utils.api_client import jsonplaceholder_client
   
   def test_api_load_performance():
       # Create benchmark with your API client
       benchmark = create_performance_benchmark(jsonplaceholder_client)
       
       # Run load test - simulate 20 users for 30 seconds
       metrics = benchmark.run_load_test(
           endpoint="/users",
           concurrent_users=20,
           duration_seconds=30,
           test_name="User_API_Load_Test"
       )
       
       # Check performance criteria
       assert metrics.error_rate < 5.0, f"Error rate too high: {metrics.error_rate}%"
       assert metrics.avg_response_time < 1.0, f"Response too slow: {metrics.avg_response_time}s"
       assert metrics.requests_per_second > 10, f"Throughput too low: {metrics.requests_per_second} RPS"

2. E-COMMERCE STRESS TEST:
   
   def test_product_api_stress():
       benchmark = create_performance_benchmark(ecommerce_client)
       
       # Find breaking point - gradually increase to 100 users
       metrics = benchmark.run_stress_test(
           endpoint="/products/search",
           method="GET",
           max_users=100,
           ramp_up_seconds=120,  # 2 minute ramp-up
           hold_duration_seconds=300,  # 5 minute hold
           test_name="Product_Search_Stress_Test"
       )
       
       # Analyze breaking point
       if metrics.error_rate > 50:
           print(f"⚠️ API breaks at {metrics.concurrent_users} concurrent users")
       else:
           print(f"✅ API handles {metrics.concurrent_users} users successfully")

3. NEWS WEBSITE SPIKE TEST:
   
   def test_breaking_news_spike():
       benchmark = create_performance_benchmark(news_client)
       
       # Simulate viral news traffic spike
       metrics = benchmark.run_spike_test(
           endpoint="/articles/trending",
           normal_users=10,      # Normal traffic
           spike_users=200,      # Viral spike traffic
           spike_duration_seconds=60,  # 1 minute spike
           total_duration_seconds=300, # 5 minute total test
           test_name="Viral_News_Spike_Test"
       )
       
       # Check if system survived the spike
       assert metrics.error_rate < 25, f"System failed during spike: {metrics.error_rate}% errors"

4. BANKING API ENDURANCE TEST:
   
   def test_payment_api_endurance():
       benchmark = create_performance_benchmark(banking_client)
       payment_data = {"amount": 100.00, "currency": "USD", "account": "12345"}
       
       # Test stability over long period
       metrics = benchmark.run_load_test(
           endpoint="/payments/process",
           method="POST",
           concurrent_users=5,   # Light but constant load
           duration_seconds=3600,  # 1 hour
           request_data=payment_data,
           test_name="Payment_Endurance_Test"
       )
       
       # Check for memory leaks or degradation
       assert metrics.error_rate < 1.0, "Payment system should be highly reliable"
       assert metrics.p95_response_time < 2.0, "95% of payments should complete in <2s"

5. COMPREHENSIVE PERFORMANCE ANALYSIS:
   
   def test_complete_performance_suite():
       benchmark = create_performance_benchmark(api_client)
       
       # Run multiple test types
       load_metrics = benchmark.run_load_test("/api/data", concurrent_users=25, duration_seconds=60)
       stress_metrics = benchmark.run_stress_test("/api/data", max_users=100, ramp_up_seconds=60)
       spike_metrics = benchmark.run_spike_test("/api/data", normal_users=10, spike_users=80)
       
       # Generate comprehensive report
       report = benchmark.generate_performance_report()
       
       print(f"📊 Performance Summary:")
       print(f"   Best Performance: {report['summary']['best_performance']['test_name']}")
       print(f"   Average RPS: {report['summary']['average_rps']:.1f}")
       print(f"   Average Response Time: {report['summary']['average_response_time']:.3f}s")
       
       # Export detailed results
       csv_file = benchmark.export_results_to_csv()
       print(f"📋 Detailed results exported to: {csv_file}")

6. REAL-TIME MONITORING EXAMPLE:
   
   def test_with_performance_monitoring():
       benchmark = create_performance_benchmark(api_client)
       
       # Custom validation during test
       def performance_callback(metrics):
           if metrics.error_rate > 10:
               print(f"⚠️ High error rate detected: {metrics.error_rate}%")
           if metrics.avg_response_time > 5:
               print(f"⚠️ Slow response time: {metrics.avg_response_time}s")
       
       metrics = benchmark.run_load_test(
           endpoint="/api/critical-service",
           concurrent_users=50,
           duration_seconds=120,
           test_name="Critical_Service_Monitoring"
       )
       
       # Real-time alerts based on results
       performance_callback(metrics)

🎯 REAL-WORLD SCENARIOS:

✅ E-COMMERCE BLACK FRIDAY:
   - Normal load: 100 users
   - Peak load: 10,000 users
   - Spike duration: 2 hours

✅ SOCIAL MEDIA VIRAL POST:
   - Normal load: 50 users  
   - Spike load: 5,000 users
   - Spike duration: 30 minutes

✅ BANKING END-OF-MONTH:
   - Normal load: 20 users
   - Peak load: 500 users
   - Duration: 8 hours

✅ NEWS BREAKING STORY:
   - Normal load: 25 users
   - Spike load: 2,000 users
   - Spike duration: 1 hour

✅ GAMING NEW RELEASE:
   - Normal load: 100 users
   - Launch spike: 50,000 users
   - Duration: 4 hours

📊 PERFORMANCE BENCHMARKS (Industry Standards):

🌟 EXCELLENT:
   - Response Time: < 200ms
   - Error Rate: < 0.1%
   - Throughput: > 1000 RPS

✅ GOOD:
   - Response Time: < 1s
   - Error Rate: < 1%
   - Throughput: > 100 RPS

⚠️ ACCEPTABLE:
   - Response Time: < 3s
   - Error Rate: < 5%
   - Throughput: > 10 RPS

❌ POOR:
   - Response Time: > 5s
   - Error Rate: > 10%
   - Throughput: < 10 RPS

🎯 BENEFITS:
✅ PREVENT OUTAGES: Find issues before production
✅ CAPACITY PLANNING: Know your limits
✅ SLA COMPLIANCE: Meet performance requirements  
✅ COST OPTIMIZATION: Right-size infrastructure
✅ USER EXPERIENCE: Ensure fast, reliable service
✅ COMPETITIVE ADVANTAGE: Outperform competitors
""" 