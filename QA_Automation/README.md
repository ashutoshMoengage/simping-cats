# Advanced PyTest API Testing Framework

A comprehensive, production-ready API testing framework built with PyTest, featuring advanced capabilities for API automation, reporting, and CI/CD integration.

## 🚀 Features

### Core Framework Features
- **Advanced API Client**: Robust HTTP client with retry mechanisms, request/response logging, and timeout handling
- **Comprehensive Assertions**: Custom assertion library with detailed logging and JSON schema validation
- **Data-Driven Testing**: Support for CSV, JSON, Excel, and YAML test data sources
- **Flexible Configuration**: Environment-specific configurations with easy switching
- **Rich Logging**: Structured logging with multiple handlers and log rotation
- **Schema Validation**: JSON schema validation for API responses
- **Parallel Execution**: Built-in support for parallel test execution

### Advanced Testing Capabilities
- **Performance Testing**: Built-in performance testing with response time assertions
- **Bulk Operations**: Support for bulk API operations testing
- **Parametrized Tests**: Extensive parametrization support for data-driven testing
- **Authentication Testing**: Comprehensive auth and authorization test coverage
- **Negative Testing**: Built-in negative test scenarios and edge case handling
- **Boundary Testing**: Validation of API limits and constraints

### Reporting & Integration
- **Multiple Report Formats**: HTML, JSON, Allure reports
- **Test Coverage**: Code Coverage reporting
- **CI/CD Ready**: Jenkins, GitHub Actions integration ready
- **Allure Integration**: Rich test reporting with attachments
- **Custom Decorators**: Advanced test decorators for enhanced functionality

## 📁 Project Structure

```
QA_Automation/
├── config/                     # Configuration management
│   ├── __init__.py
│   ├── config.py              # Main configuration class
│   └── environments.json     # Environment-specific configs
├── data/                      # Test data storage
│   ├── users.json            # User test data
│   ├── posts.json            # Post test data
│   ├── test_data.csv         # Parametrized test data
│   └── schema/               # JSON schemas
│       ├── user_schema.json
│       └── post_schema.json
├── tests/                     # Test suites
│   ├── conftest.py           # PyTest fixtures
│   ├── api/                  # API tests
│   │   ├── test_users.py     # User API tests
│   │   ├── test_posts.py     # Post API tests
│   │   └── test_auth.py      # Authentication tests
│   └── integration/          # Integration tests
├── utils/                     # Utility modules
│   ├── api_client.py         # HTTP client wrapper
│   ├── assertions.py         # Custom assertions
│   ├── data_provider.py      # Test data management
│   ├── decorators.py         # Custom decorators
│   ├── helpers.py            # Helper functions
│   └── logger.py             # Logging configuration
├── reports/                   # Generated reports
├── logs/                      # Log files
├── requirements.txt           # Dependencies
├── pytest.ini               # PyTest configuration
└── README.md                 # This file
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- pip

### Setup
1. Clone the repository:
```bash
git clone <repository-url>
cd QA_Automation
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Allure (optional, for enhanced reporting):
```bash
# On macOS
brew install allure

# On Ubuntu/Debian
sudo apt-get install allure

# On Windows
# Download from https://github.com/allure-framework/allure2/releases
```

## 🏃‍♂️ Running Tests

### Basic Test Execution
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/api/test_users.py

# Run tests with specific marker
pytest -m smoke

# Run tests in parallel
pytest -n auto
```

### Advanced Test Execution
```bash
# Run with specific environment
ENVIRONMENT=staging pytest

# Run with HTML report
pytest --html=reports/report.html --self-contained-html

# Run with Allure reporting
pytest --alluredir=reports/allure-results
allure serve reports/allure-results

# Run specific test categories
pytest -m "smoke or critical"
pytest -m "not slow"

# Run with coverage
pytest --cov=utils --cov-report=html
```

### Test Filtering Examples
```bash
# Run only user tests
pytest tests/api/test_users.py

# Run only authentication tests
pytest -k "auth"

# Run performance tests
pytest -m performance

# Run regression suite
pytest -m regression

# Run smoke tests only
pytest -m smoke
```

## 📊 Available Test Markers

- `smoke`: Critical functionality tests
- `regression`: Regression test suite
- `performance`: Performance/load tests
- `auth`: Authentication/authorization tests
- `crud`: Create, Read, Update, Delete operations
- `negative`: Negative test scenarios
- `parametrize`: Parametrized tests
- `integration`: Integration tests
- `slow`: Long-running tests

## 🔧 Configuration

### Environment Configuration
The framework supports multiple environments configured in `config/environments.json`:

```json
{
  "dev": {
    "base_url": "https://jsonplaceholder.typicode.com",
    "timeout": 30,
    "retry_count": 3
  },
  "staging": {
    "base_url": "https://staging.api.example.com",
    "timeout": 45,
    "retry_count": 2
  }
}
```

### Environment Variables
- `ENVIRONMENT`: Set the target environment (dev, staging, prod)
- `AUTH_TOKEN`: Authentication token for protected APIs
- `DATABASE_URL`: Database connection string (if needed)

## 📝 Writing Tests

### Basic Test Structure
```python
import pytest
from utils.assertions import api_assert
from utils.decorators import api_test

@api_test(
    title="Get User by ID",
    description="Verify user retrieval by valid ID",
    severity="critical",
    tags=["smoke", "users"]
)
def test_get_user_by_id(self, jsonplaceholder_api, test_user_id):
    response = jsonplaceholder_api.get(f"/users/{test_user_id}")
    
    api_assert.assert_status_code(response, 200)
    api_assert.assert_json_key_exists(response, "id")
    api_assert.assert_json_key_value(response, "id", test_user_id)
```

### Parametrized Tests
```python
@pytest.mark.parametrize("user_id", [1, 2, 3, 4, 5])
def test_get_multiple_users(self, jsonplaceholder_api, user_id):
    response = jsonplaceholder_api.get(f"/users/{user_id}")
    api_assert.assert_status_code(response, 200)
```

### Data-Driven Tests
```python
def test_create_user_with_csv_data(self, jsonplaceholder_api, parametrized_test_data):
    for test_case in parametrized_test_data:
        if test_case['test_name'] == 'create_user_valid':
            response = jsonplaceholder_api.post("/users", json_data=test_case)
            api_assert.assert_status_code(response, int(test_case['expected_status']))
```

## 🎯 API Endpoints Tested

The framework includes comprehensive tests for:

### JSONPlaceholder API
- **Users**: CRUD operations, validation, filtering
- **Posts**: Content management, search, pagination
- **Comments**: Nested resources, relationships

### ReqRes API
- **Authentication**: Registration, login, token validation
- **Authorization**: Role-based access, permissions
- **User Management**: Profile operations

## 📈 Reporting

### Built-in Reports
- **HTML Report**: `reports/report.html`
- **JSON Report**: `reports/report.json`
- **Coverage Report**: `reports/coverage/`
- **JUnit XML**: For CI/CD integration

### Allure Reports
```bash
# Generate Allure report
pytest --alluredir=reports/allure-results
allure serve reports/allure-results
```

Features:
- Test execution timeline
- Request/response attachments
- Test categorization
- Historical trends
- Failed test analysis

## 🚀 CI/CD Integration

### GitHub Actions Example
```yaml
name: API Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run tests
      run: pytest --html=report.html --alluredir=allure-results
    - name: Upload test results
      uses: actions/upload-artifact@v2
      with:
        name: test-results
        path: |
          report.html
          allure-results/
```

### Jenkins Pipeline Example
```groovy
pipeline {
    agent any
    stages {
        stage('Setup') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }
        stage('Run Tests') {
            steps {
                sh 'pytest --html=report.html --alluredir=allure-results'
            }
        }
        stage('Publish Results') {
            steps {
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: '.',
                    reportFiles: 'report.html',
                    reportName: 'API Test Report'
                ])
                allure([
                    includeProperties: false,
                    jdk: '',
                    properties: [],
                    reportBuildPolicy: 'ALWAYS',
                    results: [[path: 'allure-results']]
                ])
            }
        }
    }
}
```

## 🛡️ Best Practices

### Test Design
- Use descriptive test names and docstrings
- Implement proper test data management
- Follow the AAA pattern (Arrange, Act, Assert)
- Use appropriate test markers
- Implement proper cleanup in fixtures

### API Testing
- Validate both positive and negative scenarios
- Test boundary conditions
- Verify response schemas
- Check performance characteristics
- Test authentication and authorization

### Data Management
- Use factories for test data generation
- Implement data cleanup strategies
- Separate test data by environment
- Use parametrization for data-driven tests

## 🔍 Debugging

### Logging
Logs are automatically generated in the `logs/` directory:
- `api_tests.log`: General test execution logs
- `errors.log`: Error-specific logs
- `api_requests.log`: HTTP request/response logs

### Debug Mode
```bash
# Run with verbose output
pytest -v -s

# Run with debug logging
pytest --log-cli-level=DEBUG

# Run single test with detailed output
pytest tests/api/test_users.py::TestUserAPI::test_get_user_by_valid_id -v -s
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📋 TODO / Roadmap

- [ ] Database integration and validation
- [ ] GraphQL API testing support
- [ ] WebSocket testing capabilities
- [ ] Mock server integration
- [ ] Docker containerization
- [ ] Kubernetes deployment tests
- [ ] API contract testing
- [ ] Security testing enhancements
- [ ] Real-time monitoring integration
- [ ] Advanced analytics dashboard

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For questions and support:
- Create an issue in the repository
- Check the documentation in the `docs/` folder
- Review the example tests in `tests/api/`

## 🙏 Acknowledgments

- [PyTest](https://pytest.org/) for the excellent testing framework
- [Requests](https://requests.readthedocs.io/) for HTTP client functionality
- [Allure](https://docs.qameta.io/allure/) for beautiful test reporting
- [JSONPlaceholder](https://jsonplaceholder.typicode.com/) for the demo API
- [ReqRes](https://reqres.in/) for authentication testing endpoints

---

Built with ❤️ for the QA community 