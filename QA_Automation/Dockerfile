# 🐳 Advanced API Testing Framework - Production Docker Image
# ================================================================
#
# 📚 FOR BEGINNERS:
# Docker creates a "container" - think of it as a lightweight virtual machine
# that packages your application with everything it needs to run:
# - Python runtime
# - Dependencies (pip packages)
# - Your code
# - Configuration files
#
# 🎯 WHY USE DOCKER?
# ✅ CONSISTENCY: Runs the same on your laptop, servers, and cloud
# ✅ ISOLATION: Won't conflict with other applications
# ✅ SCALABILITY: Easy to run multiple instances
# ✅ DEPLOYMENT: Simple to deploy anywhere
#
# 🚀 MULTI-STAGE BUILD:
# Stage 1: Build dependencies and install packages
# Stage 2: Create minimal runtime image
# This keeps the final image small and secure!

# ========================================
# STAGE 1: BUILD STAGE (Dependencies)
# ========================================
FROM python:3.11-slim as builder

# 📝 Metadata for the image
LABEL maintainer="QA Automation Team <qa@company.com>"
LABEL description="Advanced API Testing Framework with PyTest"
LABEL version="2.0.0"
LABEL documentation="https://github.com/yourcompany/pytest-framework"

# 🔧 Set environment variables for Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 📁 Create app directory
WORKDIR /app

# 🔄 Install system dependencies needed for building Python packages
# These are needed for packages like psycopg2, lxml, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libc6-dev \
    libpq-dev \
    libxml2-dev \
    libxslt1-dev \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 📦 Copy requirements first (for better Docker layer caching)
# Docker caches layers, so if requirements.txt hasn't changed,
# it won't reinstall all packages - saves time!
COPY requirements.txt .

# 🏗️ Install Python dependencies
# --user installs to user directory (more secure)
# --no-warn-script-location suppresses warnings
RUN pip install --user --no-warn-script-location -r requirements.txt

# 📋 Install additional production dependencies
RUN pip install --user \
    gunicorn==21.2.0 \
    prometheus-client==0.18.0 \
    psutil==5.9.6 \
    matplotlib==3.7.2 \
    pandas==2.1.3

# ========================================
# STAGE 2: PRODUCTION STAGE (Runtime)
# ========================================
FROM python:3.11-slim as production

# 🔧 Production environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENVIRONMENT=production \
    LOG_LEVEL=INFO \
    PYTEST_WORKERS=auto \
    ALLURE_VERSION=2.24.0

# 📁 Create app directory and user
WORKDIR /app

# 👤 Create non-root user for security
# Running as root is a security risk in production
RUN groupadd -r pytest && useradd -r -g pytest pytest

# 🔄 Install minimal runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libxml2 \
    libxslt1.1 \
    curl \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# 📦 Copy Python packages from builder stage
COPY --from=builder /root/.local /home/pytest/.local

# 🔧 Install Allure CLI for reporting
RUN wget -q https://github.com/allure-framework/allure2/releases/download/${ALLURE_VERSION}/allure-${ALLURE_VERSION}.tgz \
    && tar -xzf allure-${ALLURE_VERSION}.tgz \
    && mv allure-${ALLURE_VERSION} /opt/allure \
    && ln -s /opt/allure/bin/allure /usr/local/bin/allure \
    && rm allure-${ALLURE_VERSION}.tgz

# 📁 Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/reports /app/data /app/config \
    && chown -R pytest:pytest /app

# 📂 Copy application code
COPY --chown=pytest:pytest . .

# 🔐 Switch to non-root user
USER pytest

# 🔗 Add local Python bin to PATH
ENV PATH="/home/pytest/.local/bin:$PATH"

# 📊 Health check endpoint
# Docker will use this to check if the container is healthy
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health', timeout=5)" || exit 1

# 🚀 Expose ports
# 8080: Web dashboard
# 9090: Prometheus metrics
EXPOSE 8080 9090

# 📋 Default command options
# These can be overridden when running the container
CMD ["python", "-m", "pytest", \
     "--html=reports/docker-report.html", \
     "--self-contained-html", \
     "--alluredir=reports/allure-results", \
     "--json-report", \
     "--json-report-file=reports/test-results.json", \
     "--tb=short", \
     "-v"]

# ========================================
# DEVELOPMENT STAGE (Optional)
# ========================================
FROM production as development

# 🔧 Development environment variables
ENV ENVIRONMENT=development \
    LOG_LEVEL=DEBUG \
    PYTEST_ADDOPTS="-v --tb=long"

# 👤 Switch back to root for development setup
USER root

# 🛠️ Install development tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    vim \
    htop \
    && rm -rf /var/lib/apt/lists/*

# 📦 Install development Python packages
RUN pip install --user \
    pytest-watch==4.2.0 \
    pytest-benchmark==4.0.0 \
    black==23.9.1 \
    flake8==6.1.0 \
    isort==5.12.0 \
    mypy==1.6.1

# 🔄 Install pre-commit hooks for code quality
RUN pip install --user pre-commit==3.5.0

# 🔐 Switch back to pytest user
USER pytest

# 🎯 Development command - watch for changes and re-run tests
CMD ["pytest-watch", "--", \
     "--html=reports/dev-report.html", \
     "--alluredir=reports/allure-results", \
     "-v", \
     "--tb=short"]

# ========================================
# CI/CD STAGE (For automated testing)
# ========================================
FROM production as ci

# 🔧 CI environment variables
ENV ENVIRONMENT=ci \
    LOG_LEVEL=INFO \
    CI=true \
    PYTEST_WORKERS=auto

# 👤 Switch to root for CI setup
USER root

# 🛠️ Install CI tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

# 📦 Install CI Python packages
RUN pip install --user \
    coverage==7.3.2 \
    pytest-cov==4.1.0 \
    pytest-xdist==3.3.1 \
    bandit==1.7.5 \
    safety==2.3.5

# 🔐 Switch back to pytest user
USER pytest

# 🎯 CI command - comprehensive testing with coverage
CMD ["python", "-m", "pytest", \
     "--cov=utils", \
     "--cov=config", \
     "--cov-report=html:reports/coverage", \
     "--cov-report=xml:reports/coverage.xml", \
     "--cov-report=term-missing", \
     "--html=reports/ci-report.html", \
     "--self-contained-html", \
     "--alluredir=reports/allure-results", \
     "--json-report", \
     "--json-report-file=reports/ci-results.json", \
     "--tb=short", \
     "-v", \
     "-n", "auto", \
     "--strict-markers", \
     "--strict-config"]

# ========================================
# USAGE EXAMPLES FOR BEGINNERS:
# ========================================

# 🏗️ BUILD THE IMAGE:
# docker build -t api-testing-framework .
# docker build --target development -t api-testing-framework:dev .
# docker build --target ci -t api-testing-framework:ci .

# 🚀 RUN THE CONTAINER:
# 
# 1. BASIC RUN (Production):
# docker run --rm -v $(pwd)/reports:/app/reports api-testing-framework
#
# 2. DEVELOPMENT MODE:
# docker run --rm -it -v $(pwd):/app -p 8080:8080 api-testing-framework:dev
#
# 3. CI MODE:
# docker run --rm -v $(pwd)/reports:/app/reports api-testing-framework:ci
#
# 4. INTERACTIVE SHELL:
# docker run --rm -it api-testing-framework bash
#
# 5. CUSTOM TEST COMMAND:
# docker run --rm api-testing-framework python -m pytest tests/api/test_users.py -v
#
# 6. WITH ENVIRONMENT VARIABLES:
# docker run --rm -e ENVIRONMENT=dev -e LOG_LEVEL=DEBUG api-testing-framework

# 🌐 DOCKER COMPOSE EXAMPLE:
# Create docker-compose.yml file:
# 
# version: '3.8'
# services:
#   api-tests:
#     build: .
#     volumes:
#       - ./reports:/app/reports
#       - ./logs:/app/logs
#     environment:
#       - ENVIRONMENT=dev
#       - LOG_LEVEL=INFO
#     depends_on:
#       - postgres
#       - redis
#
#   postgres:
#     image: postgres:15
#     environment:
#       POSTGRES_DB: testdb
#       POSTGRES_USER: testuser
#       POSTGRES_PASSWORD: testpass
#     ports:
#       - "5432:5432"
#
#   redis:
#     image: redis:7-alpine
#     ports:
#       - "6379:6379"
#
# Then run: docker-compose up

# 🔧 OPTIMIZATION TIPS:
# 
# 1. MULTI-STAGE BUILD: Keeps final image small (200MB vs 800MB)
# 2. LAYER CACHING: Copy requirements.txt first for better caching
# 3. NON-ROOT USER: Runs as 'pytest' user for security
# 4. HEALTH CHECKS: Docker can monitor container health
# 5. MINIMAL BASE: Uses python:3.11-slim instead of full Ubuntu
# 6. CLEAN APT CACHE: Removes package manager cache to save space

# 🎯 PRODUCTION DEPLOYMENT:
# 
# 1. BUILD AND TAG:
# docker build -t your-registry.com/api-testing-framework:v2.0.0 .
# docker push your-registry.com/api-testing-framework:v2.0.0
#
# 2. KUBERNETES DEPLOYMENT:
# kubectl create deployment api-tests --image=your-registry.com/api-testing-framework:v2.0.0
#
# 3. AWS ECS/FARGATE:
# Use the image in ECS task definitions
#
# 4. AZURE CONTAINER INSTANCES:
# az container create --resource-group myRG --name api-tests --image your-registry.com/api-testing-framework:v2.0.0

# 📊 IMAGE SIZE OPTIMIZATION:
# Base python:3.11-slim: ~45MB
# + Dependencies: ~150MB  
# + Application code: ~5MB
# Total optimized image: ~200MB
# (vs ~800MB with full python:3.11 image)

# 🔒 SECURITY FEATURES:
# ✅ Non-root user execution
# ✅ Minimal system packages
# ✅ No unnecessary tools in production
# ✅ Health checks for monitoring
# ✅ Secrets via environment variables
# ✅ Read-only container filesystem (can be enabled)

# 🎯 BENEFITS FOR TEAMS:
# ✅ CONSISTENT ENVIRONMENT: Same Python version, dependencies everywhere
# ✅ EASY DEPLOYMENT: Works on any Docker-compatible platform  
# ✅ SCALABLE: Can run multiple containers for load testing
# ✅ ISOLATED: Won't interfere with other applications
# ✅ PORTABLE: Runs on laptop, CI/CD, cloud, anywhere
# ✅ VERSION CONTROLLED: Infrastructure as code 