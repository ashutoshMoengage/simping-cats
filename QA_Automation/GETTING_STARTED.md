# 🚀 Getting Started with the Advanced PyTest API Testing Framework

Welcome to the most comprehensive API testing framework designed for both **beginners** and **enterprise** use! 

## 📋 Table of Contents
- [🎯 Quick Start (5 Minutes)](#-quick-start-5-minutes)
- [🏗️ Framework Architecture](#️-framework-architecture)
- [🔧 Installation & Setup](#-installation--setup)
- [📚 Your First API Test](#-your-first-api-test)
- [🎨 Customizing for Your API](#-customizing-for-your-api)
- [📊 Understanding Reports](#-understanding-reports)
- [🚀 CI/CD Integration](#-cicd-integration)
- [💡 Best Practices](#-best-practices)
- [🆘 Troubleshooting](#-troubleshooting)

---

## 🎯 Quick Start (5 Minutes)

### 1. **Clone and Setup**
```bash
# Clone the framework
git clone <your-repo-url>
cd QA_Automation

# Install dependencies
pip install -r requirements.txt

# Verify setup
python demo.py
```

### 2. **Run Your First Test**
```bash
# Run smoke tests (quick validation)
pytest -m smoke

# Run all tests with beautiful HTML report
pytest --html=reports/my-first-report.html --self-contained-html
```

### 3. **View Results**
- Open `reports/my-first-report.html` in your browser
- Check `logs/pytest.log` for detailed logs
- View Allure report: `allure serve reports/allure-results`

**🎉 Congratulations! You've run your first enterprise-grade API tests!**

---

## 🏗️ Framework Architecture

Our framework follows **professional OOP principles** and **enterprise patterns**:

```
QA_Automation/
├── 🔧 config/                    # Configuration management
│   ├── config.py                 # Centralized config class
│   └── environments.json         # Multi-environment settings
├── 📊 data/                      # Test data management
│   ├── users.json               # User test scenarios
│   ├── posts.json               # Post test scenarios
│   └── schema/                  # JSON schema validation
├── 🧪 tests/                     # Test suites
│   ├── api/                     # API-specific tests
│   └── conftest.py              # PyTest fixtures
├── 🛠️ utils/                     # Reusable utilities
│   ├── api_client.py            # HTTP client with retry logic
│   ├── assertions.py            # Custom API assertions
│   ├── decorators.py            # Test decorators
│   ├── logger.py                # Advanced logging
│   └── helpers.py               # Utility functions
├── 📋 framework_templates/       # Templates for customization
│   ├── base_client.py           # Abstract base client
│   └── custom_api_template.py   # Your API template
└── 🚀 .github/workflows/        # CI/CD pipeline
```

### 🏆 **OOP Concepts Demonstrated:**

| Concept | Implementation | Benefit |
|---------|---------------|---------|
| **Inheritance** | `BaseAPIClient` → `YourAPIClient` | Code reuse, consistency |
| **Polymorphism** | Different clients implement same methods | Flexibility, extensibility |
| **Encapsulation** | Private methods (`_method`) vs public | Data protection, clean interfaces |
| **Abstraction** | Abstract methods force implementation | Consistent API contracts |

---

## 🔧 Installation & Setup

### **Prerequisites**
- Python 3.9+ (recommended: 3.11)
- Git
- Code editor (VS Code, PyCharm, etc.)

### **Step-by-Step Setup**

#### 1. **Environment Setup**
```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip
```

#### 2. **Install Dependencies**
```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
python -c "import pytest, requests, allure; print('✅ All dependencies installed!')"
```

#### 3. **Configure Your Environment**
```bash
# Copy environment template
cp config/environments.json config/my-environments.json

# Set environment variable
export ENVIRONMENT=dev  # or staging, prod
```

#### 4. **Test Your Setup**
```bash
# Run framework demo
python demo.py

# Expected output:
# ✅ Configuration loaded successfully
# ✅ Logger initialized
# ✅ API client created
# ✅ Basic API call successful
```

#### 5. **IDE Configuration** (Optional but Recommended)

**VS Code Settings** (`.vscode/settings.json`):
```json
{
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["."],
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black"
}
```

---

## 📚 Your First API Test

Let's create your first API test step by step:

### **Step 1: Understanding the Structure**

Every test in our framework follows this pattern:
```python
@api_test(title="Descriptive Test Name")
@attach_request_response
def test_something(self, api_client, test_data):
    # 1. Arrange - Setup test data
    # 2. Act - Make API call
    # 3. Assert - Verify response
```

### **Step 2: Create Your Test File**

Create `tests/api/test_my_first_api.py`:
```python
"""
🧪 My First API Test Suite
==========================

This demonstrates how to write API tests using our framework.
"""

import pytest
import allure
from utils.assertions import api_assert
from utils.decorators import api_test, attach_request_response


@allure.epic("My First Tests")
class TestMyFirstAPI:
    """
    📚 BEGINNER'S TEST CLASS
    
    This class shows basic API testing patterns:
    - GET requests (reading data)
    - POST requests (creating data)
    - Response validation
    - Error handling
    """
    
    @api_test(
        title="Get All Users - My First Test",
        description="This test fetches all users and validates the response",
        severity="critical",
        tags=["smoke", "get"]
    )
    @attach_request_response
    def test_get_all_users(self, jsonplaceholder_api):
        """
        🎯 MY FIRST TEST: Get all users
        
        What this test does:
        1. Makes a GET request to /users
        2. Validates the response status is 200
        3. Checks that we received a list of users
        4. Validates the data structure
        """
        
        # 🔥 ACT: Make the API call
        response = jsonplaceholder_api.get("/users")
        
        # ✅ ASSERT: Validate the response
        api_assert.assert_status_code(response, 200)
        api_assert.assert_content_type(response, "application/json")
        
        # Get the JSON data
        users = response.json()
        
        # Validate we have users
        assert isinstance(users, list), "Response should be a list"
        assert len(users) > 0, "Should have at least one user"
        
        # Validate user structure
        first_user = users[0]
        assert "id" in first_user, "User should have an ID"
        assert "name" in first_user, "User should have a name"
        assert "email" in first_user, "User should have an email"
        
        print(f"✅ Successfully retrieved {len(users)} users!")
    
    @api_test(
        title="Create New User - My First POST",
        description="This test creates a new user and validates the response",
        tags=["post", "create"]
    )
    @attach_request_response
    def test_create_user(self, jsonplaceholder_api):
        """
        🎯 MY FIRST POST TEST: Create a new user
        
        What this test does:
        1. Prepares user data
        2. Makes a POST request to create a user
        3. Validates the creation was successful
        4. Checks the returned data
        """
        
        # 🔧 ARRANGE: Prepare test data
        new_user = {
            "name": "John Doe",
            "username": "johndoe",
            "email": "john@example.com",
            "phone": "1-555-123-4567"
        }
        
        # 🔥 ACT: Create the user
        response = jsonplaceholder_api.post("/users", json_data=new_user)
        
        # ✅ ASSERT: Validate creation
        api_assert.assert_status_code(response, 201)  # 201 = Created
        
        created_user = response.json()
        
        # Verify the user was created with our data
        assert created_user["name"] == new_user["name"]
        assert created_user["email"] == new_user["email"]
        assert "id" in created_user, "Created user should have an ID"
        
        print(f"✅ Successfully created user with ID: {created_user['id']}")
    
    @pytest.mark.parametrize("user_id,expected_status", [
        (1, 200),      # Valid user
        (999, 404),    # Non-existent user
        ("abc", 404),  # Invalid ID format
    ])
    @api_test(title="Get User by ID - Parametrized Test")
    def test_get_user_by_id(self, jsonplaceholder_api, user_id, expected_status):
        """
        🎯 PARAMETRIZED TEST: Test different user ID scenarios
        
        This demonstrates how to test multiple scenarios efficiently.
        """
        response = jsonplaceholder_api.get(f"/users/{user_id}")
        api_assert.assert_status_code(response, expected_status)
        
        if expected_status == 200:
            user = response.json()
            assert user["id"] == user_id
            print(f"✅ Found user: {user['name']}")
        else:
            print(f"✅ Correctly handled invalid user ID: {user_id}")
```

### **Step 3: Run Your Test**
```bash
# Run your specific test
pytest tests/api/test_my_first_api.py -v

# Run with HTML report
pytest tests/api/test_my_first_api.py --html=reports/my-first-test.html --self-contained-html

# Run with Allure reporting
pytest tests/api/test_my_first_api.py --alluredir=reports/allure-results
allure serve reports/allure-results
```

---

## 🎨 Customizing for Your API

### **Option 1: Using the Template (Recommended for Beginners)**

1. **Copy the template:**
```bash
cp framework_templates/custom_api_template.py utils/my_api_client.py
```

2. **Customize for your API:**
```python
# Edit utils/my_api_client.py

class MyCompanyAPIClient(BaseAPIClient):
    def __init__(self, api_key: str):
        # 👈 CHANGE: Update your API's base URL
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"  # 👈 CHANGE: Your auth method
        }
        super().__init__("https://api.mycompany.com", headers)  # 👈 CHANGE: Your URL
    
    def authenticate(self, credentials):
        # 👈 IMPLEMENT: Your authentication logic
        api_key = credentials.get('api_key')
        if api_key:
            response = self.get("/user/profile")  # 👈 CHANGE: Your auth test endpoint
            return response.status_code == 200
        return False
    
    def get_health_check_endpoint(self):
        return "/health"  # 👈 CHANGE: Your health endpoint
    
    # 👈 ADD: Your specific API methods
    def get_products(self, category=None):
        params = {"category": category} if category else {}
        return self.get("/products", params=params)
```

3. **Create tests for your API:**
```python
# Create tests/api/test_my_company_api.py
from utils.my_api_client import MyCompanyAPIClient

@allure.epic("My Company API")
class TestMyCompanyAPI:
    def test_get_products(self):
        client = MyCompanyAPIClient(api_key="your-key")
        response = client.get_products()
        api_assert.assert_status_code(response, 200)
```

### **Option 2: Quick Configuration (For Known APIs)**

Add your API to `config/environments.json`:
```json
{
  "dev": {
    "base_url": "https://jsonplaceholder.typicode.com",
    "your_api_url": "https://api.yourcompany.com",
    "your_api_key": "your-api-key-here",
    "timeout": 30
  }
}
```

Then use it in tests:
```python
from config.config import config_instance

def test_your_api():
    api_url = config_instance.config_data.get('your_api_url')
    client = APIClient(api_url)
    # Your test logic here
```

---

## 📊 Understanding Reports

Our framework generates **multiple types of reports** for different audiences:

### **1. HTML Reports** (For Developers)
```bash
pytest --html=reports/test-report.html --self-contained-html
```
- **Purpose:** Quick test overview
- **Audience:** Developers, QA engineers
- **Features:** Pass/fail status, execution time, error details

### **2. Allure Reports** (For Management & Stakeholders)
```bash
pytest --alluredir=reports/allure-results
allure serve reports/allure-results
```
- **Purpose:** Beautiful, interactive reports
- **Audience:** Project managers, stakeholders
- **Features:** Test trends, analytics, screenshots, step-by-step execution

### **3. JSON Reports** (For Automation & CI/CD)
```bash
pytest --json-report --json-report-file=reports/results.json
```
- **Purpose:** Machine-readable results
- **Audience:** CI/CD systems, monitoring tools
- **Features:** Structured data, easy parsing, integration-friendly

### **4. Coverage Reports** (For Code Quality)
```bash
pytest --cov=utils --cov-report=html:reports/coverage
```
- **Purpose:** Code coverage analysis
- **Audience:** Developers, tech leads
- **Features:** Line-by-line coverage, missed code identification

### **📊 Report Examples:**

**Allure Report Features:**
- 📈 **Trends:** See test stability over time
- 🏷️ **Categories:** Organize tests by feature/epic
- ⏱️ **Timeline:** Understand execution flow
- 📝 **Attachments:** Request/response data, logs
- 🎯 **Flaky Tests:** Identify unreliable tests

---

## 🚀 CI/CD Integration

Our framework includes **enterprise-grade CI/CD** configuration:

### **GitHub Actions (Included)**
```yaml
# File: .github/workflows/ci-cd-pipeline.yml
# ✅ Multi-Python version testing
# ✅ Parallel execution
# ✅ Advanced reporting
# ✅ Slack notifications
# ✅ Automatic issue creation on failure
```

### **Jenkins Integration** (Add to Jenkinsfile)
```groovy
pipeline {
    agent any
    
    stages {
        stage('Test') {
            steps {
                sh '''
                    pip install -r requirements.txt
                    pytest --html=reports/report.html --alluredir=reports/allure-results
                '''
            }
        }
        
        stage('Report') {
            steps {
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'reports',
                    reportFiles: 'report.html',
                    reportName: 'API Test Report'
                ])
                
                allure includeProperties: false, 
                       jdk: '', 
                       results: [[path: 'reports/allure-results']]
            }
        }
    }
}
```

### **Setting Up Notifications**

1. **Slack Integration:**
```bash
# Add to GitHub Secrets:
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

2. **Email Notifications:**
```yaml
# Add to CI/CD pipeline
- name: Send Email
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 587
    username: ${{secrets.EMAIL_USERNAME}}
    password: ${{secrets.EMAIL_PASSWORD}}
    subject: Test Results - ${{ github.sha }}
    body: file://reports/email-summary.txt
    to: team@company.com
```

---

## 💡 Best Practices

### **🏗️ Writing Maintainable Tests**

**✅ DO:**
```python
@api_test(title="Create Product - Valid Data", tags=["smoke", "product"])
def test_create_product_valid_data(self, api_client, valid_product_data):
    """Clear, descriptive test that tests one thing"""
    response = api_client.post("/products", json_data=valid_product_data)
    api_assert.assert_status_code(response, 201)
    api_assert.assert_json_schema(response, product_schema)
```

**❌ DON'T:**
```python
def test_products(self, api_client):
    """Vague test that tests everything"""
    # Creates product
    response1 = api_client.post("/products", json_data={...})
    # Updates product
    response2 = api_client.put("/products/1", json_data={...})
    # Deletes product
    response3 = api_client.delete("/products/1")
    # Too many responsibilities!
```

### **📊 Test Organization**

**File Structure:**
```
tests/
├── api/
│   ├── test_users.py          # User-related tests
│   ├── test_products.py       # Product-related tests
│   └── test_orders.py         # Order-related tests
├── integration/               # Cross-service tests
└── performance/               # Load tests
```

**Test Naming Convention:**
```python
def test_[action]_[resource]_[condition]_[expected_result]:
    # Examples:
    def test_get_user_valid_id_returns_user_data()
    def test_create_product_missing_name_returns_400()
    def test_delete_order_unauthorized_returns_401()
```

### **🔧 Configuration Management**

**Environment-Specific Settings:**
```python
# config/environments.json
{
    "dev": {
        "base_url": "https://api-dev.company.com",
        "timeout": 30,
        "retry_count": 3
    },
    "staging": {
        "base_url": "https://api-staging.company.com",  
        "timeout": 15,
        "retry_count": 1
    },
    "prod": {
        "base_url": "https://api.company.com",
        "timeout": 10,
        "retry_count": 0  # No retries in prod
    }
}
```

### **📝 Documentation Standards**

**Docstring Template:**
```python
def test_create_user_valid_data(self, api_client, user_data):
    """
    🎯 Test user creation with valid data
    
    **Scenario:** Admin creates a new user with all required fields
    **Expected:** User is created successfully with 201 status
    
    **Test Steps:**
    1. Prepare valid user data
    2. Send POST request to /users
    3. Validate 201 status code
    4. Verify user data in response
    5. Confirm user can be retrieved
    
    **Dependencies:** None
    **Test Data:** Valid user data from fixtures
    """
```

---

## 🆘 Troubleshooting

### **Common Issues & Solutions**

#### **1. Import Errors**
```bash
# Error: ModuleNotFoundError: No module named 'utils'
# Solution: Run from project root
cd QA_Automation
pytest tests/
```

#### **2. Missing Dependencies**
```bash
# Error: ModuleNotFoundError: No module named 'loguru'
# Solution: Install requirements
pip install -r requirements.txt
```

#### **3. Configuration Issues**
```bash
# Error: KeyError: 'base_url'
# Solution: Check environment configuration
export ENVIRONMENT=dev
python -c "from config.config import config_instance; print(config_instance.base_url)"
```

#### **4. API Connection Issues**
```python
# Error: requests.exceptions.ConnectionError
# Solution: Check API availability and network
import requests
response = requests.get("https://jsonplaceholder.typicode.com/users")
print(f"Status: {response.status_code}")
```

#### **5. Test Discovery Issues**
```bash
# Error: No tests found
# Solution: Check test file naming
# Files must start with 'test_' or end with '_test.py'
mv my_tests.py test_my_tests.py
```

### **Debug Mode**

Enable detailed logging:
```bash
# Set log level to DEBUG
export LOG_LEVEL=DEBUG
pytest tests/ -v -s --log-cli-level=DEBUG
```

### **Performance Issues**

Speed up test execution:
```bash
# Run tests in parallel
pip install pytest-xdist
pytest -n auto

# Run only failed tests
pytest --lf

# Run only smoke tests
pytest -m smoke
```

---

## 🎓 Next Steps

### **For Beginners:**
1. ✅ Run the demo script: `python demo.py`
2. ✅ Execute existing tests: `pytest -m smoke`
3. ✅ Create your first test using the template
4. ✅ Customize for your API
5. ✅ Set up CI/CD pipeline

### **For Advanced Users:**
1. 🚀 Implement custom decorators
2. 🚀 Add database validation
3. 🚀 Create performance benchmarks
4. 🚀 Integrate with monitoring tools
5. 🚀 Build custom reporting dashboards

### **Learning Resources:**
- 📚 [PyTest Documentation](https://pytest.org/)
- 📚 [Requests Library Guide](https://requests.readthedocs.io/)
- 📚 [Allure Framework](https://docs.qameta.io/allure/)
- 📚 [API Testing Best Practices](https://github.com/public-apis/public-apis)

---

## 🤝 Contributing

Found a bug? Want to add a feature? We welcome contributions!

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Add tests for your changes
5. Run the test suite: `pytest`
6. Commit your changes: `git commit -m 'Add amazing feature'`
7. Push to the branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

---

## 📞 Support

Need help? Here's how to get support:

1. 📖 **Documentation:** Check this guide and the README
2. 🐛 **Issues:** Open a GitHub issue for bugs
3. 💡 **Feature Requests:** Use GitHub discussions
4. 🗣️ **Questions:** Stack Overflow with tag `pytest-api-framework`

---

**🎉 Happy Testing! You're now ready to build enterprise-grade API tests!** 