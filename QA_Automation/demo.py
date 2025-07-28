#!/usr/bin/env python3
"""
Demo script to showcase the Advanced API Testing Framework
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.api_client import jsonplaceholder_client, reqres_client
from utils.assertions import api_assert
from utils.data_provider import data_provider
from utils.helpers import data_gen
from config.config import config_instance
from utils.logger import test_logger


def demo_basic_api_calls():
    """Demonstrate basic API calls"""
    print("\n" + "="*60)
    print("🚀 DEMO: Basic API Calls")
    print("="*60)
    
    # Test JSONPlaceholder API
    print("\n📡 Testing JSONPlaceholder API...")
    
    # Get all users
    response = jsonplaceholder_client.get("/users")
    print(f"✅ GET /users - Status: {response.status_code}")
    print(f"   Response time: {jsonplaceholder_client.response_time:.3f}s")
    print(f"   Users count: {len(response.json())}")
    
    # Get specific user
    response = jsonplaceholder_client.get("/users/1")
    print(f"✅ GET /users/1 - Status: {response.status_code}")
    user_data = response.json()
    print(f"   User: {user_data.get('name', 'Unknown')}")
    print(f"   Email: {user_data.get('email', 'Unknown')}")
    
    # Create new post
    new_post = {
        "title": "Demo Post from Framework",
        "body": "This post was created by the API testing framework demo",
        "userId": 1
    }
    response = jsonplaceholder_client.post("/posts", json_data=new_post)
    print(f"✅ POST /posts - Status: {response.status_code}")
    created_post = response.json()
    print(f"   Created post ID: {created_post.get('id', 'Unknown')}")


def demo_assertions():
    """Demonstrate advanced assertions"""
    print("\n" + "="*60)
    print("🔍 DEMO: Advanced Assertions")
    print("="*60)
    
    print("\n🧪 Testing assertions with JSONPlaceholder...")
    
    # Test user endpoint
    response = jsonplaceholder_client.get("/users/1")
    
    try:
        # Status code assertion
        api_assert.assert_status_code(response, 200)
        print("✅ Status code assertion passed")
        
        # Content type assertion
        api_assert.assert_content_type(response, "application/json")
        print("✅ Content type assertion passed")
        
        # Response time assertion
        api_assert.assert_response_time(jsonplaceholder_client.response_time, 5.0)
        print("✅ Response time assertion passed")
        
        # JSON key existence assertions
        api_assert.assert_json_key_exists(response, "id")
        api_assert.assert_json_key_exists(response, "name")
        api_assert.assert_json_key_exists(response, "email")
        print("✅ JSON key existence assertions passed")
        
        # JSON value assertions
        api_assert.assert_json_key_value(response, "id", 1)
        print("✅ JSON value assertion passed")
        
        # Data type assertions
        api_assert.assert_json_types(response, {
            "id": int,
            "name": str,
            "email": str
        })
        print("✅ Data type assertions passed")
        
    except AssertionError as e:
        print(f"❌ Assertion failed: {e}")


def demo_data_provider():
    """Demonstrate data provider functionality"""
    print("\n" + "="*60)
    print("📊 DEMO: Data Provider & Test Data")
    print("="*60)
    
    # Load user test data
    print("\n📁 Loading test data...")
    user_data = data_provider.get_user_test_data("valid")
    print(f"✅ Loaded valid user data: {user_data.get('name', 'Unknown')}")
    
    # Load post test data
    post_data = data_provider.get_post_test_data("valid")
    print(f"✅ Loaded valid post data: {post_data.get('title', 'Unknown')[:50]}...")
    
    # Generate random data
    print("\n🎲 Generating random test data...")
    random_user = data_gen.random_user_data()
    print(f"✅ Generated random user: {random_user.get('name', 'Unknown')}")
    
    random_post = data_gen.random_post_data()
    print(f"✅ Generated random post: {random_post.get('title', 'Unknown')[:50]}...")
    
    # Load CSV test data
    csv_data = data_provider.get_parametrized_data("test_data.csv")
    print(f"✅ Loaded {len(csv_data)} test cases from CSV")


def demo_authentication():
    """Demonstrate authentication testing"""
    print("\n" + "="*60)
    print("🔐 DEMO: Authentication Testing")
    print("="*60)
    
    print("\n🔑 Testing ReqRes authentication...")
    
    # Test user registration
    registration_data = {
        "email": "eve.holt@reqres.in",
        "password": "pistol"
    }
    
    response = reqres_client.post("/register", json_data=registration_data)
    print(f"✅ Registration - Status: {response.status_code}")
    
    if response.status_code == 200:
        reg_data = response.json()
        print(f"   User ID: {reg_data.get('id', 'Unknown')}")
        print(f"   Token: {reg_data.get('token', 'Unknown')[:20]}...")
    
    # Test user login
    login_data = {
        "email": "eve.holt@reqres.in",
        "password": "cityslicka"
    }
    
    response = reqres_client.post("/login", json_data=login_data)
    print(f"✅ Login - Status: {response.status_code}")
    
    if response.status_code == 200:
        login_response = response.json()
        token = login_response.get('token', '')
        print(f"   Token: {token[:20]}...")
        
        # Test authenticated request
        reqres_client.set_auth_token(token)
        response = reqres_client.get("/users/2")
        print(f"✅ Authenticated request - Status: {response.status_code}")


def demo_configuration():
    """Demonstrate configuration management"""
    print("\n" + "="*60)
    print("⚙️ DEMO: Configuration Management")
    print("="*60)
    
    print(f"\n🌍 Current environment: {config_instance.environment}")
    print(f"🔗 Base URL: {config_instance.base_url}")
    print(f"⏱️ Timeout: {config_instance.timeout}s")
    print(f"🔄 Retry count: {config_instance.retry_count}")
    print(f"📄 Headers: {config_instance.headers}")


def demo_logging():
    """Demonstrate logging capabilities"""
    print("\n" + "="*60)
    print("📝 DEMO: Logging System")
    print("="*60)
    
    print("\n📋 Demonstrating different log levels...")
    
    test_logger.log_test_start("demo_test")
    test_logger.log_request("GET", "https://example.com/api/users", {"Authorization": "Bearer token"})
    test_logger.log_response(200, 0.245, '{"id": 1, "name": "Demo User"}')
    test_logger.log_assertion("Status code should be 200", True)
    test_logger.log_test_end("demo_test", "passed")
    
    print("✅ Logs written to logs/ directory")
    print("   - api_tests.log: General logs")
    print("   - errors.log: Error logs")
    print("   - api_requests.log: Request/response logs")


def demo_performance():
    """Demonstrate performance testing"""
    print("\n" + "="*60)
    print("⚡ DEMO: Performance Testing")
    print("="*60)
    
    print("\n🏃‍♂️ Running performance tests...")
    
    # Test multiple endpoints for performance
    endpoints = ["/users", "/posts", "/comments", "/albums", "/photos"]
    results = []
    
    for endpoint in endpoints:
        response = jsonplaceholder_client.get(endpoint)
        response_time = jsonplaceholder_client.response_time
        results.append({
            "endpoint": endpoint,
            "status": response.status_code,
            "time": response_time,
            "size": len(response.text)
        })
        print(f"✅ {endpoint:<12} - {response.status_code} - {response_time:.3f}s - {len(response.text):,} bytes")
    
    # Calculate averages
    avg_time = sum(r["time"] for r in results) / len(results)
    max_time = max(r["time"] for r in results)
    min_time = min(r["time"] for r in results)
    
    print(f"\n📊 Performance Summary:")
    print(f"   Average response time: {avg_time:.3f}s")
    print(f"   Fastest response: {min_time:.3f}s")
    print(f"   Slowest response: {max_time:.3f}s")


def demo_error_handling():
    """Demonstrate error handling"""
    print("\n" + "="*60)
    print("⚠️ DEMO: Error Handling")
    print("="*60)
    
    print("\n🧪 Testing error scenarios...")
    
    # Test 404 error
    response = jsonplaceholder_client.get("/users/999")
    print(f"✅ GET /users/999 - Status: {response.status_code} (Expected 404)")
    
    # Test invalid endpoint
    response = jsonplaceholder_client.get("/invalid-endpoint")
    print(f"✅ GET /invalid-endpoint - Status: {response.status_code} (Expected 404)")
    
    # Test malformed data
    try:
        response = jsonplaceholder_client.post("/posts", json_data="invalid json")
    except Exception as e:
        print(f"✅ Handled malformed data error: {type(e).__name__}")


def run_all_demos():
    """Run all demonstration functions"""
    print("🎉 Welcome to the Advanced API Testing Framework Demo!")
    print("This demo will showcase the framework's capabilities.")
    
    try:
        demo_configuration()
        demo_basic_api_calls()
        demo_assertions()
        demo_data_provider()
        demo_authentication()
        demo_logging()
        demo_performance()
        demo_error_handling()
        
        print("\n" + "="*60)
        print("🎊 DEMO COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\n✨ Framework Features Demonstrated:")
        print("   ✅ Basic API operations (GET, POST)")
        print("   ✅ Advanced assertions and validations")
        print("   ✅ Data provider and test data management")
        print("   ✅ Authentication and authorization")
        print("   ✅ Configuration management")
        print("   ✅ Comprehensive logging")
        print("   ✅ Performance testing")
        print("   ✅ Error handling")
        
        print("\n🚀 Ready to run tests!")
        print("   Command: pytest")
        print("   Smoke tests: pytest -m smoke")
        print("   With reports: pytest --html=reports/report.html")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_demos() 