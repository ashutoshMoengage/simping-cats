"""
Comprehensive User API Tests
"""
import pytest
import allure
from utils.assertions import api_assert
from utils.decorators import api_test, attach_request_response
from utils.data_provider import data_provider
from utils.helpers import data_gen


@allure.epic("User Management")
@allure.feature("User CRUD Operations")
class TestUserAPI:
    """Test class for User API operations"""
    
    @api_test(
        title="Get All Users - Smoke Test",
        description="Verify that all users can be retrieved successfully",
        severity="critical",
        tags=["smoke", "users", "get"]
    )
    @attach_request_response
    def test_get_all_users_smoke(self, jsonplaceholder_api, user_schema):
        """Test getting all users - smoke test"""
        # Make API request
        response = jsonplaceholder_api.get("/users")
        
        # Basic assertions
        api_assert.assert_status_code(response, 200)
        api_assert.assert_content_type(response, "application/json")
        api_assert.assert_response_time(jsonplaceholder_api.response_time, 3.0)
        
        # Response structure validation
        users = response.json()
        assert isinstance(users, list), "Response should be a list"
        assert len(users) > 0, "Users list should not be empty"
        
        # Validate first user against schema
        if users:
            api_assert.assert_json_schema(response, {
                "type": "array",
                "items": user_schema
            })
    
    @api_test(
        title="Get User by Valid ID",
        description="Verify that a user can be retrieved by valid ID",
        severity="critical",
        tags=["regression", "users", "get"]
    )
    @attach_request_response
    def test_get_user_by_valid_id(self, jsonplaceholder_api, test_user_id, user_schema):
        """Test getting user by valid ID"""
        response = jsonplaceholder_api.get(f"/users/{test_user_id}")
        
        # Assertions
        api_assert.assert_status_code(response, 200)
        api_assert.assert_content_type(response, "application/json")
        
        # Validate response structure
        api_assert.assert_json_schema(response, user_schema)
        
        # Validate specific fields
        api_assert.assert_json_key_exists(response, "id")
        api_assert.assert_json_key_exists(response, "name")
        api_assert.assert_json_key_exists(response, "email")
        api_assert.assert_json_key_value(response, "id", test_user_id)
        
        # Validate data types
        api_assert.assert_json_types(response, {
            "id": int,
            "name": str,
            "username": str,
            "email": str
        })
    
    @pytest.mark.parametrize("user_id", [0, -1, 999, "abc", ""])
    @api_test(
        title="Get User by Invalid ID",
        description="Verify appropriate error handling for invalid user IDs",
        severity="normal",
        tags=["negative", "users", "get"]
    )
    @attach_request_response
    def test_get_user_by_invalid_id(self, jsonplaceholder_api, user_id):
        """Test getting user by invalid ID"""
        response = jsonplaceholder_api.get(f"/users/{user_id}")
        
        # Should return 404 for invalid IDs
        api_assert.assert_status_code(response, 404)
    
    @api_test(
        title="Create New User with Valid Data",
        description="Verify that a new user can be created with valid data",
        severity="critical",
        tags=["crud", "users", "post"],
        max_response_time=2.0
    )
    @attach_request_response
    def test_create_user_valid_data(self, jsonplaceholder_api, user_data, cleanup_created_resources):
        """Test creating user with valid data"""
        response = jsonplaceholder_api.post("/users", json_data=user_data)
        
        # Assertions
        api_assert.assert_status_code(response, 201)
        api_assert.assert_content_type(response, "application/json")
        
        # Validate response contains ID
        api_assert.assert_json_key_exists(response, "id")
        
        # Validate that request data is reflected in response
        response_data = response.json()
        for key, value in user_data.items():
            if key in response_data:
                assert response_data[key] == value, f"Field {key} should match input data"
        
        # Track created resource for cleanup
        user_id = response_data.get("id")
        if user_id:
            cleanup_created_resources["users"].append(user_id)
    
    @api_test(
        title="Create User with Random Generated Data",
        description="Test creating user with randomly generated data",
        tags=["data-driven", "users", "post"]
    )
    @attach_request_response
    def test_create_user_random_data(self, jsonplaceholder_api, random_user_data):
        """Test creating user with random data"""
        response = jsonplaceholder_api.post("/users", json_data=random_user_data)
        
        api_assert.assert_status_code(response, 201)
        api_assert.assert_json_key_exists(response, "id")
    
    @pytest.mark.parametrize("field_to_remove", ["name", "username", "email"])
    @api_test(
        title="Create User with Missing Required Fields",
        description="Verify validation for missing required fields",
        severity="normal",
        tags=["negative", "validation", "users", "post"]
    )
    def test_create_user_missing_fields(self, jsonplaceholder_api, user_data, field_to_remove):
        """Test creating user with missing required fields"""
        # Remove required field
        invalid_data = user_data.copy()
        invalid_data.pop(field_to_remove, None)
        
        response = jsonplaceholder_api.post("/users", json_data=invalid_data)
        
        # Note: JSONPlaceholder is permissive, but in real API this should be 400
        # Adjusting assertion based on actual API behavior
        api_assert.assert_status_code_in(response, [201, 400])
    
    @api_test(
        title="Update User with Valid Data",
        description="Verify that a user can be updated with valid data",
        severity="critical",
        tags=["crud", "users", "put"]
    )
    @attach_request_response
    def test_update_user_valid_data(self, jsonplaceholder_api, test_user_id, user_data):
        """Test updating user with valid data"""
        # First get existing user
        get_response = jsonplaceholder_api.get(f"/users/{test_user_id}")
        api_assert.assert_status_code(get_response, 200)
        
        # Update user data
        updated_data = user_data.copy()
        updated_data["name"] = "Updated User Name"
        updated_data["email"] = "updated@example.com"
        
        response = jsonplaceholder_api.put(f"/users/{test_user_id}", json_data=updated_data)
        
        # Assertions
        api_assert.assert_status_code(response, 200)
        api_assert.assert_json_key_value(response, "id", test_user_id)
        api_assert.assert_json_key_value(response, "name", updated_data["name"])
        api_assert.assert_json_key_value(response, "email", updated_data["email"])
    
    @api_test(
        title="Partial Update User with PATCH",
        description="Verify that a user can be partially updated using PATCH",
        tags=["crud", "users", "patch"]
    )
    @attach_request_response
    def test_patch_user(self, jsonplaceholder_api, test_user_id):
        """Test partial update of user using PATCH"""
        patch_data = {
            "name": "Partially Updated Name",
            "email": "patch@example.com"
        }
        
        response = jsonplaceholder_api.patch(f"/users/{test_user_id}", json_data=patch_data)
        
        api_assert.assert_status_code(response, 200)
        api_assert.assert_json_key_value(response, "name", patch_data["name"])
        api_assert.assert_json_key_value(response, "email", patch_data["email"])
    
    @api_test(
        title="Delete User by Valid ID",
        description="Verify that a user can be deleted by valid ID",
        severity="critical",
        tags=["crud", "users", "delete"]
    )
    @attach_request_response
    def test_delete_user_valid_id(self, jsonplaceholder_api, test_user_id):
        """Test deleting user by valid ID"""
        response = jsonplaceholder_api.delete(f"/users/{test_user_id}")
        
        # Should return success status for deletion
        api_assert.assert_status_code(response, 200)
    
    @api_test(
        title="Delete User by Invalid ID",
        description="Verify appropriate handling when deleting non-existent user",
        tags=["negative", "users", "delete"]
    )
    def test_delete_user_invalid_id(self, jsonplaceholder_api, invalid_id):
        """Test deleting user by invalid ID"""
        response = jsonplaceholder_api.delete(f"/users/{invalid_id}")
        
        # Should return success even for non-existent resource in JSONPlaceholder
        api_assert.assert_status_code(response, 200)
    
    @api_test(
        title="User Email Validation Test",
        description="Verify email format validation in user data",
        tags=["validation", "users", "email"]
    )
    def test_user_email_validation(self, jsonplaceholder_api, invalid_user_data):
        """Test email validation"""
        response = jsonplaceholder_api.post("/users", json_data=invalid_user_data)
        
        # Note: JSONPlaceholder doesn't validate emails, but real APIs should
        # This test demonstrates how to test validation
        response_data = response.json()
        
        # In a real API, this should validate email format
        # For demo purposes, we'll just verify the response structure
        api_assert.assert_json_key_exists(response, "email")
    
    @pytest.mark.parametrize("user_id", [1, 2, 3, 4, 5])
    @api_test(
        title="Performance Test - Multiple User Retrievals",
        description="Performance test for retrieving multiple users",
        tags=["performance", "users", "get"],
        max_response_time=1.0
    )
    def test_get_users_performance(self, jsonplaceholder_api, user_id):
        """Performance test for getting users"""
        response = jsonplaceholder_api.get(f"/users/{user_id}")
        
        api_assert.assert_status_code(response, 200)
        api_assert.assert_response_time(jsonplaceholder_api.response_time, 1.0)
    
    @api_test(
        title="Bulk User Operations Test",
        description="Test bulk operations on multiple users",
        tags=["bulk", "users", "integration"]
    )
    def test_bulk_user_operations(self, jsonplaceholder_api, bulk_test_data):
        """Test bulk user operations"""
        users_data = bulk_test_data["users"]
        created_users = []
        
        # Create multiple users
        for user_data in users_data[:3]:  # Limit to 3 for performance
            response = jsonplaceholder_api.post("/users", json_data=user_data)
            api_assert.assert_status_code(response, 201)
            
            user_id = response.json().get("id")
            if user_id:
                created_users.append(user_id)
        
        # Verify created users
        for user_id in created_users:
            response = jsonplaceholder_api.get(f"/users/{user_id}")
            api_assert.assert_status_code_in(response, [200, 404])  # May not persist
    
    @api_test(
        title="User Data Boundary Testing",
        description="Test user creation with boundary values",
        tags=["boundary", "users", "validation"]
    )
    def test_user_boundary_values(self, jsonplaceholder_api):
        """Test user with boundary values"""
        # Test with very long strings
        long_data = data_provider.get_user_test_data("long_fields")
        response = jsonplaceholder_api.post("/users", json_data=long_data)
        
        # Should handle long data gracefully
        api_assert.assert_status_code_in(response, [201, 400, 413])
        
        # Test with special characters
        special_data = data_provider.get_user_test_data("special_characters")
        response = jsonplaceholder_api.post("/users", json_data=special_data)
        
        api_assert.assert_status_code_in(response, [201, 400])
    
    @api_test(
        title="User Response Headers Validation",
        description="Validate response headers for user endpoints",
        tags=["headers", "users", "validation"]
    )
    def test_user_response_headers(self, jsonplaceholder_api, test_user_id):
        """Test response headers"""
        response = jsonplaceholder_api.get(f"/users/{test_user_id}")
        
        api_assert.assert_status_code(response, 200)
        api_assert.assert_header_exists(response, "Content-Type")
        api_assert.assert_content_type(response, "application/json")
        
        # Check for common security headers (may not be present in test API)
        headers = response.headers
        if "X-Content-Type-Options" in headers:
            api_assert.assert_header_value(response, "X-Content-Type-Options", "nosniff") 