"""
Advanced API client with retry, logging, and validation capabilities
"""
import json
import time
from typing import Dict, Any, Optional, Union, List
from urllib.parse import urljoin
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from loguru import logger

from config.config import config_instance
from utils.logger import api_logger


class APIClient:
    """
    Advanced API client with comprehensive features
    """
    
    def __init__(self, base_url: str = None, headers: Dict[str, str] = None):
        self.base_url = base_url or config_instance.base_url
        self.default_headers = headers or config_instance.headers
        self.session = self._create_session()
        self.last_response = None
        self.response_time = 0
        
    def _create_session(self) -> requests.Session:
        """Create requests session with retry strategy and adapters"""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=config_instance.retry_count,
            backoff_factor=config_instance.retry_delay,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default timeout and headers
        session.headers.update(self.default_headers)
        
        return session
    
    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint"""
        if endpoint.startswith(('http://', 'https://')):
            return endpoint
        return urljoin(self.base_url.rstrip('/') + '/', endpoint.lstrip('/'))
    
    def _log_request(self, method: str, url: str, headers: Dict = None, data: Any = None):
        """Log request details"""
        log_headers = dict(self.session.headers)
        if headers:
            log_headers.update(headers)
            
        api_logger.info(f"🔄 {method.upper()} {url}")
        api_logger.debug(f"Headers: {log_headers}")
        if data:
            api_logger.debug(f"Request Body: {json.dumps(data, indent=2) if isinstance(data, dict) else data}")
    
    def _log_response(self, response: requests.Response, response_time: float):
        """Log response details"""
        api_logger.info(f"📋 Response: {response.status_code} ({response_time:.3f}s)")
        
        try:
            response_json = response.json()
            api_logger.debug(f"Response Body: {json.dumps(response_json, indent=2)}")
        except (json.JSONDecodeError, ValueError):
            if response.text:
                api_logger.debug(f"Response Body: {response.text[:500]}{'...' if len(response.text) > 500 else ''}")
    
    def request(self, method: str, endpoint: str, headers: Dict[str, str] = None, 
                params: Dict[str, Any] = None, json_data: Dict[str, Any] = None,
                data: Any = None, timeout: int = None, **kwargs) -> requests.Response:
        """
        Make HTTP request with comprehensive logging and error handling
        """
        url = self._build_url(endpoint)
        request_headers = dict(self.session.headers)
        if headers:
            request_headers.update(headers)
        
        # Log request
        self._log_request(method, url, request_headers, json_data or data)
        
        # Make request with timing
        start_time = time.time()
        try:
            response = self.session.request(
                method=method.upper(),
                url=url,
                headers=headers,
                params=params,
                json=json_data,
                data=data,
                timeout=timeout or config_instance.timeout,
                **kwargs
            )
            
            self.response_time = time.time() - start_time
            self.last_response = response
            
            # Log response
            self._log_response(response, self.response_time)
            
            return response
            
        except requests.exceptions.RequestException as e:
            self.response_time = time.time() - start_time
            api_logger.error(f"❌ Request failed: {str(e)}")
            raise
    
    def get(self, endpoint: str, params: Dict[str, Any] = None, 
            headers: Dict[str, str] = None, **kwargs) -> requests.Response:
        """Make GET request"""
        return self.request('GET', endpoint, headers=headers, params=params, **kwargs)
    
    def post(self, endpoint: str, json_data: Dict[str, Any] = None, 
             data: Any = None, headers: Dict[str, str] = None, **kwargs) -> requests.Response:
        """Make POST request"""
        return self.request('POST', endpoint, headers=headers, json_data=json_data, data=data, **kwargs)
    
    def put(self, endpoint: str, json_data: Dict[str, Any] = None, 
            data: Any = None, headers: Dict[str, str] = None, **kwargs) -> requests.Response:
        """Make PUT request"""
        return self.request('PUT', endpoint, headers=headers, json_data=json_data, data=data, **kwargs)
    
    def patch(self, endpoint: str, json_data: Dict[str, Any] = None, 
              data: Any = None, headers: Dict[str, str] = None, **kwargs) -> requests.Response:
        """Make PATCH request"""
        return self.request('PATCH', endpoint, headers=headers, json_data=json_data, data=data, **kwargs)
    
    def delete(self, endpoint: str, headers: Dict[str, str] = None, **kwargs) -> requests.Response:
        """Make DELETE request"""
        return self.request('DELETE', endpoint, headers=headers, **kwargs)
    
    def head(self, endpoint: str, headers: Dict[str, str] = None, **kwargs) -> requests.Response:
        """Make HEAD request"""
        return self.request('HEAD', endpoint, headers=headers, **kwargs)
    
    def options(self, endpoint: str, headers: Dict[str, str] = None, **kwargs) -> requests.Response:
        """Make OPTIONS request"""
        return self.request('OPTIONS', endpoint, headers=headers, **kwargs)
    
    def set_auth_token(self, token: str, auth_type: str = 'Bearer'):
        """Set authentication token"""
        self.session.headers['Authorization'] = f'{auth_type} {token}'
        api_logger.info(f"🔐 Set {auth_type} authentication token")
    
    def set_basic_auth(self, username: str, password: str):
        """Set basic authentication"""
        self.session.auth = (username, password)
        api_logger.info("🔐 Set Basic authentication")
    
    def add_header(self, key: str, value: str):
        """Add header to session"""
        self.session.headers[key] = value
        api_logger.debug(f"Added header: {key} = {value}")
    
    def remove_header(self, key: str):
        """Remove header from session"""
        if key in self.session.headers:
            del self.session.headers[key]
            api_logger.debug(f"Removed header: {key}")
    
    def get_response_json(self) -> Dict[str, Any]:
        """Get last response as JSON"""
        if self.last_response:
            try:
                return self.last_response.json()
            except json.JSONDecodeError:
                api_logger.warning("Response is not valid JSON")
                return {}
        return {}
    
    def get_response_text(self) -> str:
        """Get last response as text"""
        return self.last_response.text if self.last_response else ""
    
    def get_response_headers(self) -> Dict[str, str]:
        """Get last response headers"""
        return dict(self.last_response.headers) if self.last_response else {}
    
    def get_status_code(self) -> int:
        """Get last response status code"""
        return self.last_response.status_code if self.last_response else 0
    
    def close(self):
        """Close the session"""
        self.session.close()
        api_logger.info("🔒 API client session closed")


# Global API client instances
default_client = APIClient()
jsonplaceholder_client = APIClient("https://jsonplaceholder.typicode.com")
reqres_client = APIClient("https://reqres.in/api")
httpbin_client = APIClient("https://httpbin.org") 