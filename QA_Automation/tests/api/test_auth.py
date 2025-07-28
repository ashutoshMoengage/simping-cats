"""
Authentication and Authorization API Tests
"""
import pytest
import allure
from utils.assertions import api_assert
from utils.decorators import api_test, attach_request_response
from utils.api_client import reqres_client


@allure.epic("Security")
@allure.feature("Authentication & Authorization")
class TestAuthAPI:
    """Test class for Authentication and Authorization"""
    
    @api_test(
        title="User Registration - Valid Data",
        description="Verify successful user registration with valid data",
        severity="critical",
        tags=["auth", "registration", "post"]
    )
    @attach_request_response
    def test_user_registration_valid(self, reqres_api):
        """Test user registration with valid data"""
        registration_data = {
            "email": "eve.holt@reqres.in",
            "password": "pistol"
        }
        
        response = reqres_api.post("/register", json_data=registration_data)
        
        # Should return 200 and contain id and token
        api_assert.assert_status_code(response, 200)
        api_assert.assert_content_type(response, "application/json")
        
        # Validate response structure
        api_assert.assert_json_key_exists(response, "id")
        api_assert.assert_json_key_exists(response, "token")
        
        # Validate data types
        api_assert.assert_json_types(response, {
            "id": int,
            "token": str
        })
    
    @api_test(
        title="User Registration - Missing Password",
        description="Verify error handling when password is missing",
        severity="normal",
        tags=["auth", "registration", "negative", "post"]
    )
    def test_user_registration_missing_password(self, reqres_api):
        """Test user registration with missing password"""
        registration_data = {
            "email": "sydney@fife"
        }
        
        response = reqres_api.post("/register", json_data=registration_data)
        
        # Should return 400 Bad Request
        api_assert.assert_status_code(response, 400)
        api_assert.assert_json_key_exists(response, "error")
        
        # Verify error message
        error_message = response.json().get("error", "")
        assert "password" in error_message.lower(), "Error should mention missing password"
    
    @api_test(
        title="User Login - Valid Credentials",
        description="Verify successful login with valid credentials",
        severity="critical",
        tags=["auth", "login", "post"]
    )
    @attach_request_response
    def test_user_login_valid(self, reqres_api):
        """Test user login with valid credentials"""
        login_data = {
            "email": "eve.holt@reqres.in",
            "password": "cityslicka"
        }
        
        response = reqres_api.post("/login", json_data=login_data)
        
        # Should return 200 and contain token
        api_assert.assert_status_code(response, 200)
        api_assert.assert_content_type(response, "application/json")
        
        # Validate response structure
        api_assert.assert_json_key_exists(response, "token")
        
        # Validate token format (should be non-empty string)
        token = response.json().get("token")
        assert token and len(token) > 0, "Token should not be empty"
        assert isinstance(token, str), "Token should be a string"
    
    @api_test(
        title="User Login - Invalid Credentials",
        description="Verify error handling for invalid credentials",
        severity="normal",
        tags=["auth", "login", "negative", "post"]
    )
    def test_user_login_invalid(self, reqres_api):
        """Test user login with invalid credentials"""
        login_data = {
            "email": "invalid@user.com",
            "password": "wrongpassword"
        }
        
        response = reqres_api.post("/login", json_data=login_data)
        
        # Should return 400 Bad Request
        api_assert.assert_status_code(response, 400)
        api_assert.assert_json_key_exists(response, "error")
    
    @api_test(
        title="User Login - Missing Password",
        description="Verify error handling when password is missing from login",
        tags=["auth", "login", "validation", "post"]
    )
    def test_user_login_missing_password(self, reqres_api):
        """Test user login with missing password"""
        login_data = {
            "email": "eve.holt@reqres.in"
        }
        
        response = reqres_api.post("/login", json_data=login_data)
        
        # Should return 400 Bad Request
        api_assert.assert_status_code(response, 400)
        api_assert.assert_json_key_exists(response, "error")
        
        # Verify error message mentions password
        error_message = response.json().get("error", "")
        assert "password" in error_message.lower(), "Error should mention missing password"
    
    @pytest.mark.parametrize("invalid_email", [
        "",  # Empty email
        "invalid",  # No @ symbol
        "@domain.com",  # No username
        "user@",  # No domain
    ])
    @api_test(
        title="Login Email Format Validation",
        description="Test various invalid email formats in login",
        tags=["auth", "login", "validation", "parametrize"]
    )
    def test_login_email_format_validation(self, reqres_api, invalid_email):
        """Test login with various invalid email formats"""
        login_data = {
            "email": invalid_email,
            "password": "testpassword"
        }
        
        response = reqres_api.post("/login", json_data=login_data)
        
        # Should return 400 for invalid email formats
        api_assert.assert_status_code(response, 400)
    
    @api_test(
        title="Token-Based Authentication Test",
        description="Test API access with authentication token",
        tags=["auth", "token", "authorization"]
    )
    def test_token_based_authentication(self, reqres_api):
        """Test token-based authentication"""
        # First, login to get token
        login_data = {
            "email": "eve.holt@reqres.in",
            "password": "cityslicka"
        }
        
        login_response = reqres_api.post("/login", json_data=login_data)
        api_assert.assert_status_code(login_response, 200)
        
        token = login_response.json().get("token")
        assert token, "Token should be received from login"
        
        # Use token for authenticated request
        reqres_api.set_auth_token(token)
        
        # Make authenticated request
        response = reqres_api.get("/users/2")
        
        # Should work with valid token
        api_assert.assert_status_code(response, 200)
        
        # Clean up - remove token
        reqres_api.remove_header('Authorization') 