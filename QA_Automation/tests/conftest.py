"""
Pytest fixtures and configuration for API testing framework
"""
import pytest
import json
from pathlib import Path
from typing import Dict, Any, List

from utils.api_client import APIClient, jsonplaceholder_client, reqres_client
from utils.data_provider import data_provider
from utils.helpers import data_gen, test_helper
from utils.logger import test_logger
from config.config import config_instance


@pytest.fixture(scope="session")
def api_client():
    """Fixture providing the main API client"""
    client = APIClient()
    yield client
    client.close()


@pytest.fixture(scope="session")
def jsonplaceholder_api():
    """Fixture providing JSONPlaceholder API client"""
    yield jsonplaceholder_client


@pytest.fixture(scope="session")
def reqres_api():
    """Fixture providing ReqRes API client"""
    yield reqres_client


@pytest.fixture(scope="function")
def user_data():
    """Fixture providing valid user test data"""
    return data_provider.get_user_test_data("valid")


@pytest.fixture(scope="function")
def post_data():
    """Fixture providing valid post test data"""
    return data_provider.get_post_test_data("valid")


@pytest.fixture(scope="function")
def invalid_user_data():
    """Fixture providing invalid user test data"""
    return data_provider.get_user_test_data("invalid_email")


@pytest.fixture(scope="function")
def minimal_user_data():
    """Fixture providing minimal user test data"""
    return data_provider.get_user_test_data("minimal")


@pytest.fixture(scope="function")
def random_user_data():
    """Fixture providing randomly generated user data"""
    return data_gen.random_user_data()


@pytest.fixture(scope="function")
def random_post_data():
    """Fixture providing randomly generated post data"""
    return data_gen.random_post_data()


@pytest.fixture(scope="function")
def user_schema():
    """Fixture providing user JSON schema for validation"""
    schema_path = Path(__file__).parent.parent / "data" / "schema" / "user_schema.json"
    with open(schema_path, 'r') as f:
        return json.load(f)


@pytest.fixture(scope="function")
def post_schema():
    """Fixture providing post JSON schema for validation"""
    schema_path = Path(__file__).parent.parent / "data" / "schema" / "post_schema.json"
    with open(schema_path, 'r') as f:
        return json.load(f)


@pytest.fixture(scope="function")
def test_user_id():
    """Fixture providing a test user ID"""
    return 1


@pytest.fixture(scope="function")
def test_post_id():
    """Fixture providing a test post ID"""
    return 1


@pytest.fixture(scope="function")
def invalid_id():
    """Fixture providing an invalid ID for negative testing"""
    return 999


@pytest.fixture(scope="function")
def parametrized_test_data():
    """Fixture providing parametrized test data from CSV"""
    return data_provider.get_parametrized_data("test_data.csv")


@pytest.fixture(scope="function", autouse=True)
def test_setup_teardown(request):
    """Auto-used fixture for test setup and teardown"""
    test_name = request.node.name
    test_logger.log_test_start(test_name)
    
    yield
    
    # Test teardown logic here if needed
    test_logger.log_test_end(test_name, "completed")


@pytest.fixture(scope="session")
def test_environment():
    """Fixture providing test environment configuration"""
    return config_instance.environment


@pytest.fixture(scope="function")
def cleanup_created_resources():
    """Fixture to track and cleanup created resources"""
    created_resources = {
        "users": [],
        "posts": [],
        "comments": []
    }
    
    yield created_resources
    
    # Cleanup logic would go here
    # This is where you'd delete any resources created during testing
    test_logger.log_test_end("cleanup", "completed")


@pytest.fixture(scope="function")
def mock_response_data():
    """Fixture providing mock response data for testing"""
    return {
        "user": {
            "id": 1,
            "name": "Test User",
            "username": "testuser",
            "email": "test@example.com",
            "phone": "1-555-123-4567",
            "website": "http://example.com"
        },
        "post": {
            "id": 1,
            "title": "Test Post",
            "body": "Test post body",
            "userId": 1
        }
    }


@pytest.fixture(scope="function")
def response_time_threshold():
    """Fixture providing response time threshold for performance tests"""
    return 2.0  # 2 seconds


@pytest.fixture(scope="function")
def bulk_test_data():
    """Fixture providing bulk test data"""
    users = data_provider.load_json("users.json").get("bulk_users", [])
    posts = data_provider.load_json("posts.json").get("bulk_posts", [])
    
    return {
        "users": users,
        "posts": posts
    }


@pytest.fixture(scope="session")
def database_connection():
    """Fixture providing database connection (if needed)"""
    # This would be implemented based on your database needs
    # Example: connection = create_db_connection()
    connection = None
    
    yield connection
    
    # Cleanup database connection
    if connection:
        # connection.close()
        pass


@pytest.fixture(scope="function")
def authenticated_client():
    """Fixture providing authenticated API client"""
    client = APIClient()
    
    # Add authentication logic here if needed
    # Example: client.set_auth_token("your-token-here")
    
    yield client
    client.close()


@pytest.fixture(scope="function", params=[
    ("valid", 200),
    ("invalid_email", 400),
    ("empty_fields", 400)
])
def user_test_cases(request):
    """Parametrized fixture for user test cases"""
    user_type, expected_status = request.param
    user_data = data_provider.get_user_test_data(user_type)
    
    return {
        "user_type": user_type,
        "user_data": user_data,
        "expected_status": expected_status
    }


@pytest.fixture(scope="function", params=[1, 2, 3, 4, 5])
def valid_user_ids(request):
    """Parametrized fixture for valid user IDs"""
    return request.param


@pytest.fixture(scope="function", params=[0, -1, 999, "abc", None])
def invalid_user_ids(request):
    """Parametrized fixture for invalid user IDs"""
    return request.param


@pytest.fixture(scope="function")
def api_endpoints():
    """Fixture providing API endpoints"""
    return {
        "users": "/users",
        "posts": "/posts",
        "comments": "/comments",
        "albums": "/albums",
        "photos": "/photos",
        "todos": "/todos"
    }


@pytest.fixture(scope="function")
def http_methods():
    """Fixture providing HTTP methods for testing"""
    return ["GET", "POST", "PUT", "PATCH", "DELETE"]


@pytest.fixture(scope="function")
def content_types():
    """Fixture providing content types for testing"""
    return [
        "application/json",
        "application/xml",
        "text/plain",
        "text/html"
    ]


# Pytest hooks for custom behavior
def pytest_configure(config):
    """Configure pytest with custom markers and settings"""
    config.addinivalue_line(
        "markers", "smoke: mark test as smoke test"
    )
    config.addinivalue_line(
        "markers", "regression: mark test as regression test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names"""
    for item in items:
        # Add smoke marker to tests with 'smoke' in name
        if "smoke" in item.name.lower():
            item.add_marker(pytest.mark.smoke)
        
        # Add slow marker to performance tests
        if "performance" in item.name.lower() or "load" in item.name.lower():
            item.add_marker(pytest.mark.slow)


def pytest_runtest_makereport(item, call):
    """Hook to customize test reporting"""
    if call.when == "call":
        # Log test result
        test_name = item.name
        if call.excinfo is None:
            test_logger.log_test_end(test_name, "passed")
        else:
            test_logger.log_test_end(test_name, "failed")


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Session-level fixture to setup test environment"""
    test_logger.log_test_start("test_session_setup")
    
    # Setup test environment
    # This could include database setup, test data preparation, etc.
    
    yield
    
    # Teardown test environment
    test_logger.log_test_end("test_session_teardown", "completed") 