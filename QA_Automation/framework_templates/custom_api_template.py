"""
🎯 CUSTOM API CLIENT TEMPLATE
==============================

STEP-BY-STEP GUIDE for creating your own API client using our framework.

📚 FOR BEGINNERS:
This template shows you EXACTLY how to create an API client for any service.
Just follow the steps and customize for your specific API.

🚀 QUICK START:
1. Copy this template
2. Replace 'YourAPI' with your API name
3. Update the URLs and authentication method
4. Add your specific API methods
5. Run tests to verify everything works!
"""

from framework_templates.base_client import BaseAPIClient
from typing import Dict, Any, Optional, List
from utils.assertions import api_assert
import json


class YourAPIClient(BaseAPIClient):
    """
    🌟 YOUR CUSTOM API CLIENT
    
    📝 INSTRUCTIONS:
    1. Replace 'YourAPI' with your actual API name (e.g., 'GitHubAPIClient')
    2. Update the base_url to your API's URL
    3. Modify authentication method for your API
    4. Add methods specific to your API endpoints
    
    💡 EXAMPLE APIS YOU CAN INTEGRATE:
    - GitHub API: https://api.github.com
    - Stripe API: https://api.stripe.com
    - Slack API: https://slack.com/api
    - Twitter API: https://api.twitter.com
    - Your Company's Internal API
    """
    
    def __init__(self, api_key: str = None, base_url: str = None):
        """
        🚀 Initialize your API client
        
        Args:
            api_key (str): Your API key (if your API uses API keys)
            base_url (str): Override default base URL if needed
            
        📝 CUSTOMIZE THIS:
        - Change authentication method if your API uses OAuth, JWT, etc.
        - Update default headers for your API's requirements
        - Add any initialization logic specific to your API
        """
        
        # 🔧 STEP 1: Set your API's base URL
        self.base_url = base_url or "https://api.yourservice.com"  # 👈 CHANGE THIS
        
        # 🔧 STEP 2: Set up headers for your API
        default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "YourApp-API-Client/1.0",  # 👈 CHANGE THIS
        }
        
        # 🔧 STEP 3: Add authentication header if using API key
        if api_key:
            # 👈 CHANGE THIS based on your API's auth method:
            # Option A: API Key in header
            default_headers["X-API-Key"] = api_key
            # Option B: Bearer token
            # default_headers["Authorization"] = f"Bearer {api_key}"
            # Option C: Basic auth
            # default_headers["Authorization"] = f"Basic {api_key}"
        
        # Call parent constructor
        super().__init__(self.base_url, default_headers)
        
        self.api_key = api_key
        
        # 📝 Log successful initialization
        print(f"✅ {self.__class__.__name__} initialized successfully!")
    
    # 🌟 REQUIRED: Implement abstract methods from BaseAPIClient
    
    def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """
        🔐 STEP 4: Implement authentication for your API
        
        📝 CUSTOMIZE THIS based on your API's authentication:
        
        Args:
            credentials (dict): Authentication data
            
        Returns:
            bool: True if authentication successful
            
        💡 COMMON AUTHENTICATION PATTERNS:
        
        # API Key authentication:
        def authenticate(self, credentials):
            api_key = credentials.get('api_key')
            if api_key:
                self.session.headers['X-API-Key'] = api_key
                return self._test_auth_endpoint()
            return False
        
        # OAuth 2.0:
        def authenticate(self, credentials):
            token = credentials.get('access_token')
            if token:
                self.session.headers['Authorization'] = f'Bearer {token}'
                return self._test_auth_endpoint()
            return False
        
        # Basic Authentication:
        def authenticate(self, credentials):
            username = credentials.get('username')
            password = credentials.get('password')
            if username and password:
                self.session.auth = (username, password)
                return self._test_auth_endpoint()
            return False
        """
        
        # 👈 IMPLEMENT YOUR AUTHENTICATION LOGIC HERE
        try:
            # Example for API key authentication
            if self.api_key:
                # Test authentication by making a simple API call
                response = self.get("/user")  # 👈 CHANGE to your API's user/profile endpoint
                return response.status_code == 200
            return False
            
        except Exception as e:
            print(f"❌ Authentication failed: {str(e)}")
            return False
    
    def get_health_check_endpoint(self) -> str:
        """
        ❤️ STEP 5: Set your API's health check endpoint
        
        Returns:
            str: Health check endpoint path
            
        💡 COMMON HEALTH CHECK ENDPOINTS:
        - "/health"
        - "/status" 
        - "/ping"
        - "/api/v1/health"
        - "/heartbeat"
        """
        # 👈 CHANGE THIS to your API's health check endpoint
        return "/health"  # or "/status", "/ping", etc.
    
    # 🌟 STEP 6: Add methods for your specific API endpoints
    
    def get_user_profile(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        👤 Get user profile information
        
        Args:
            user_id (str, optional): Specific user ID, or current user if None
            
        Returns:
            dict: User profile data
            
        📝 EXAMPLE: Customize this for your API
        """
        endpoint = f"/users/{user_id}" if user_id else "/user"
        response = self.get(endpoint)
        
        # ✅ Use our framework's assertions for validation
        api_assert.assert_status_code(response, 200)
        api_assert.assert_content_type(response, "application/json")
        
        return response.json()
    
    def list_items(self, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """
        📋 List items with pagination
        
        Args:
            page (int): Page number (starts from 1)
            per_page (int): Items per page
            
        Returns:
            dict: List of items with pagination info
            
        📝 CUSTOMIZE: Replace 'items' with your actual resource (users, orders, products, etc.)
        """
        params = {"page": page, "per_page": per_page}
        response = self.get("/items", params=params)  # 👈 CHANGE '/items' to your endpoint
        
        api_assert.assert_status_code(response, 200)
        return response.json()
    
    def create_item(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        ➕ Create a new item
        
        Args:
            item_data (dict): Data for the new item
            
        Returns:
            dict: Created item data
            
        📝 CUSTOMIZE: Replace 'item' with your actual resource
        """
        response = self.post("/items", json=item_data)  # 👈 CHANGE endpoint
        
        api_assert.assert_status_code(response, 201)  # 201 = Created
        return response.json()
    
    def update_item(self, item_id: str, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        ✏️ Update an existing item
        
        Args:
            item_id (str): ID of item to update
            item_data (dict): Updated data
            
        Returns:
            dict: Updated item data
        """
        response = self.put(f"/items/{item_id}", json=item_data)  # 👈 CHANGE endpoint
        
        api_assert.assert_status_code(response, 200)
        return response.json()
    
    def delete_item(self, item_id: str) -> bool:
        """
        🗑️ Delete an item
        
        Args:
            item_id (str): ID of item to delete
            
        Returns:
            bool: True if deletion successful
        """
        response = self.delete(f"/items/{item_id}")  # 👈 CHANGE endpoint
        
        api_assert.assert_status_code_in(response, [200, 204])  # 204 = No Content
        return True
    
    def search_items(self, query: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        🔍 Search for items
        
        Args:
            query (str): Search query
            filters (dict): Additional filters
            
        Returns:
            dict: Search results
        """
        params = {"q": query}
        if filters:
            params.update(filters)
        
        response = self.get("/search/items", params=params)  # 👈 CHANGE endpoint
        
        api_assert.assert_status_code(response, 200)
        return response.json()
    
    # 🌟 STEP 7: Add any specialized methods for your API
    
    def bulk_operation(self, operation: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        📦 Perform bulk operations (if your API supports it)
        
        Args:
            operation (str): Operation type ('create', 'update', 'delete')
            items (list): List of items to process
            
        Returns:
            dict: Bulk operation results
        """
        payload = {
            "operation": operation,
            "items": items
        }
        
        response = self.post("/bulk", json=payload)  # 👈 CHANGE endpoint
        
        api_assert.assert_status_code(response, 200)
        return response.json()
    
    def get_analytics(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        📊 Get analytics data (example of domain-specific method)
        
        Args:
            start_date (str): Start date (YYYY-MM-DD)
            end_date (str): End date (YYYY-MM-DD)
            
        Returns:
            dict: Analytics data
        """
        params = {
            "start_date": start_date,
            "end_date": end_date
        }
        
        response = self.get("/analytics", params=params)  # 👈 CHANGE endpoint
        
        api_assert.assert_status_code(response, 200)
        return response.json()


# 🎯 STEP 8: Create test class for your API client
class TestYourAPIClient:
    """
    🧪 Test class for your custom API client
    
    📝 INSTRUCTIONS:
    1. Replace 'YourAPI' with your actual API name
    2. Update test data for your API's data structure
    3. Add tests for all your custom methods
    4. Run with: pytest tests/test_your_api.py
    """
    
    def setup_method(self):
        """🔧 Setup before each test"""
        # 👈 CHANGE: Use your actual API key (or mock for testing)
        self.client = YourAPIClient(api_key="test_api_key_12345")
    
    def test_authentication(self):
        """🔐 Test authentication"""
        credentials = {"api_key": "test_api_key_12345"}
        result = self.client.authenticate(credentials)
        assert isinstance(result, bool), "Authentication should return boolean"
    
    def test_health_check(self):
        """❤️ Test API health check"""
        is_healthy = self.client.health_check()
        assert isinstance(is_healthy, bool), "Health check should return boolean"
    
    def test_get_user_profile(self):
        """👤 Test getting user profile"""
        # 👈 CHANGE: Update expected data structure for your API
        profile = self.client.get_user_profile()
        assert isinstance(profile, dict), "Profile should be a dictionary"
        # Add more specific assertions based on your API's response
    
    def test_list_items(self):
        """📋 Test listing items"""
        items = self.client.list_items(page=1, per_page=5)
        assert isinstance(items, dict), "Items should be a dictionary"
        # 👈 ADD: More specific assertions for your API
    
    def test_create_item(self):
        """➕ Test creating an item"""
        # 👈 CHANGE: Update test data for your API
        test_data = {
            "name": "Test Item",
            "description": "This is a test item",
            "price": 99.99
        }
        
        created_item = self.client.create_item(test_data)
        assert isinstance(created_item, dict), "Created item should be a dictionary"
        # 👈 ADD: Verify the created item has expected fields


# 🎯 STEP 9: Usage example
def main():
    """
    🚀 EXAMPLE: How to use your custom API client
    
    Run this function to test your API client:
    python framework_templates/custom_api_template.py
    """
    
    print("🎯 Testing Your Custom API Client")
    print("=" * 50)
    
    try:
        # 👈 CHANGE: Use your actual API credentials
        client = YourAPIClient(api_key="your_api_key_here")
        
        # Test authentication
        print("🔐 Testing authentication...")
        auth_result = client.authenticate({"api_key": "your_api_key_here"})
        print(f"   Authentication: {'✅ Success' if auth_result else '❌ Failed'}")
        
        # Test health check
        print("❤️ Testing health check...")
        health = client.health_check()
        print(f"   Health: {'✅ Healthy' if health else '❌ Unhealthy'}")
        
        # Test getting user profile
        print("👤 Testing user profile...")
        try:
            profile = client.get_user_profile()
            print(f"   Profile: ✅ Retrieved successfully")
            print(f"   Data: {json.dumps(profile, indent=2)[:200]}...")
        except Exception as e:
            print(f"   Profile: ❌ Failed - {str(e)}")
        
        print("\n🎉 Testing completed!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("💡 Make sure to update the API URL and authentication method!")


if __name__ == "__main__":
    main()


# 📚 BEGINNER'S CHECKLIST:
"""
✅ CUSTOMIZATION CHECKLIST FOR YOUR API:

□ 1. Replace 'YourAPI' with your actual API name
□ 2. Update base_url to your API's URL
□ 3. Modify authentication method (API key, OAuth, Basic, etc.)
□ 4. Change health check endpoint
□ 5. Update default headers if needed
□ 6. Replace '/items' endpoints with your actual resource endpoints
□ 7. Update method names (get_items → get_products, get_orders, etc.)
□ 8. Modify test data structures to match your API
□ 9. Add API-specific methods (webhooks, uploads, etc.)
□ 10. Update error handling for your API's error format

🎯 NEXT STEPS:
□ 1. Copy this template to a new file (e.g., github_api_client.py)
□ 2. Customize all the marked sections (👈 CHANGE THIS)
□ 3. Create tests for your API client
□ 4. Add your client to the main framework
□ 5. Update documentation with your API examples

💡 NEED HELP?
- Check the framework documentation
- Look at existing clients (jsonplaceholder_client, reqres_client)
- Run the demo script to see examples
- Review the Facebook QA Tech Lead recommendations
""" 