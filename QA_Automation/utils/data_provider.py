"""
Data provider utilities for loading test data from various sources
"""
import json
import csv
import yaml
from pathlib import Path
from typing import Dict, Any, List, Union, Optional
import pandas as pd
from loguru import logger


class DataProvider:
    """
    Comprehensive data provider for loading test data from various sources
    """
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / 'data'
        self.data_dir.mkdir(exist_ok=True)
    
    def load_json(self, filename: str) -> Union[Dict[str, Any], List[Any]]:
        """Load data from JSON file"""
        file_path = self.data_dir / filename
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"📁 Loaded JSON data from {filename}")
                return data
        except FileNotFoundError:
            logger.error(f"❌ JSON file not found: {filename}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in file {filename}: {e}")
            return {}
    
    def load_csv(self, filename: str, as_dict: bool = True) -> List[Union[Dict[str, Any], List[str]]]:
        """Load data from CSV file"""
        file_path = self.data_dir / filename
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if as_dict:
                    reader = csv.DictReader(f)
                    data = list(reader)
                else:
                    reader = csv.reader(f)
                    data = list(reader)
                
                logger.info(f"📁 Loaded CSV data from {filename} ({len(data)} rows)")
                return data
        except FileNotFoundError:
            logger.error(f"❌ CSV file not found: {filename}")
            return []
        except Exception as e:
            logger.error(f"❌ Error reading CSV file {filename}: {e}")
            return []
    
    def load_excel(self, filename: str, sheet_name: str = None) -> List[Dict[str, Any]]:
        """Load data from Excel file"""
        file_path = self.data_dir / filename
        
        try:
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                df = pd.read_excel(file_path)
            
            # Convert DataFrame to list of dictionaries
            data = df.fillna('').to_dict('records')
            logger.info(f"📁 Loaded Excel data from {filename} ({len(data)} rows)")
            return data
        except FileNotFoundError:
            logger.error(f"❌ Excel file not found: {filename}")
            return []
        except Exception as e:
            logger.error(f"❌ Error reading Excel file {filename}: {e}")
            return []
    
    def load_yaml(self, filename: str) -> Union[Dict[str, Any], List[Any]]:
        """Load data from YAML file"""
        file_path = self.data_dir / filename
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                logger.info(f"📁 Loaded YAML data from {filename}")
                return data
        except FileNotFoundError:
            logger.error(f"❌ YAML file not found: {filename}")
            return {}
        except yaml.YAMLError as e:
            logger.error(f"❌ Invalid YAML in file {filename}: {e}")
            return {}
    
    def save_json(self, data: Union[Dict[str, Any], List[Any]], filename: str, indent: int = 2):
        """Save data to JSON file"""
        file_path = self.data_dir / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False, default=str)
                logger.info(f"💾 Saved JSON data to {filename}")
        except Exception as e:
            logger.error(f"❌ Error saving JSON file {filename}: {e}")
    
    def save_csv(self, data: List[Dict[str, Any]], filename: str):
        """Save data to CSV file"""
        if not data:
            logger.warning("⚠️ No data to save to CSV")
            return
        
        file_path = self.data_dir / filename
        
        try:
            fieldnames = data[0].keys()
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
                logger.info(f"💾 Saved CSV data to {filename} ({len(data)} rows)")
        except Exception as e:
            logger.error(f"❌ Error saving CSV file {filename}: {e}")
    
    def load_test_data_by_test_case(self, test_case_name: str) -> Dict[str, Any]:
        """Load test data specific to a test case"""
        # Try to load from JSON first
        json_data = self.load_json(f"{test_case_name}.json")
        if json_data:
            return json_data
        
        # Try to load from YAML
        yaml_data = self.load_yaml(f"{test_case_name}.yaml")
        if yaml_data:
            return yaml_data
        
        logger.warning(f"⚠️ No test data found for test case: {test_case_name}")
        return {}
    
    def get_user_test_data(self, user_type: str = "valid") -> Dict[str, Any]:
        """Get user test data based on type"""
        users_data = self.load_json("users.json")
        
        if isinstance(users_data, dict) and user_type in users_data:
            return users_data[user_type]
        elif isinstance(users_data, list) and users_data:
            return users_data[0]  # Return first user as default
        
        # Return default user data if nothing found
        return {
            "name": "Test User",
            "username": "testuser",
            "email": "test@example.com",
            "phone": "1-555-123-4567",
            "website": "http://example.com"
        }
    
    def get_post_test_data(self, post_type: str = "valid") -> Dict[str, Any]:
        """Get post test data based on type"""
        posts_data = self.load_json("posts.json")
        
        if isinstance(posts_data, dict) and post_type in posts_data:
            return posts_data[post_type]
        elif isinstance(posts_data, list) and posts_data:
            return posts_data[0]  # Return first post as default
        
        # Return default post data if nothing found
        return {
            "title": "Test Post Title",
            "body": "This is a test post body with some content.",
            "userId": 1
        }
    
    def get_parametrized_data(self, filename: str, test_name: str = None) -> List[Dict[str, Any]]:
        """Get parametrized test data for data-driven testing"""
        # Try CSV first for parametrized data
        csv_data = self.load_csv(filename)
        if csv_data:
            if test_name:
                # Filter data by test name if provided
                filtered_data = [row for row in csv_data if row.get('test_name') == test_name]
                return filtered_data if filtered_data else csv_data
            return csv_data
        
        # Try JSON
        json_data = self.load_json(filename)
        if isinstance(json_data, list):
            return json_data
        elif isinstance(json_data, dict) and test_name and test_name in json_data:
            return json_data[test_name]
        
        logger.warning(f"⚠️ No parametrized data found in {filename}")
        return []
    
    def create_dynamic_test_data(self, template: Dict[str, Any], 
                                variations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create dynamic test data by applying variations to a template"""
        test_data_list = []
        
        for variation in variations:
            test_data = template.copy()
            test_data.update(variation)
            test_data_list.append(test_data)
        
        logger.info(f"🔄 Created {len(test_data_list)} dynamic test data entries")
        return test_data_list
    
    def validate_test_data_structure(self, data: Dict[str, Any], 
                                   required_keys: List[str]) -> bool:
        """Validate that test data has required structure"""
        missing_keys = [key for key in required_keys if key not in data]
        
        if missing_keys:
            logger.error(f"❌ Missing required keys in test data: {missing_keys}")
            return False
        
        logger.info("✅ Test data structure validation passed")
        return True
    
    def get_environment_specific_data(self, environment: str) -> Dict[str, Any]:
        """Get environment-specific test data"""
        env_data = self.load_json(f"env_{environment}.json")
        if not env_data:
            # Fallback to default environment data
            env_data = self.load_json("env_default.json")
        
        return env_data or {}
    
    def merge_test_data(self, *data_sources: Dict[str, Any]) -> Dict[str, Any]:
        """Merge multiple test data sources"""
        merged_data = {}
        
        for data_source in data_sources:
            if isinstance(data_source, dict):
                merged_data.update(data_source)
        
        logger.info(f"🔄 Merged {len(data_sources)} data sources")
        return merged_data


# Global instance for easy access
data_provider = DataProvider() 