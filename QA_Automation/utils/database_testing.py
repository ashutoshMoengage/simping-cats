"""
🎯 Database Integration Testing Module
======================================

This module provides database integration testing capabilities for API testing.
We'll use REAL examples with SQLite (for beginners) and PostgreSQL (for production).

📚 FOR BEGINNERS:
Database integration testing ensures that your API correctly:
- Stores data in the database
- Retrieves data accurately
- Handles database transactions
- Maintains data integrity

🌟 REAL-WORLD EXAMPLES:
- SQLite: Local testing (no setup required)
- PostgreSQL: Production-like testing
- MongoDB: NoSQL document testing
- Redis: Cache and session testing
"""

import sqlite3
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from contextlib import contextmanager
import threading

# External database libraries
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    print("💡 Install psycopg2 for PostgreSQL support: pip install psycopg2-binary")

try:
    import pymongo
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False
    print("💡 Install pymongo for MongoDB support: pip install pymongo")

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("💡 Install redis for Redis support: pip install redis")

from utils.enhanced_logging import enhanced_logger
from config.config import config_instance


@dataclass
class DatabaseTestResult:
    """
    📊 Database Test Result Data Structure
    
    This represents the result of a database operation test.
    """
    operation: str
    table_name: str
    success: bool
    execution_time: float
    records_affected: int
    error_message: Optional[str] = None
    data_snapshot: Optional[Dict[str, Any]] = None


class SQLiteTester:
    """
    🎯 SQLite Database Tester (Perfect for Beginners!)
    
    SQLite is a file-based database that requires no setup - perfect for learning!
    
    📚 BEGINNER GUIDE:
    SQLite is like a simple database stored in a file. It's perfect for:
    - Learning database concepts
    - Local testing
    - Small applications
    - Prototyping
    
    🚀 REAL EXAMPLE: Testing a User Registration API
    When a user registers via API, we want to verify:
    1. User data is correctly stored in database
    2. Password is properly hashed
    3. Timestamps are accurate
    4. Unique constraints work
    """
    
    def __init__(self, db_path: str = None):
        """
        🚀 Initialize SQLite tester
        
        Args:
            db_path (str): Path to SQLite database file
        """
        self.db_path = db_path or str(Path(__file__).parent.parent / "test_data.db")
        self.connection = None
        
        # Create database and tables if they don't exist
        self._setup_test_database()
        
        enhanced_logger.info(f"🗄️ SQLite tester initialized with database: {self.db_path}")
    
    def _setup_test_database(self):
        """🔧 Create test database schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create users table (common in API testing)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            
            # Create posts table (for testing relationships)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title VARCHAR(200) NOT NULL,
                    content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Create API logs table (for testing API usage tracking)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    endpoint VARCHAR(200) NOT NULL,
                    method VARCHAR(10) NOT NULL,
                    status_code INTEGER NOT NULL,
                    response_time REAL NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        """
        🔗 Get database connection with automatic cleanup
        
        This is a CONTEXT MANAGER that automatically handles database connections.
        It ensures connections are properly closed even if errors occur.
        
        Usage:
            with tester.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users")
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        try:
            yield conn
        finally:
            conn.close()
    
    def verify_user_creation(self, api_response: Dict[str, Any], 
                           expected_user_data: Dict[str, Any]) -> DatabaseTestResult:
        """
        ✅ REAL EXAMPLE: Verify user was created in database after API call
        
        This is what you'd use after calling POST /users API endpoint.
        
        Args:
            api_response (dict): Response from user creation API
            expected_user_data (dict): Data that should be in database
            
        Returns:
            DatabaseTestResult: Test result with verification details
            
        Example Usage:
            # After API call: POST /users {"username": "john", "email": "john@example.com"}
            api_response = {"id": 123, "username": "john", "status": "created"}
            expected_data = {"username": "john", "email": "john@example.com"}
            result = tester.verify_user_creation(api_response, expected_data)
        """
        start_time = time.time()
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get user from database
                user_id = api_response.get('id')
                cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
                db_user = cursor.fetchone()
                
                if not db_user:
                    return DatabaseTestResult(
                        operation="verify_user_creation",
                        table_name="users",
                        success=False,
                        execution_time=time.time() - start_time,
                        records_affected=0,
                        error_message=f"User with ID {user_id} not found in database"
                    )
                
                # Convert sqlite3.Row to dict for easier comparison
                db_user_dict = dict(db_user)
                
                # Verify expected data matches database data
                verification_errors = []
                for key, expected_value in expected_user_data.items():
                    if key in db_user_dict:
                        if db_user_dict[key] != expected_value:
                            verification_errors.append(
                                f"{key}: expected '{expected_value}', got '{db_user_dict[key]}'"
                            )
                    else:
                        verification_errors.append(f"Missing field: {key}")
                
                success = len(verification_errors) == 0
                error_message = "; ".join(verification_errors) if verification_errors else None
                
                enhanced_logger.info(
                    f"✅ User creation verification: {'PASSED' if success else 'FAILED'}",
                    extra_context={"user_id": user_id, "errors": verification_errors}
                )
                
                return DatabaseTestResult(
                    operation="verify_user_creation",
                    table_name="users",
                    success=success,
                    execution_time=time.time() - start_time,
                    records_affected=1,
                    error_message=error_message,
                    data_snapshot=db_user_dict
                )
                
        except Exception as e:
            enhanced_logger.error(f"❌ Database verification failed: {str(e)}")
            return DatabaseTestResult(
                operation="verify_user_creation",
                table_name="users",
                success=False,
                execution_time=time.time() - start_time,
                records_affected=0,
                error_message=str(e)
            )
    
    def log_api_call(self, endpoint: str, method: str, status_code: int, 
                     response_time: float, user_id: int = None) -> DatabaseTestResult:
        """
        📊 REAL EXAMPLE: Log API calls to database for analytics
        
        This demonstrates how APIs often log usage data to databases.
        
        Args:
            endpoint (str): API endpoint called
            method (str): HTTP method
            status_code (int): Response status code
            response_time (float): Response time in seconds
            user_id (int): ID of user who made the call
            
        Returns:
            DatabaseTestResult: Result of database insertion
        """
        start_time = time.time()
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO api_logs (endpoint, method, status_code, response_time, user_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (endpoint, method, status_code, response_time, user_id))
                
                conn.commit()
                log_id = cursor.lastrowid
                
                enhanced_logger.info(
                    f"📊 API call logged to database: {method} {endpoint}",
                    extra_context={"log_id": log_id, "status_code": status_code}
                )
                
                return DatabaseTestResult(
                    operation="log_api_call",
                    table_name="api_logs",
                    success=True,
                    execution_time=time.time() - start_time,
                    records_affected=1,
                    data_snapshot={"id": log_id, "endpoint": endpoint, "method": method}
                )
                
        except Exception as e:
            enhanced_logger.error(f"❌ Failed to log API call: {str(e)}")
            return DatabaseTestResult(
                operation="log_api_call",
                table_name="api_logs",
                success=False,
                execution_time=time.time() - start_time,
                records_affected=0,
                error_message=str(e)
            )
    
    def get_user_posts_count(self, user_id: int) -> DatabaseTestResult:
        """
        📊 REAL EXAMPLE: Verify relationship data after API operations
        
        This checks if user posts are correctly associated after API calls like:
        POST /users/123/posts {"title": "My Post", "content": "Hello World"}
        """
        start_time = time.time()
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) as post_count FROM posts WHERE user_id = ?", (user_id,))
                result = cursor.fetchone()
                post_count = result['post_count']
                
                enhanced_logger.info(f"📊 User {user_id} has {post_count} posts")
                
                return DatabaseTestResult(
                    operation="get_user_posts_count",
                    table_name="posts",
                    success=True,
                    execution_time=time.time() - start_time,
                    records_affected=post_count,
                    data_snapshot={"user_id": user_id, "post_count": post_count}
                )
                
        except Exception as e:
            return DatabaseTestResult(
                operation="get_user_posts_count",
                table_name="posts",
                success=False,
                execution_time=time.time() - start_time,
                records_affected=0,
                error_message=str(e)
            )
    
    def cleanup_test_data(self) -> DatabaseTestResult:
        """🧹 Clean up test data after tests"""
        start_time = time.time()
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Delete test data (be careful in production!)
                tables = ['api_logs', 'posts', 'users']  # Order matters due to foreign keys
                total_deleted = 0
                
                for table in tables:
                    cursor.execute(f"DELETE FROM {table}")
                    total_deleted += cursor.rowcount
                
                conn.commit()
                
                enhanced_logger.info(f"🧹 Cleaned up {total_deleted} test records")
                
                return DatabaseTestResult(
                    operation="cleanup_test_data",
                    table_name="all",
                    success=True,
                    execution_time=time.time() - start_time,
                    records_affected=total_deleted
                )
                
        except Exception as e:
            return DatabaseTestResult(
                operation="cleanup_test_data",
                table_name="all",
                success=False,
                execution_time=time.time() - start_time,
                records_affected=0,
                error_message=str(e)
            )


class PostgreSQLTester:
    """
    🎯 PostgreSQL Database Tester (Production-Grade!)
    
    PostgreSQL is a powerful, production-ready database used by companies like:
    - Instagram (stores billions of photos)
    - Spotify (manages user playlists)
    - Reddit (handles millions of posts)
    
    📚 BEGINNER SETUP:
    1. Install PostgreSQL: https://postgresql.org/download/
    2. Create database: createdb test_api_db
    3. Install Python driver: pip install psycopg2-binary
    4. Update connection string in config
    
    🌍 CLOUD OPTIONS (Free Tiers):
    - Heroku Postgres: https://heroku.com/postgres
    - ElephantSQL: https://elephantsql.com/
    - AWS RDS Free Tier: https://aws.amazon.com/rds/free/
    """
    
    def __init__(self, connection_string: str = None):
        """
        🚀 Initialize PostgreSQL tester
        
        Args:
            connection_string (str): PostgreSQL connection string
                Format: "postgresql://user:password@host:port/database"
                
        Examples:
            # Local PostgreSQL
            "postgresql://username:password@localhost:5432/test_db"
            
            # Heroku PostgreSQL  
            "postgresql://user:pass@host:5432/dbname"
            
            # ElephantSQL (free tier)
            "postgresql://user:pass@raja.db.elephantsql.com:5432/dbname"
        """
        if not POSTGRES_AVAILABLE:
            raise ImportError("PostgreSQL support requires psycopg2. Install with: pip install psycopg2-binary")
        
        self.connection_string = connection_string or self._get_default_connection()
        self._setup_test_database()
        
        enhanced_logger.info("🐘 PostgreSQL tester initialized")
    
    def _get_default_connection(self) -> str:
        """🔧 Get default connection string from config"""
        # Try to get from environment or config
        return (
            config_instance.config_data.get('postgres_url') or
            "postgresql://postgres:password@localhost:5432/test_api_db"
        )
    
    @contextmanager
    def get_connection(self):
        """🔗 Get PostgreSQL connection with automatic cleanup"""
        conn = psycopg2.connect(self.connection_string)
        try:
            yield conn
        finally:
            conn.close()
    
    def _setup_test_database(self):
        """🔧 Create PostgreSQL test schema"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Create users table with PostgreSQL-specific features
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        email VARCHAR(100) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE,
                        metadata JSONB DEFAULT '{}'
                    )
                """)
                
                # Create index for better performance
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_users_email 
                    ON users (email)
                """)
                
                conn.commit()
                enhanced_logger.info("🐘 PostgreSQL test schema created")
                
        except psycopg2.Error as e:
            enhanced_logger.error(f"❌ Failed to setup PostgreSQL: {str(e)}")
            raise
    
    def verify_user_with_json_data(self, user_id: int, 
                                  expected_metadata: Dict[str, Any]) -> DatabaseTestResult:
        """
        🎯 REAL EXAMPLE: Test PostgreSQL's JSONB functionality
        
        PostgreSQL can store and query JSON data efficiently.
        This is common in modern APIs that store flexible user preferences,
        settings, or profile data.
        
        Example API Call:
        PUT /users/123/preferences {"theme": "dark", "notifications": {"email": true}}
        """
        start_time = time.time()
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                
                cursor.execute("""
                    SELECT metadata FROM users WHERE id = %s
                """, (user_id,))
                
                result = cursor.fetchone()
                if not result:
                    return DatabaseTestResult(
                        operation="verify_json_data",
                        table_name="users",
                        success=False,
                        execution_time=time.time() - start_time,
                        records_affected=0,
                        error_message=f"User {user_id} not found"
                    )
                
                stored_metadata = result['metadata']
                
                # Compare JSON data
                matches = True
                for key, expected_value in expected_metadata.items():
                    if stored_metadata.get(key) != expected_value:
                        matches = False
                        break
                
                enhanced_logger.info(
                    f"🐘 JSON data verification: {'PASSED' if matches else 'FAILED'}",
                    extra_context={"expected": expected_metadata, "actual": stored_metadata}
                )
                
                return DatabaseTestResult(
                    operation="verify_json_data",
                    table_name="users",
                    success=matches,
                    execution_time=time.time() - start_time,
                    records_affected=1,
                    data_snapshot={"stored_metadata": stored_metadata}
                )
                
        except Exception as e:
            return DatabaseTestResult(
                operation="verify_json_data",
                table_name="users",
                success=False,
                execution_time=time.time() - start_time,
                records_affected=0,
                error_message=str(e)
            )


class DatabaseTestSuite:
    """
    🎯 Complete Database Testing Suite
    
    This combines SQLite and PostgreSQL testing into a unified interface.
    Perfect for comprehensive database integration testing!
    
    📚 USAGE IN API TESTS:
    
    @pytest.fixture
    def db_tester():
        return DatabaseTestSuite()
    
    def test_user_registration_with_db(api_client, db_tester):
        # 1. Call API
        response = api_client.post("/users", json={"username": "john"})
        
        # 2. Verify in database
        result = db_tester.verify_user_creation(response.json(), {"username": "john"})
        assert result.success, result.error_message
    """
    
    def __init__(self):
        """🚀 Initialize database test suite"""
        self.sqlite_tester = SQLiteTester()
        
        # Only initialize PostgreSQL if available and configured
        self.postgres_tester = None
        if POSTGRES_AVAILABLE:
            try:
                self.postgres_tester = PostgreSQLTester()
                enhanced_logger.info("🎯 Database test suite initialized with SQLite + PostgreSQL")
            except Exception as e:
                enhanced_logger.warning(f"⚠️ PostgreSQL not available: {str(e)}")
                enhanced_logger.info("🎯 Database test suite initialized with SQLite only")
        else:
            enhanced_logger.info("🎯 Database test suite initialized with SQLite only")
    
    def run_comprehensive_test(self, api_response: Dict[str, Any], 
                             expected_data: Dict[str, Any]) -> List[DatabaseTestResult]:
        """
        🎯 Run comprehensive database tests across all available databases
        
        This tests the same data consistency across multiple database types.
        """
        results = []
        
        # Test with SQLite
        sqlite_result = self.sqlite_tester.verify_user_creation(api_response, expected_data)
        results.append(sqlite_result)
        
        # Test with PostgreSQL if available
        if self.postgres_tester:
            # For PostgreSQL, we might test additional features like JSON data
            if 'metadata' in expected_data:
                postgres_result = self.postgres_tester.verify_user_with_json_data(
                    api_response.get('id'), expected_data['metadata']
                )
                results.append(postgres_result)
        
        return results
    
    def generate_database_report(self) -> Dict[str, Any]:
        """📊 Generate comprehensive database testing report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "databases_tested": [],
            "summary": {"total_tests": 0, "passed": 0, "failed": 0}
        }
        
        # Add SQLite info
        report["databases_tested"].append({
            "type": "SQLite",
            "available": True,
            "file_path": self.sqlite_tester.db_path
        })
        
        # Add PostgreSQL info
        report["databases_tested"].append({
            "type": "PostgreSQL", 
            "available": self.postgres_tester is not None,
            "connection_info": "Available" if self.postgres_tester else "Not configured"
        })
        
        return report


# 🌟 GLOBAL INSTANCE for easy access
db_test_suite = DatabaseTestSuite()


# 🎯 USAGE EXAMPLES FOR BEGINNERS:
"""
📚 HOW TO USE DATABASE INTEGRATION TESTING:

1. BASIC SQLITE TESTING (No setup required!):
   
   from utils.database_testing import db_test_suite
   
   def test_user_creation_with_database(api_client):
       # Call your API
       response = api_client.post("/users", json={"username": "testuser", "email": "test@example.com"})
       
       # Verify in database
       result = db_test_suite.sqlite_tester.verify_user_creation(
           response.json(), 
           {"username": "testuser", "email": "test@example.com"}
       )
       
       assert result.success, f"Database verification failed: {result.error_message}"

2. POSTGRESQL TESTING (Production-like):
   
   # First, set up PostgreSQL connection in config/environments.json:
   {
       "dev": {
           "postgres_url": "postgresql://user:pass@localhost:5432/testdb"
       }
   }
   
   def test_user_json_metadata(api_client):
       user_data = {"username": "john", "preferences": {"theme": "dark"}}
       response = api_client.post("/users", json=user_data)
       
       # Test PostgreSQL JSON functionality
       result = db_test_suite.postgres_tester.verify_user_with_json_data(
           response.json()['id'],
           {"theme": "dark"}
       )
       
       assert result.success

3. API USAGE LOGGING:
   
   def test_api_usage_tracking(api_client):
       # Make API call
       response = api_client.get("/users/123")
       
       # Log the API call to database
       result = db_test_suite.sqlite_tester.log_api_call(
           endpoint="/users/123",
           method="GET", 
           status_code=response.status_code,
           response_time=0.5,
           user_id=123
       )
       
       assert result.success

4. CLEANUP AFTER TESTS:
   
   @pytest.fixture(autouse=True)
   def cleanup_database():
       yield  # Run the test
       # Clean up after each test
       db_test_suite.sqlite_tester.cleanup_test_data()

🎯 REAL-WORLD SCENARIOS:
✅ E-commerce: Verify orders are stored correctly
✅ Social Media: Check posts are linked to users
✅ Banking: Ensure transactions are recorded
✅ Analytics: Confirm API usage is tracked
✅ User Management: Validate user data integrity

📊 BENEFITS:
✅ CATCH DATA BUGS: Find issues before production
✅ VERIFY BUSINESS LOGIC: Ensure data relationships work
✅ PERFORMANCE TESTING: Measure database operation speed
✅ COMPLIANCE: Verify data handling requirements
✅ CONFIDENCE: Know your API actually works end-to-end
""" 