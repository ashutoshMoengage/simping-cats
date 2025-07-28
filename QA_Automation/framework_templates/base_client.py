"""
Abstract Base API Client Template
==================================

This template demonstrates proper OOP principles with inheritance, polymorphism,
and encapsulation. Use this as a base for creating custom API clients.

🎯 For Beginners:
- Inheritance: BaseAPIClient -> CustomAPIClient (reuse common functionality)
- Polymorphism: Different clients can implement same methods differently
- Encapsulation: Private methods (_method) vs public methods (method)
- Abstraction: Abstract methods must be implemented by child classes
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import requests
from urllib.parse import urljoin
import time

from utils.logger import api_logger


class BaseAPIClient(ABC):
    """
    🏗️ Abstract Base Class for API Clients
    
    This is a TEMPLATE that demonstrates proper OOP concepts:
    
    ✅ INHERITANCE: Child classes inherit common functionality
    ✅ POLYMORPHISM: Child classes can override methods with specific behavior
    ✅ ENCAPSULATION: Private (_method) and public methods properly separated
    ✅ ABSTRACTION: Abstract methods force implementation in child classes
    
    📚 BEGINNER GUIDE:
    1. Create your API client by inheriting from this class
    2. Implement the abstract methods (marked with @abstractmethod)
    3. Override any methods you want to customize
    4. Add your own specific methods
    """
    
    def __init__(self, base_url: str, headers: Dict[str, str] = None):
        """
        🚀 Initialize the API client
        
        Args:
            base_url (str): The base URL for your API (e.g., 'https://api.example.com')
            headers (dict): Default headers to include with all requests
            
        Example:
            client = MyAPIClient('https://api.example.com', {'Authorization': 'Bearer token'})
        """
        self.base_url = base_url.rstrip('/')
        self.default_headers = headers or {}
        self.session = self._create_session()
        self.last_response = None
        self.response_time = 0
        
        # 📝 Log initialization for debugging
        api_logger.info(f"🔧 Initialized {self.__class__.__name__} with base_url: {self.base_url}")
    
    def _create_session(self) -> requests.Session:
        """
        🔒 PRIVATE METHOD: Create and configure HTTP session
        
        This is a PRIVATE method (starts with _) that handles internal session setup.
        Child classes can override this to customize session configuration.
        
        Returns:
            requests.Session: Configured session object
        """
        session = requests.Session()
        session.headers.update(self.default_headers)
        
        # Add retry strategy - this is common for all API clients
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _build_url(self, endpoint: str) -> str:
        """
        🔒 PRIVATE METHOD: Build complete URL from endpoint
        
        Args:
            endpoint (str): API endpoint (e.g., '/users/123')
            
        Returns:
            str: Complete URL (e.g., 'https://api.example.com/users/123')
        """
        if endpoint.startswith(('http://', 'https://')):
            return endpoint
        return urljoin(self.base_url + '/', endpoint.lstrip('/'))
    
    def _log_request(self, method: str, url: str, **kwargs):
        """🔒 PRIVATE METHOD: Log request details for debugging"""
        api_logger.info(f"📤 {method.upper()} {url}")
        if kwargs.get('json'):
            api_logger.debug(f"📋 Request Body: {kwargs['json']}")
    
    def _log_response(self, response: requests.Response, response_time: float):
        """🔒 PRIVATE METHOD: Log response details for debugging"""
        api_logger.info(f"📥 Response: {response.status_code} ({response_time:.3f}s)")
        
        try:
            if hasattr(response, 'json') and response.text:
                response_data = response.json()
                api_logger.debug(f"📋 Response Body: {response_data}")
        except:
            api_logger.debug(f"📋 Response Text: {response.text[:200]}...")
    
    # 🌟 ABSTRACT METHODS - Must be implemented by child classes
    @abstractmethod
    def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """
        🔐 ABSTRACT METHOD: Handle authentication for this API
        
        This method MUST be implemented by each child class because different
        APIs have different authentication methods (API key, OAuth, JWT, etc.)
        
        Args:
            credentials (dict): Authentication credentials
            
        Returns:
            bool: True if authentication successful, False otherwise
            
        Example Implementation:
            def authenticate(self, credentials):
                api_key = credentials.get('api_key')
                self.session.headers['X-API-Key'] = api_key
                return self._test_authentication()
        """
        pass
    
    @abstractmethod
    def get_health_check_endpoint(self) -> str:
        """
        ❤️ ABSTRACT METHOD: Return the health check endpoint for this API
        
        Different APIs have different health check endpoints:
        - '/health'
        - '/status'  
        - '/ping'
        - '/v1/health'
        
        Returns:
            str: Health check endpoint path
            
        Example Implementation:
            def get_health_check_endpoint(self):
                return '/api/v1/health'
        """
        pass
    
    # 🌟 COMMON METHODS - Available to all child classes
    def request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        🌐 Make HTTP request with logging and error handling
        
        This is a PUBLIC method that all child classes can use.
        It provides common functionality like logging, timing, and error handling.
        
        Args:
            method (str): HTTP method ('GET', 'POST', etc.)
            endpoint (str): API endpoint
            **kwargs: Additional arguments for requests
            
        Returns:
            requests.Response: HTTP response
            
        Example:
            response = client.request('GET', '/users/123')
            response = client.request('POST', '/users', json={'name': 'John'})
        """
        url = self._build_url(endpoint)
        
        # 📝 Log the request
        self._log_request(method, url, **kwargs)
        
        # ⏱️ Time the request
        start_time = time.time()
        
        try:
            response = self.session.request(method, url, **kwargs)
            self.response_time = time.time() - start_time
            self.last_response = response
            
            # 📝 Log the response
            self._log_response(response, self.response_time)
            
            return response
            
        except requests.exceptions.RequestException as e:
            self.response_time = time.time() - start_time
            api_logger.error(f"❌ Request failed: {str(e)}")
            raise
    
    def get(self, endpoint: str, **kwargs) -> requests.Response:
        """🌐 Make GET request"""
        return self.request('GET', endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> requests.Response:
        """🌐 Make POST request"""
        return self.request('POST', endpoint, **kwargs)
    
    def put(self, endpoint: str, **kwargs) -> requests.Response:
        """🌐 Make PUT request"""
        return self.request('PUT', endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """🌐 Make DELETE request"""
        return self.request('DELETE', endpoint, **kwargs)
    
    def health_check(self) -> bool:
        """
        ❤️ Check API health status
        
        This method uses the abstract method get_health_check_endpoint()
        This demonstrates how abstract and concrete methods work together.
        
        Returns:
            bool: True if API is healthy, False otherwise
        """
        try:
            endpoint = self.get_health_check_endpoint()  # Calls abstract method
            response = self.get(endpoint)
            is_healthy = response.status_code == 200
            
            api_logger.info(f"❤️ Health check: {'✅ Healthy' if is_healthy else '❌ Unhealthy'}")
            return is_healthy
            
        except Exception as e:
            api_logger.error(f"❌ Health check failed: {str(e)}")
            return False
    
    def close(self):
        """🔒 Close the session and cleanup resources"""
        if self.session:
            self.session.close()
            api_logger.info(f"🔒 {self.__class__.__name__} session closed")


# 🎯 EXAMPLE: How to create a custom API client using inheritance
class ExampleAPIClient(BaseAPIClient):
    """
    📚 EXAMPLE IMPLEMENTATION: Custom API Client
    
    This shows how to create your own API client by inheriting from BaseAPIClient.
    This demonstrates INHERITANCE and POLYMORPHISM in action.
    """
    
    def __init__(self, api_key: str):
        """
        🚀 Initialize with API-specific configuration
        
        Args:
            api_key (str): Your API key for authentication
        """
        # Set up headers specific to this API
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': api_key,
            'User-Agent': 'MyApp/1.0'
        }
        
        # Call parent constructor (INHERITANCE)
        super().__init__('https://api.example.com', headers)
        
        self.api_key = api_key
    
    # 🌟 IMPLEMENT ABSTRACT METHODS (required)
    def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """
        🔐 POLYMORPHISM: Custom authentication implementation
        
        This is our specific implementation of the abstract method.
        Each API client can have different authentication logic.
        """
        # For this example API, we just verify the API key is set
        if self.api_key:
            api_logger.info("🔐 Authentication successful")
            return True
        else:
            api_logger.error("❌ No API key provided")
            return False
    
    def get_health_check_endpoint(self) -> str:
        """❤️ Return health check endpoint for this specific API"""
        return '/api/v1/status'
    
    # 🌟 ADD CUSTOM METHODS (specific to this API)
    def get_users(self, page: int = 1, limit: int = 10) -> requests.Response:
        """
        👥 Get users with pagination
        
        This is a CUSTOM method specific to this API.
        It uses the inherited request() method.
        """
        params = {'page': page, 'limit': limit}
        return self.get('/users', params=params)
    
    def create_user(self, user_data: Dict[str, Any]) -> requests.Response:
        """👤 Create a new user"""
        return self.post('/users', json=user_data)
    
    def get_user_by_id(self, user_id: int) -> requests.Response:
        """👤 Get specific user by ID"""
        return self.get(f'/users/{user_id}')


# 🎯 USAGE EXAMPLES FOR BEGINNERS:
"""
📚 HOW TO USE THIS TEMPLATE:

1. CREATE YOUR OWN API CLIENT:
   
   class MyAPIClient(BaseAPIClient):
       def authenticate(self, credentials):
           # Your authentication logic here
           return True
           
       def get_health_check_endpoint(self):
           return '/health'  # Your API's health endpoint
   
2. USE YOUR CLIENT:
   
   client = MyAPIClient('https://your-api.com')
   response = client.get('/users')
   
3. ADD CUSTOM METHODS:
   
   def get_products(self):
       return self.get('/products')
       
   def create_order(self, order_data):
       return self.post('/orders', json=order_data)

🎯 BENEFITS OF THIS APPROACH:
✅ REUSABILITY: Common functionality is shared
✅ CONSISTENCY: All API clients work the same way
✅ MAINTAINABILITY: Bug fixes in base class benefit all clients
✅ EXTENSIBILITY: Easy to add new API clients
✅ TESTABILITY: Base functionality can be tested once
""" 