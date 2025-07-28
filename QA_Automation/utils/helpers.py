"""
Helper utilities for API testing framework
"""
import json
import random
import string
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from faker import Faker
from loguru import logger


fake = Faker()


class DataGenerator:
    """Generate test data for API testing"""
    
    @staticmethod
    def random_string(length: int = 10, letters: bool = True, digits: bool = True) -> str:
        """Generate random string"""
        chars = ""
        if letters:
            chars += string.ascii_letters
        if digits:
            chars += string.digits
        
        return ''.join(random.choice(chars) for _ in range(length))
    
    @staticmethod
    def random_email() -> str:
        """Generate random email"""
        return fake.email()
    
    @staticmethod
    def random_phone() -> str:
        """Generate random phone number"""
        return fake.phone_number()
    
    @staticmethod
    def random_name() -> str:
        """Generate random name"""
        return fake.name()
    
    @staticmethod
    def random_address() -> Dict[str, str]:
        """Generate random address"""
        return {
            "street": fake.street_address(),
            "city": fake.city(),
            "state": fake.state(),
            "zipcode": fake.zipcode(),
            "country": fake.country()
        }
    
    @staticmethod
    def random_user_data() -> Dict[str, Any]:
        """Generate random user data"""
        return {
            "name": fake.name(),
            "username": fake.user_name(),
            "email": fake.email(),
            "phone": fake.phone_number(),
            "website": fake.url(),
            "address": DataGenerator.random_address(),
            "company": {
                "name": fake.company(),
                "catchPhrase": fake.catch_phrase(),
                "bs": fake.bs()
            }
        }
    
    @staticmethod
    def random_post_data() -> Dict[str, Any]:
        """Generate random post data"""
        return {
            "title": fake.sentence(nb_words=6),
            "body": fake.paragraph(nb_sentences=5),
            "userId": random.randint(1, 10)
        }
    
    @staticmethod
    def random_comment_data() -> Dict[str, Any]:
        """Generate random comment data"""
        return {
            "name": fake.sentence(nb_words=4),
            "email": fake.email(),
            "body": fake.paragraph(nb_sentences=3)
        }
    
    @staticmethod
    def generate_uuid() -> str:
        """Generate UUID"""
        return str(uuid.uuid4())
    
    @staticmethod
    def future_date(days: int = 30) -> str:
        """Generate future date"""
        future = datetime.now() + timedelta(days=days)
        return future.isoformat()
    
    @staticmethod
    def past_date(days: int = 30) -> str:
        """Generate past date"""
        past = datetime.now() - timedelta(days=days)
        return past.isoformat()


class ResponseValidator:
    """Validate API responses"""
    
    @staticmethod
    def is_valid_json(response_text: str) -> bool:
        """Check if response is valid JSON"""
        try:
            json.loads(response_text)
            return True
        except (json.JSONDecodeError, TypeError):
            return False
    
    @staticmethod
    def has_required_keys(data: Dict[str, Any], required_keys: List[str]) -> bool:
        """Check if data has all required keys"""
        return all(key in data for key in required_keys)
    
    @staticmethod
    def validate_email_format(email: str) -> bool:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_url_format(url: str) -> bool:
        """Validate URL format"""
        import re
        pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
        return bool(re.match(pattern, url))
    
    @staticmethod
    def validate_phone_format(phone: str) -> bool:
        """Validate phone number format (basic)"""
        import re
        # Basic phone validation - can be customized based on requirements
        pattern = r'^[\+]?[1-9][\d\s\-\(\)\.]{7,15}$'
        return bool(re.match(pattern, phone.replace(' ', '').replace('-', '')))


class APITestHelper:
    """General helper methods for API testing"""
    
    @staticmethod
    def extract_id_from_location_header(response) -> Optional[str]:
        """Extract ID from Location header"""
        location = response.headers.get('Location', '')
        if location:
            # Extract ID from URL like /users/123
            parts = location.strip('/').split('/')
            if parts:
                return parts[-1]
        return None
    
    @staticmethod
    def build_query_string(params: Dict[str, Any]) -> str:
        """Build query string from parameters"""
        if not params:
            return ""
        
        query_parts = []
        for key, value in params.items():
            if isinstance(value, list):
                for item in value:
                    query_parts.append(f"{key}={item}")
            else:
                query_parts.append(f"{key}={value}")
        
        return "&".join(query_parts)
    
    @staticmethod
    def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries"""
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = APITestHelper.deep_merge_dicts(result[key], value)
            else:
                result[key] = value
        
        return result
    
    @staticmethod
    def sanitize_test_data(data: Dict[str, Any], remove_none: bool = True) -> Dict[str, Any]:
        """Sanitize test data by removing None values or empty strings"""
        if not isinstance(data, dict):
            return data
        
        sanitized = {}
        for key, value in data.items():
            if remove_none and value is None:
                continue
            if isinstance(value, dict):
                sanitized[key] = APITestHelper.sanitize_test_data(value, remove_none)
            elif isinstance(value, list):
                sanitized[key] = [
                    APITestHelper.sanitize_test_data(item, remove_none) 
                    if isinstance(item, dict) else item 
                    for item in value
                ]
            else:
                sanitized[key] = value
        
        return sanitized
    
    @staticmethod
    def compare_json_responses(response1, response2, ignore_keys: List[str] = None) -> bool:
        """Compare two JSON responses, optionally ignoring certain keys"""
        ignore_keys = ignore_keys or []
        
        try:
            data1 = response1.json()
            data2 = response2.json()
            
            # Remove ignored keys
            for key in ignore_keys:
                data1.pop(key, None)
                data2.pop(key, None)
            
            return data1 == data2
        except (json.JSONDecodeError, AttributeError):
            return False
    
    @staticmethod
    def wait_for_condition(condition_func, timeout: int = 30, interval: int = 1) -> bool:
        """Wait for a condition to be true with timeout"""
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if condition_func():
                return True
            time.sleep(interval)
        
        return False
    
    @staticmethod
    def log_test_data(test_name: str, data: Dict[str, Any]):
        """Log test data in a formatted way"""
        logger.info(f"📋 Test data for {test_name}:")
        logger.info(json.dumps(data, indent=2, default=str))
    
    @staticmethod
    def create_test_summary(test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a summary of test results"""
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results if result.get('status') == 'passed')
        failed_tests = total_tests - passed_tests
        
        avg_response_time = 0
        if test_results:
            response_times = [result.get('response_time', 0) for result in test_results]
            avg_response_time = sum(response_times) / len(response_times)
        
        summary = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "pass_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "average_response_time": avg_response_time,
            "timestamp": datetime.now().isoformat()
        }
        
        return summary


class DatabaseHelper:
    """Helper methods for database operations (if needed)"""
    
    @staticmethod
    def setup_test_data():
        """Setup test data in database"""
        # This would be implemented based on your database needs
        logger.info("🗄️ Setting up test data in database")
        pass
    
    @staticmethod
    def cleanup_test_data():
        """Cleanup test data from database"""
        # This would be implemented based on your database needs
        logger.info("🧹 Cleaning up test data from database")
        pass
    
    @staticmethod
    def verify_database_state(expected_state: Dict[str, Any]) -> bool:
        """Verify database state matches expected state"""
        # This would be implemented based on your database needs
        logger.info("🔍 Verifying database state")
        return True


# Global instances for easy access
data_gen = DataGenerator()
response_validator = ResponseValidator()
test_helper = APITestHelper()
db_helper = DatabaseHelper() 