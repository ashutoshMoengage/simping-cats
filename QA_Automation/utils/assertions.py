"""
Custom assertions for API testing with detailed logging
"""
import json
import time
from typing import Dict, Any, List, Union, Optional
from jsonschema import validate, ValidationError
from deepdiff import DeepDiff
import jmespath
from loguru import logger


class APIAssertions:
    """
    Advanced assertion utilities for API testing
    """
    
    @staticmethod
    def assert_status_code(response, expected_code: int, message: str = None):
        """Assert response status code"""
        actual_code = response.status_code
        assertion_msg = message or f"Expected status code {expected_code}, got {actual_code}"
        
        logger.info(f"🔍 Asserting status code: {expected_code}")
        assert actual_code == expected_code, assertion_msg
        logger.info(f"✅ Status code assertion passed: {actual_code}")
    
    @staticmethod
    def assert_status_code_in(response, expected_codes: List[int], message: str = None):
        """Assert response status code is in list of expected codes"""
        actual_code = response.status_code
        assertion_msg = message or f"Expected status code in {expected_codes}, got {actual_code}"
        
        logger.info(f"🔍 Asserting status code in: {expected_codes}")
        assert actual_code in expected_codes, assertion_msg
        logger.info(f"✅ Status code assertion passed: {actual_code}")
    
    @staticmethod
    def assert_response_time(response_time: float, max_time: float, message: str = None):
        """Assert response time is within acceptable limit"""
        assertion_msg = message or f"Response time {response_time:.3f}s exceeded limit {max_time}s"
        
        logger.info(f"🔍 Asserting response time: {response_time:.3f}s <= {max_time}s")
        assert response_time <= max_time, assertion_msg
        logger.info(f"✅ Response time assertion passed: {response_time:.3f}s")
    
    @staticmethod
    def assert_json_schema(response, schema: Dict[str, Any], message: str = None):
        """Assert response JSON matches schema"""
        try:
            response_data = response.json()
            logger.info("🔍 Validating JSON schema")
            validate(instance=response_data, schema=schema)
            logger.info("✅ JSON schema validation passed")
        except ValidationError as e:
            assertion_msg = message or f"Schema validation failed: {e.message}"
            logger.error(f"❌ Schema validation failed: {e.message}")
            raise AssertionError(assertion_msg)
        except json.JSONDecodeError:
            assertion_msg = message or "Response is not valid JSON"
            logger.error("❌ Response is not valid JSON")
            raise AssertionError(assertion_msg)
    
    @staticmethod
    def assert_json_key_exists(response, key_path: str, message: str = None):
        """Assert JSON key exists using JMESPath"""
        try:
            response_data = response.json()
            result = jmespath.search(key_path, response_data)
            assertion_msg = message or f"Key '{key_path}' not found in response"
            
            logger.info(f"🔍 Checking if key exists: {key_path}")
            assert result is not None, assertion_msg
            logger.info(f"✅ Key exists assertion passed: {key_path}")
            return result
        except json.JSONDecodeError:
            assertion_msg = message or "Response is not valid JSON"
            logger.error("❌ Response is not valid JSON")
            raise AssertionError(assertion_msg)
    
    @staticmethod
    def assert_json_key_value(response, key_path: str, expected_value: Any, message: str = None):
        """Assert JSON key has expected value"""
        try:
            response_data = response.json()
            actual_value = jmespath.search(key_path, response_data)
            assertion_msg = message or f"Expected '{key_path}' = {expected_value}, got {actual_value}"
            
            logger.info(f"🔍 Asserting key value: {key_path} = {expected_value}")
            assert actual_value == expected_value, assertion_msg
            logger.info(f"✅ Key value assertion passed: {key_path} = {actual_value}")
        except json.JSONDecodeError:
            assertion_msg = message or "Response is not valid JSON"
            logger.error("❌ Response is not valid JSON")
            raise AssertionError(assertion_msg)
    
    @staticmethod
    def assert_json_contains(response, expected_data: Dict[str, Any], message: str = None):
        """Assert response JSON contains expected data (partial match)"""
        try:
            response_data = response.json()
            diff = DeepDiff(expected_data, response_data, ignore_order=True, exclude_paths=['root'])
            
            # Check if expected data is subset of response data
            missing_keys = []
            for key, value in expected_data.items():
                if key not in response_data:
                    missing_keys.append(key)
                elif response_data[key] != value:
                    missing_keys.append(f"{key} (value mismatch)")
            
            assertion_msg = message or f"Response doesn't contain expected data. Missing: {missing_keys}"
            
            logger.info("🔍 Checking if response contains expected data")
            assert not missing_keys, assertion_msg
            logger.info("✅ Contains assertion passed")
        except json.JSONDecodeError:
            assertion_msg = message or "Response is not valid JSON"
            logger.error("❌ Response is not valid JSON")
            raise AssertionError(assertion_msg)
    
    @staticmethod
    def assert_header_exists(response, header_name: str, message: str = None):
        """Assert response header exists"""
        assertion_msg = message or f"Header '{header_name}' not found in response"
        
        logger.info(f"🔍 Checking if header exists: {header_name}")
        assert header_name in response.headers, assertion_msg
        logger.info(f"✅ Header exists assertion passed: {header_name}")
    
    @staticmethod
    def assert_header_value(response, header_name: str, expected_value: str, message: str = None):
        """Assert response header has expected value"""
        actual_value = response.headers.get(header_name)
        assertion_msg = message or f"Expected header '{header_name}' = {expected_value}, got {actual_value}"
        
        logger.info(f"🔍 Asserting header value: {header_name} = {expected_value}")
        assert actual_value == expected_value, assertion_msg
        logger.info(f"✅ Header value assertion passed: {header_name} = {actual_value}")
    
    @staticmethod
    def assert_content_type(response, expected_type: str, message: str = None):
        """Assert response content type"""
        actual_type = response.headers.get('Content-Type', '').split(';')[0]
        assertion_msg = message or f"Expected Content-Type {expected_type}, got {actual_type}"
        
        logger.info(f"🔍 Asserting content type: {expected_type}")
        assert actual_type == expected_type, assertion_msg
        logger.info(f"✅ Content type assertion passed: {actual_type}")
    
    @staticmethod
    def assert_text_contains(response, expected_text: str, case_sensitive: bool = True, message: str = None):
        """Assert response text contains expected string"""
        response_text = response.text
        search_text = expected_text if case_sensitive else expected_text.lower()
        search_in = response_text if case_sensitive else response_text.lower()
        
        assertion_msg = message or f"Text '{expected_text}' not found in response"
        
        logger.info(f"🔍 Checking if text contains: {expected_text}")
        assert search_text in search_in, assertion_msg
        logger.info(f"✅ Text contains assertion passed")
    
    @staticmethod
    def assert_json_array_length(response, key_path: str, expected_length: int, message: str = None):
        """Assert JSON array has expected length"""
        try:
            response_data = response.json()
            array_data = jmespath.search(key_path, response_data)
            
            if array_data is None:
                assertion_msg = f"Array not found at path: {key_path}"
                logger.error(f"❌ {assertion_msg}")
                raise AssertionError(assertion_msg)
            
            if not isinstance(array_data, list):
                assertion_msg = f"Data at path '{key_path}' is not an array"
                logger.error(f"❌ {assertion_msg}")
                raise AssertionError(assertion_msg)
            
            actual_length = len(array_data)
            assertion_msg = message or f"Expected array length {expected_length}, got {actual_length}"
            
            logger.info(f"🔍 Asserting array length: {expected_length}")
            assert actual_length == expected_length, assertion_msg
            logger.info(f"✅ Array length assertion passed: {actual_length}")
        except json.JSONDecodeError:
            assertion_msg = message or "Response is not valid JSON"
            logger.error("❌ Response is not valid JSON")
            raise AssertionError(assertion_msg)
    
    @staticmethod
    def assert_json_types(response, type_mapping: Dict[str, type], message: str = None):
        """Assert JSON field types"""
        try:
            response_data = response.json()
            
            for key_path, expected_type in type_mapping.items():
                value = jmespath.search(key_path, response_data)
                
                if value is None:
                    assertion_msg = f"Key '{key_path}' not found in response"
                    logger.error(f"❌ {assertion_msg}")
                    raise AssertionError(assertion_msg)
                
                actual_type = type(value)
                if not isinstance(value, expected_type):
                    assertion_msg = message or f"Expected '{key_path}' to be {expected_type.__name__}, got {actual_type.__name__}"
                    logger.error(f"❌ Type assertion failed: {key_path}")
                    raise AssertionError(assertion_msg)
                
                logger.info(f"✅ Type assertion passed: {key_path} is {expected_type.__name__}")
        except json.JSONDecodeError:
            assertion_msg = message or "Response is not valid JSON"
            logger.error("❌ Response is not valid JSON")
            raise AssertionError(assertion_msg)


# Global instance for easy access
api_assert = APIAssertions() 