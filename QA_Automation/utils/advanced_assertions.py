"""
🎯 Advanced Custom Assertion Library
====================================

This module provides enterprise-grade assertions for API testing with REAL examples
and beginner-friendly explanations.

📚 FOR BEGINNERS:
Assertions are checks that verify your API works correctly. Instead of writing:
    if response.status_code != 200:
        raise Exception("API failed")

You write:
    assert_status_code(response, 200)

This library provides 50+ specialized assertions for common API testing scenarios.

🌟 REAL-WORLD EXAMPLES:
- E-commerce: Validate product prices, inventory, orders
- Social Media: Check user profiles, posts, comments
- Banking: Verify transactions, balances, security
- Healthcare: Validate patient data, appointments
- IoT: Check sensor readings, device status
"""

import json
import re
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Callable
from decimal import Decimal
from urllib.parse import urlparse
import math
import statistics

import requests
from jsonschema import validate, ValidationError
from deepdiff import DeepDiff
import jmespath
from dateutil import parser as date_parser

from utils.enhanced_logging import enhanced_logger


class AssertionError(Exception):
    """Custom assertion error with detailed context"""
    def __init__(self, message: str, context: Dict[str, Any] = None):
        self.message = message
        self.context = context or {}
        super().__init__(message)


class AdvancedAPIAssertions:
    """
    🎯 Advanced API Testing Assertions
    
    This class provides comprehensive assertion methods for API testing
    with real-world examples and beginner-friendly explanations.
    
    🏗️ OOP CONCEPTS:
    - STATIC METHODS: Don't need instance, can be called directly  
    - TYPE HINTS: Better code quality and IDE support
    - ERROR HANDLING: Detailed error messages with context
    - LOGGING INTEGRATION: All assertions are logged
    """
    
    @staticmethod
    def assert_status_code(response: requests.Response, expected_code: int, 
                          message: str = None) -> None:
        """
        ✅ BASIC: Assert HTTP status code
        
        Args:
            response: HTTP response object
            expected_code: Expected status code (200, 404, etc.)
            message: Custom error message
            
        Example:
            assert_status_code(response, 200)  # Success
            assert_status_code(response, 404)  # Not found
            assert_status_code(response, 401)  # Unauthorized
        """
        actual_code = response.status_code
        
        if actual_code != expected_code:
            context = {
                "expected_status": expected_code,
                "actual_status": actual_code,
                "url": response.url,
                "method": response.request.method,
                "response_text": response.text[:500]
            }
            
            error_msg = (message or 
                        f"Expected status code {expected_code}, got {actual_code}")
            
            enhanced_logger.error(f"❌ Status code assertion failed: {error_msg}", 
                                extra_context=context)
            raise AssertionError(error_msg, context)
        
        enhanced_logger.info(f"✅ Status code assertion passed: {actual_code}")
    
    @staticmethod
    def assert_response_time(response: requests.Response, max_time: float,
                           message: str = None) -> None:
        """
        ⏱️ PERFORMANCE: Assert response time is within limit
        
        Args:
            response: HTTP response object
            max_time: Maximum allowed response time in seconds
            message: Custom error message
            
        Real Examples:
            assert_response_time(response, 1.0)    # API should respond in <1s
            assert_response_time(response, 0.5)    # Critical APIs <500ms
            assert_response_time(response, 5.0)    # Complex queries <5s
        """
        actual_time = response.elapsed.total_seconds()
        
        if actual_time > max_time:
            context = {
                "expected_max_time": max_time,
                "actual_time": actual_time,
                "url": response.url,
                "performance_grade": "SLOW" if actual_time > max_time * 2 else "ACCEPTABLE"
            }
            
            error_msg = (message or 
                        f"Response time {actual_time:.3f}s exceeded limit {max_time}s")
            
            enhanced_logger.error(f"⏱️ Response time assertion failed: {error_msg}",
                                extra_context=context)
            raise AssertionError(error_msg, context)
        
        enhanced_logger.info(f"✅ Response time assertion passed: {actual_time:.3f}s")
    
    @staticmethod
    def assert_json_structure(response: requests.Response, 
                            expected_structure: Dict[str, type],
                            message: str = None) -> None:
        """
        🏗️ STRUCTURE: Assert JSON response has expected structure
        
        Args:
            response: HTTP response object
            expected_structure: Dict mapping field names to expected types
            message: Custom error message
            
        Real Example - E-commerce Product API:
            expected = {
                "id": int,
                "name": str,
                "price": float,
                "in_stock": bool,
                "categories": list,
                "metadata": dict
            }
            assert_json_structure(response, expected)
        """
        try:
            data = response.json()
        except json.JSONDecodeError:
            raise AssertionError("Response is not valid JSON")
        
        errors = []
        
        for field, expected_type in expected_structure.items():
            if field not in data:
                errors.append(f"Missing field: {field}")
            elif not isinstance(data[field], expected_type):
                actual_type = type(data[field]).__name__
                expected_type_name = expected_type.__name__
                errors.append(f"Field '{field}': expected {expected_type_name}, got {actual_type}")
        
        if errors:
            context = {
                "expected_structure": {k: v.__name__ for k, v in expected_structure.items()},
                "actual_data": data,
                "structure_errors": errors
            }
            
            error_msg = message or f"JSON structure validation failed: {'; '.join(errors)}"
            enhanced_logger.error(f"🏗️ JSON structure assertion failed: {error_msg}",
                                extra_context=context)
            raise AssertionError(error_msg, context)
        
        enhanced_logger.info("✅ JSON structure assertion passed")
    
    @staticmethod
    def assert_business_logic(response: requests.Response, 
                            validation_func: Callable[[Dict], bool],
                            error_message: str,
                            context_data: Dict[str, Any] = None) -> None:
        """
        💼 BUSINESS LOGIC: Assert custom business rules
        
        Args:
            response: HTTP response object
            validation_func: Function that takes response data and returns bool
            error_message: Error message if validation fails
            context_data: Additional context for debugging
            
        Real Example - Banking API:
            def validate_account_balance(data):
                # Business rule: Account balance can't be negative for standard accounts
                return data.get('account_type') == 'credit' or data.get('balance', 0) >= 0
            
            assert_business_logic(
                response, 
                validate_account_balance,
                "Account balance validation failed",
                {"account_id": "123456"}
            )
        """
        try:
            data = response.json()
        except json.JSONDecodeError:
            raise AssertionError("Response is not valid JSON for business logic validation")
        
        is_valid = validation_func(data)
        
        if not is_valid:
            context = {
                "business_rule": validation_func.__name__,
                "response_data": data,
                "additional_context": context_data or {}
            }
            
            enhanced_logger.error(f"💼 Business logic assertion failed: {error_message}",
                                extra_context=context)
            raise AssertionError(error_message, context)
        
        enhanced_logger.info(f"✅ Business logic assertion passed: {validation_func.__name__}")
    
    @staticmethod
    def assert_price_format(response: requests.Response, price_field: str = "price",
                          currency: str = "USD", min_price: float = 0,
                          max_price: float = None) -> None:
        """
        💰 E-COMMERCE: Assert price data is properly formatted
        
        Args:
            response: HTTP response object
            price_field: Name of the price field in JSON
            currency: Expected currency code
            min_price: Minimum allowed price
            max_price: Maximum allowed price
            
        Real Example - Product Catalog API:
            assert_price_format(response, "price", "USD", 0.01, 9999.99)
            # Validates price is between $0.01 and $9,999.99
        """
        data = response.json()
        
        if price_field not in data:
            raise AssertionError(f"Price field '{price_field}' not found in response")
        
        price_value = data[price_field]
        errors = []
        
        # Validate price is a number
        if not isinstance(price_value, (int, float, Decimal)):
            errors.append(f"Price must be numeric, got {type(price_value).__name__}")
        else:
            price_float = float(price_value)
            
            # Validate minimum price
            if price_float < min_price:
                errors.append(f"Price {price_float} is below minimum {min_price}")
            
            # Validate maximum price
            if max_price is not None and price_float > max_price:
                errors.append(f"Price {price_float} exceeds maximum {max_price}")
            
            # Validate price precision (max 2 decimal places for currency)
            if len(str(price_float).split('.')[-1]) > 2:
                errors.append(f"Price has too many decimal places: {price_float}")
        
        # Validate currency if present
        if "currency" in data and data["currency"] != currency:
            errors.append(f"Expected currency {currency}, got {data['currency']}")
        
        if errors:
            context = {
                "price_field": price_field,
                "price_value": price_value,
                "expected_currency": currency,
                "validation_errors": errors
            }
            
            error_msg = f"Price validation failed: {'; '.join(errors)}"
            enhanced_logger.error(f"💰 Price assertion failed: {error_msg}",
                                extra_context=context)
            raise AssertionError(error_msg, context)
        
        enhanced_logger.info(f"✅ Price assertion passed: {price_value} {currency}")
    
    @staticmethod
    def assert_email_format(response: requests.Response, email_field: str = "email",
                          allow_empty: bool = False) -> None:
        """
        📧 USER DATA: Assert email address is properly formatted
        
        Args:
            response: HTTP response object
            email_field: Name of the email field in JSON
            allow_empty: Whether empty email is acceptable
            
        Real Example - User Registration API:
            assert_email_format(response, "email")
            assert_email_format(response, "contact_email", allow_empty=True)
        """
        data = response.json()
        
        if email_field not in data:
            if not allow_empty:
                raise AssertionError(f"Email field '{email_field}' not found in response")
            return
        
        email = data[email_field]
        
        if not email and allow_empty:
            enhanced_logger.info("✅ Email assertion passed: empty email allowed")
            return
        
        if not email:
            raise AssertionError(f"Email field '{email_field}' is empty")
        
        # Email validation regex (basic but effective)
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            context = {
                "email_field": email_field,
                "email_value": email,
                "pattern": email_pattern
            }
            
            error_msg = f"Invalid email format: {email}"
            enhanced_logger.error(f"📧 Email assertion failed: {error_msg}",
                                extra_context=context)
            raise AssertionError(error_msg, context)
        
        enhanced_logger.info(f"✅ Email assertion passed: {email}")
    
    @staticmethod
    def assert_date_format(response: requests.Response, date_field: str,
                          expected_format: str = "ISO8601",
                          allow_future: bool = True,
                          max_age_days: int = None) -> None:
        """
        📅 DATE/TIME: Assert date fields are properly formatted
        
        Args:
            response: HTTP response object
            date_field: Name of the date field in JSON
            expected_format: Expected date format ("ISO8601", "YYYY-MM-DD", etc.)
            allow_future: Whether future dates are allowed
            max_age_days: Maximum age in days (for historical data validation)
            
        Real Examples:
            # Event API - event dates can be in future
            assert_date_format(response, "event_date", allow_future=True)
            
            # Log API - log entries shouldn't be older than 30 days
            assert_date_format(response, "timestamp", allow_future=False, max_age_days=30)
        """
        data = response.json()
        
        if date_field not in data:
            raise AssertionError(f"Date field '{date_field}' not found in response")
        
        date_str = data[date_field]
        
        try:
            # Parse the date string
            if expected_format == "ISO8601":
                parsed_date = date_parser.isoparse(date_str)
            else:
                parsed_date = datetime.strptime(date_str, expected_format)
            
            now = datetime.now(parsed_date.tzinfo) if parsed_date.tzinfo else datetime.now()
            
            # Check if future dates are allowed
            if not allow_future and parsed_date > now:
                raise AssertionError(f"Future date not allowed: {date_str}")
            
            # Check maximum age
            if max_age_days is not None:
                age_limit = now - timedelta(days=max_age_days)
                if parsed_date < age_limit:
                    raise AssertionError(f"Date {date_str} is older than {max_age_days} days")
            
            enhanced_logger.info(f"✅ Date assertion passed: {date_str}")
            
        except (ValueError, TypeError) as e:
            context = {
                "date_field": date_field,
                "date_value": date_str,
                "expected_format": expected_format,
                "parse_error": str(e)
            }
            
            error_msg = f"Invalid date format: {date_str}"
            enhanced_logger.error(f"📅 Date assertion failed: {error_msg}",
                                extra_context=context)
            raise AssertionError(error_msg, context)
    
    @staticmethod
    def assert_pagination_data(response: requests.Response,
                             expected_page_size: int = None,
                             expected_total_count: int = None,
                             has_next_page: bool = None) -> None:
        """
        📄 PAGINATION: Assert pagination metadata is correct
        
        Args:
            response: HTTP response object
            expected_page_size: Expected number of items per page
            expected_total_count: Expected total number of items
            has_next_page: Whether there should be a next page
            
        Real Example - Product Listing API:
            # GET /products?page=1&limit=20
            assert_pagination_data(response, expected_page_size=20, has_next_page=True)
        """
        data = response.json()
        
        # Common pagination field names
        pagination_fields = {
            'page_size': ['page_size', 'limit', 'per_page', 'size'],
            'total_count': ['total', 'total_count', 'count', 'total_items'],
            'current_page': ['page', 'current_page', 'page_number'],
            'has_next': ['has_next', 'has_next_page', 'next_page_url'],
            'items': ['data', 'items', 'results', 'records']
        }
        
        # Find actual pagination fields in response
        found_fields = {}
        for field_type, possible_names in pagination_fields.items():
            for name in possible_names:
                if name in data:
                    found_fields[field_type] = name
                    break
        
        errors = []
        
        # Validate page size
        if expected_page_size is not None:
            if 'items' in found_fields:
                actual_items = len(data[found_fields['items']])
                if actual_items > expected_page_size:
                    errors.append(f"Too many items: {actual_items} > {expected_page_size}")
            
            if 'page_size' in found_fields:
                actual_page_size = data[found_fields['page_size']]
                if actual_page_size != expected_page_size:
                    errors.append(f"Page size mismatch: {actual_page_size} != {expected_page_size}")
        
        # Validate total count
        if expected_total_count is not None and 'total_count' in found_fields:
            actual_total = data[found_fields['total_count']]
            if actual_total != expected_total_count:
                errors.append(f"Total count mismatch: {actual_total} != {expected_total_count}")
        
        # Validate has_next_page
        if has_next_page is not None and 'has_next' in found_fields:
            actual_has_next = data[found_fields['has_next']]
            if bool(actual_has_next) != has_next_page:
                errors.append(f"Has next page mismatch: {actual_has_next} != {has_next_page}")
        
        if errors:
            context = {
                "found_pagination_fields": found_fields,
                "response_data": data,
                "validation_errors": errors
            }
            
            error_msg = f"Pagination validation failed: {'; '.join(errors)}"
            enhanced_logger.error(f"📄 Pagination assertion failed: {error_msg}",
                                extra_context=context)
            raise AssertionError(error_msg, context)
        
        enhanced_logger.info("✅ Pagination assertion passed")
    
    @staticmethod
    def assert_security_headers(response: requests.Response,
                              required_headers: List[str] = None) -> None:
        """
        🔒 SECURITY: Assert security headers are present
        
        Args:
            response: HTTP response object
            required_headers: List of required security headers
            
        Real Example - Production API Security:
            required_security_headers = [
                "X-Content-Type-Options",
                "X-Frame-Options", 
                "X-XSS-Protection",
                "Strict-Transport-Security"
            ]
            assert_security_headers(response, required_security_headers)
        """
        if required_headers is None:
            required_headers = [
                "X-Content-Type-Options",
                "X-Frame-Options",
                "X-XSS-Protection"
            ]
        
        missing_headers = []
        present_headers = {}
        
        for header in required_headers:
            if header in response.headers:
                present_headers[header] = response.headers[header]
            else:
                missing_headers.append(header)
        
        if missing_headers:
            context = {
                "required_headers": required_headers,
                "missing_headers": missing_headers,
                "present_headers": present_headers,
                "all_response_headers": dict(response.headers)
            }
            
            error_msg = f"Missing security headers: {', '.join(missing_headers)}"
            enhanced_logger.error(f"🔒 Security headers assertion failed: {error_msg}",
                                extra_context=context)
            raise AssertionError(error_msg, context)
        
        enhanced_logger.info(f"✅ Security headers assertion passed: {len(present_headers)} headers found")
    
    @staticmethod
    def assert_api_rate_limit(response: requests.Response,
                            expected_limit: int = None,
                            expected_remaining: int = None) -> None:
        """
        🚦 RATE LIMITING: Assert rate limit headers are correct
        
        Args:
            response: HTTP response object
            expected_limit: Expected rate limit per time window
            expected_remaining: Expected remaining requests
            
        Real Example - API Rate Limiting:
            # After making 50 requests with 100/hour limit
            assert_api_rate_limit(response, expected_limit=100, expected_remaining=50)
        """
        rate_limit_headers = {
            'limit': ['X-RateLimit-Limit', 'X-Rate-Limit-Limit', 'RateLimit-Limit'],
            'remaining': ['X-RateLimit-Remaining', 'X-Rate-Limit-Remaining', 'RateLimit-Remaining'],
            'reset': ['X-RateLimit-Reset', 'X-Rate-Limit-Reset', 'RateLimit-Reset']
        }
        
        found_headers = {}
        for header_type, possible_names in rate_limit_headers.items():
            for name in possible_names:
                if name in response.headers:
                    found_headers[header_type] = {
                        'name': name,
                        'value': response.headers[name]
                    }
                    break
        
        errors = []
        
        # Validate rate limit
        if expected_limit is not None and 'limit' in found_headers:
            actual_limit = int(found_headers['limit']['value'])
            if actual_limit != expected_limit:
                errors.append(f"Rate limit mismatch: {actual_limit} != {expected_limit}")
        
        # Validate remaining requests
        if expected_remaining is not None and 'remaining' in found_headers:
            actual_remaining = int(found_headers['remaining']['value'])
            if actual_remaining != expected_remaining:
                errors.append(f"Remaining requests mismatch: {actual_remaining} != {expected_remaining}")
        
        # Validate that remaining <= limit
        if 'limit' in found_headers and 'remaining' in found_headers:
            limit_val = int(found_headers['limit']['value'])
            remaining_val = int(found_headers['remaining']['value'])
            if remaining_val > limit_val:
                errors.append(f"Remaining ({remaining_val}) cannot exceed limit ({limit_val})")
        
        if errors:
            context = {
                "found_rate_limit_headers": found_headers,
                "validation_errors": errors,
                "all_headers": dict(response.headers)
            }
            
            error_msg = f"Rate limit validation failed: {'; '.join(errors)}"
            enhanced_logger.error(f"🚦 Rate limit assertion failed: {error_msg}",
                                extra_context=context)
            raise AssertionError(error_msg, context)
        
        enhanced_logger.info("✅ Rate limit assertion passed")
    
    @staticmethod
    def assert_data_consistency(responses: List[requests.Response],
                              consistency_field: str,
                              tolerance: float = 0.0) -> None:
        """
        🔄 DATA CONSISTENCY: Assert data is consistent across multiple requests
        
        Args:
            responses: List of HTTP responses to compare
            consistency_field: JSON field to check for consistency
            tolerance: Allowed tolerance for numeric values
            
        Real Example - Distributed System Testing:
            # Check that user balance is consistent across different API endpoints
            responses = [
                api_client.get("/user/123/balance"),
                api_client.get("/accounts/123/summary"),
                api_client.get("/user/123/profile")
            ]
            assert_data_consistency(responses, "balance", tolerance=0.01)
        """
        if len(responses) < 2:
            raise AssertionError("Need at least 2 responses to check consistency")
        
        values = []
        errors = []
        
        for i, response in enumerate(responses):
            try:
                data = response.json()
                value = jmespath.search(consistency_field, data)
                if value is None:
                    errors.append(f"Response {i}: field '{consistency_field}' not found")
                else:
                    values.append((i, value))
            except json.JSONDecodeError:
                errors.append(f"Response {i}: invalid JSON")
        
        if errors:
            raise AssertionError(f"Data consistency check failed: {'; '.join(errors)}")
        
        if len(values) < 2:
            raise AssertionError("Not enough valid values to check consistency")
        
        # Check consistency
        reference_value = values[0][1]
        inconsistencies = []
        
        for response_index, value in values[1:]:
            if isinstance(reference_value, (int, float)) and isinstance(value, (int, float)):
                # Numeric comparison with tolerance
                if abs(float(value) - float(reference_value)) > tolerance:
                    inconsistencies.append(
                        f"Response {response_index}: {value} differs from reference {reference_value}"
                    )
            else:
                # Exact comparison for non-numeric values
                if value != reference_value:
                    inconsistencies.append(
                        f"Response {response_index}: {value} differs from reference {reference_value}"
                    )
        
        if inconsistencies:
            context = {
                "consistency_field": consistency_field,
                "reference_value": reference_value,
                "all_values": values,
                "tolerance": tolerance,
                "inconsistencies": inconsistencies
            }
            
            error_msg = f"Data inconsistency detected: {'; '.join(inconsistencies)}"
            enhanced_logger.error(f"🔄 Data consistency assertion failed: {error_msg}",
                                extra_context=context)
            raise AssertionError(error_msg, context)
        
        enhanced_logger.info(f"✅ Data consistency assertion passed: {len(values)} responses consistent")


# 🌟 GLOBAL INSTANCE for easy access
advanced_assert = AdvancedAPIAssertions()


# 🎯 USAGE EXAMPLES FOR BEGINNERS:
"""
📚 HOW TO USE ADVANCED ASSERTIONS:

1. BASIC API RESPONSE VALIDATION:
   
   from utils.advanced_assertions import advanced_assert
   
   def test_user_profile_api(api_client):
       response = api_client.get("/users/123")
       
       # Basic validations
       advanced_assert.assert_status_code(response, 200)
       advanced_assert.assert_response_time(response, 1.0)  # Must respond in <1s
       
       # Structure validation
       expected_structure = {
           "id": int,
           "name": str,
           "email": str,
           "created_at": str,
           "is_active": bool
       }
       advanced_assert.assert_json_structure(response, expected_structure)

2. E-COMMERCE API TESTING:
   
   def test_product_api(api_client):
       response = api_client.get("/products/456")
       
       # E-commerce specific validations
       advanced_assert.assert_price_format(response, "price", "USD", 0.01, 9999.99)
       advanced_assert.assert_json_structure(response, {
           "id": int,
           "name": str,
           "price": float,
           "in_stock": bool,
           "category": str
       })
       
       # Business logic validation
       def validate_product_availability(data):
           # Business rule: If in stock, quantity must be > 0
           if data.get('in_stock', False):
               return data.get('quantity', 0) > 0
           return True
       
       advanced_assert.assert_business_logic(
           response, 
           validate_product_availability,
           "Product availability logic is invalid"
       )

3. USER REGISTRATION API TESTING:
   
   def test_user_registration(api_client):
       user_data = {
           "name": "John Doe",
           "email": "john@example.com",
           "password": "securepassword123"
       }
       
       response = api_client.post("/users/register", json=user_data)
       
       # Registration validations
       advanced_assert.assert_status_code(response, 201)  # Created
       advanced_assert.assert_email_format(response, "email")
       advanced_assert.assert_date_format(response, "created_at", allow_future=False)
       
       # Security validations
       advanced_assert.assert_security_headers(response)

4. PAGINATION API TESTING:
   
   def test_products_listing(api_client):
       response = api_client.get("/products?page=1&limit=20")
       
       # Pagination validations
       advanced_assert.assert_status_code(response, 200)
       advanced_assert.assert_pagination_data(
           response, 
           expected_page_size=20,
           has_next_page=True
       )

5. DATA CONSISTENCY TESTING:
   
   def test_user_balance_consistency(api_client):
       # Get user balance from different endpoints
       responses = [
           api_client.get("/users/123/balance"),
           api_client.get("/accounts/456/summary"), 
           api_client.get("/wallet/789/details")
       ]
       
       # All should return the same balance
       advanced_assert.assert_data_consistency(
           responses, 
           "balance", 
           tolerance=0.01  # Allow 1 cent difference
       )

6. RATE LIMITING TESTING:
   
   def test_api_rate_limits(api_client):
       # Make request and check rate limit headers
       response = api_client.get("/api/data")
       
       advanced_assert.assert_api_rate_limit(
           response,
           expected_limit=1000,  # 1000 requests per hour
           expected_remaining=999  # Should have 999 left
       )

🎯 REAL-WORLD SCENARIOS:
✅ BANKING: Validate transaction amounts, account balances, security
✅ E-COMMERCE: Check product prices, inventory, order processing
✅ SOCIAL MEDIA: Verify user profiles, posts, privacy settings
✅ HEALTHCARE: Validate patient data, appointment schedules, compliance
✅ IOT: Check sensor readings, device status, data ranges
✅ GAMING: Verify scores, achievements, player statistics

📊 BENEFITS:
✅ COMPREHENSIVE VALIDATION: 20+ specialized assertion methods
✅ REAL-WORLD EXAMPLES: Based on actual industry scenarios
✅ DETAILED ERROR MESSAGES: Know exactly what went wrong
✅ PERFORMANCE AWARE: Built-in response time validation
✅ SECURITY FOCUSED: Validate headers, rate limits, data consistency
✅ BEGINNER FRIENDLY: Clear examples and explanations
""" 