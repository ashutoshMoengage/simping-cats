"""
Decorators for API testing framework
"""
import time
import functools
from typing import Callable, Any, Dict, List
from loguru import logger
import allure
from retry import retry as retry_decorator


def log_test_execution(func: Callable) -> Callable:
    """Decorator to log test execution start and end"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        test_name = func.__name__
        logger.info(f"🚀 Starting test: {test_name}")
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"✅ Test passed: {test_name} ({execution_time:.3f}s)")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ Test failed: {test_name} ({execution_time:.3f}s) - {str(e)}")
            raise
    
    return wrapper


def measure_response_time(max_time: float = None):
    """Decorator to measure and optionally assert response time"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            response_time = time.time() - start_time
            
            logger.info(f"📊 Response time: {response_time:.3f}s")
            
            if max_time and response_time > max_time:
                logger.error(f"❌ Response time {response_time:.3f}s exceeded limit {max_time}s")
                raise AssertionError(f"Response time {response_time:.3f}s exceeded limit {max_time}s")
            
            # Attach response time to result if it's a response object
            if hasattr(result, '__dict__'):
                result.measured_response_time = response_time
            
            return result
        
        return wrapper
    return decorator


def retry_on_failure(max_retries: int = 3, delay: int = 1, backoff: int = 2):
    """Decorator to retry test on failure"""
    def decorator(func: Callable) -> Callable:
        @retry_decorator(tries=max_retries, delay=delay, backoff=backoff, logger=logger)
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def allure_test_case(title: str = None, description: str = None, 
                    severity: str = "normal", tags: List[str] = None):
    """Decorator to add Allure test case information"""
    def decorator(func: Callable) -> Callable:
        @allure.title(title or func.__name__)
        @allure.description(description or func.__doc__ or "")
        @allure.severity(getattr(allure.severity_level, severity.upper(), allure.severity_level.NORMAL))
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Add tags if provided
            if tags:
                for tag in tags:
                    allure.dynamic.tag(tag)
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def api_test(title: str = None, description: str = None, severity: str = "normal", 
            tags: List[str] = None, max_response_time: float = None,
            retry_count: int = 0):
    """Combined decorator for API tests with logging, Allure, and optional features"""
    def decorator(func: Callable) -> Callable:
        # Apply decorators in order
        decorated_func = func
        
        # Add retry if specified
        if retry_count > 0:
            decorated_func = retry_on_failure(max_retries=retry_count)(decorated_func)
        
        # Add response time measurement if specified
        if max_response_time:
            decorated_func = measure_response_time(max_response_time)(decorated_func)
        
        # Add Allure reporting
        decorated_func = allure_test_case(title, description, severity, tags)(decorated_func)
        
        # Add logging
        decorated_func = log_test_execution(decorated_func)
        
        return decorated_func
    
    return decorator


def data_provider(data_source: Any):
    """Decorator to provide test data"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Add data source to kwargs
            kwargs['test_data'] = data_source
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def skip_if_condition(condition: bool, reason: str = "Condition not met"):
    """Decorator to skip test based on condition"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if condition:
                logger.warning(f"⏭️ Skipping test {func.__name__}: {reason}")
                import pytest
                pytest.skip(reason)
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def attach_request_response(func: Callable) -> Callable:
    """Decorator to attach request/response to Allure report"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        
        # Try to find API client or response in args/kwargs
        for arg in args:
            if hasattr(arg, 'last_response') and arg.last_response:
                response = arg.last_response
                
                # Attach request
                allure.attach(
                    f"URL: {response.request.url}\n"
                    f"Method: {response.request.method}\n"
                    f"Headers: {dict(response.request.headers)}\n"
                    f"Body: {response.request.body or 'None'}",
                    name="Request Details",
                    attachment_type=allure.attachment_type.TEXT
                )
                
                # Attach response
                allure.attach(
                    f"Status Code: {response.status_code}\n"
                    f"Headers: {dict(response.headers)}\n"
                    f"Body: {response.text[:1000]}{'...' if len(response.text) > 1000 else ''}",
                    name="Response Details",
                    attachment_type=allure.attachment_type.TEXT
                )
                break
        
        return result
    
    return wrapper


def performance_test(max_response_time: float, percentile: int = 95):
    """Decorator for performance testing"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            response_times = []
            
            # Run test multiple times to gather performance data
            for i in range(10):  # Run 10 times for statistical significance
                start_time = time.time()
                result = func(*args, **kwargs)
                response_time = time.time() - start_time
                response_times.append(response_time)
            
            # Calculate percentile
            response_times.sort()
            percentile_index = int(len(response_times) * percentile / 100)
            percentile_time = response_times[percentile_index]
            
            logger.info(f"📊 Performance test results:")
            logger.info(f"   Average: {sum(response_times)/len(response_times):.3f}s")
            logger.info(f"   {percentile}th percentile: {percentile_time:.3f}s")
            logger.info(f"   Max: {max(response_times):.3f}s")
            logger.info(f"   Min: {min(response_times):.3f}s")
            
            if percentile_time > max_response_time:
                raise AssertionError(
                    f"Performance test failed: {percentile}th percentile "
                    f"({percentile_time:.3f}s) exceeded limit ({max_response_time}s)"
                )
            
            return result
        
        return wrapper
    return decorator 