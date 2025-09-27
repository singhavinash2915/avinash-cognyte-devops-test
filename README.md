# Currency Converter Application - Production Grade Architecture

A full-stack currency converter application demonstrating modern DevOps practices with separated backend and frontend microservices.

## 🏗️ Architecture Overview

This project follows **production-grade microservices architecture** with clear separation of concerns:

```
currency-converter/
├── application/
│   ├── backend/           # Flask API microservice
│   ├── frontend/          # Static web application  
│   └── tests/            # Integration tests
├── docs/             # Documentation
└── docker/           # Container definitions (future)
```

### **Key Design Decisions:**

1. **Microservices Architecture**: Backend and frontend are completely decoupled
2. **CORS Enabled**: Proper cross-origin resource sharing for API access
3. **Production Ready**: Structured logging, error handling, configuration management
4. **Scalable**: Each service can be deployed and scaled independently

## 🎯 Services

### Backend API (Port 8090)
- **Technology**: Flask + Flask-CORS
- **Purpose**: RESTful API for currency conversion
- **Features**: Health checks, structured logging, error handling
- **Endpoints**: `/health`, `/api/convert`, `/api/rates`, `/api/info`

### Frontend Application (Port 5000)  
- **Technology**: Vanilla JavaScript + Python HTTP Server
- **Purpose**: Static web interface with AJAX integration
- **Features**: Responsive design, real-time API calls, error handling
- **Architecture**: Single Page Application (SPA)

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Virtual environment support

### 1. Setup Environment
```bash
# Clone and enter project directory
cd avinash-cognyte-devops-test

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Start Backend API
```bash
# Install backend dependencies
cd application/backend
pip install -r requirements.txt

# Start API server
python app.py
# Backend available at: http://127.0.0.1:8090
```

### 3. Start Frontend Application
```bash
# In a new terminal, navigate to frontend
cd application/frontend

# Start static file server (default port is now 5000)
python3 server.py
# Frontend available at: http://127.0.0.1:5000
```

### 4. Access Application
- **Frontend UI**: http://127.0.0.1:5000
- **Backend API**: http://127.0.0.1:8090
- **API Health**: http://127.0.0.1:8090/health

## 🔧 API Documentation

### Base URL
```
http://127.0.0.1:8090
```

### Endpoints

#### GET /health
Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "message": "Currency converter API is running",
  "version": "1.0.0",
  "timestamp": "2025-09-26T08:05:18.552695",
  "supported_currencies": ["USD", "EUR", "GBP", "JPY"]
}
```

#### POST /api/convert
Convert between currencies.

**Request:**
```json
{
  "amount": 100,
  "from": "USD",
  "to": "EUR"
}
```

**Response:**
```json
{
  "success": true,
  "original_amount": 100.0,
  "from_currency": "USD",
  "to_currency": "EUR",
  "converted_amount": 85.0,
  "exchange_rate": 0.85,
  "timestamp": "2025-09-26T08:05:18.552695"
}
```

#### GET /api/rates?base=USD
Get exchange rates for a base currency.

#### GET /api/info  
Get API information and available endpoints.

## 🎨 Frontend Features

### Modern Web Application
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Updates**: AJAX calls without page refresh
- **Error Handling**: User-friendly error messages and retry options
- **Loading States**: Visual feedback during API calls
- **Input Validation**: Client-side form validation
- **Accessibility**: Keyboard navigation and screen reader support

### User Interface
- Clean, professional gradient design
- Currency selection with flag emojis
- Swap currencies functionality
- Live API health status indicator
- Formatted number display

## 🛠️ Development Features

### Backend (Production Grade)
- **Structured Logging**: Timestamped logs with levels
- **Error Handling**: Comprehensive error responses
- **CORS Support**: Cross-origin requests enabled
- **Configuration Management**: Environment-based config
- **Request Validation**: Input sanitization and validation
- **Health Monitoring**: Endpoint for service health checks

### Frontend (Modern JavaScript)
- **Modular Architecture**: Separated config, API, and app logic
- **Error Recovery**: Automatic retry mechanisms
- **Configuration Driven**: Easy API endpoint changes
- **Progressive Enhancement**: Works without JavaScript (basic functionality)
- **Performance Optimized**: Minimal dependencies, fast loading

## 📁 Project Structure

```
avinash-cognyte-devops-test/
├── application/               # Main application directory
│   ├── backend/                    # Flask API Service (Port 8090)
│   │   ├── app.py                 # Main Flask application
│   │   └── requirements.txt       # Python dependencies
│   ├── frontend/                  # Static Web Application (Port 5000)
│   │   ├── index.html            # Main HTML page
│   │   ├── server.py             # Static file server
│   │   └── assets/
│   │       ├── css/
│   │       │   └── style.css     # Responsive CSS styles
│   │       └── js/
│   │           ├── config.js     # Configuration management
│   │           ├── api.js        # API service layer
│   │           └── app.js        # Main application logic
│   └── tests/                     # Integration tests
├── instructions.md            # Project requirements (excluded from git)
├── venv/                      # Virtual environment (excluded from git)
└── README.md                 # This file
```

## 🧪 Testing

This application includes comprehensive testing covering unit tests, integration tests, and containerized testing with CI/CD automation.

### **Testing Architecture**
- **Unit Tests**: Individual component testing with pytest
- **Integration Tests**: Full application flow testing
- **Container Tests**: Testing the complete containerized application
- **CI/CD Pipeline**: Automated testing with GitHub Actions

### **Quick Test Commands**

#### **Run All Tests**
```bash
# Run complete test suite
cd application/tests
python run_tests.py --all --coverage --html

# Quick unit tests only
python run_tests.py --quick
```

#### **Specific Test Types**
```bash
# Unit tests only
python run_tests.py --unit --coverage

# Integration tests only  
python run_tests.py --integration

# Setup test environment
python run_tests.py --setup
```

### **Test Structure**
```
application/tests/
├── conftest.py                    # Pytest configuration and fixtures
├── pytest.ini                    # Pytest settings
├── requirements.txt               # Test dependencies
├── run_tests.py                   # Test runner script
├── ci_runner.sh                   # CI/CD automation script
├── test_health_endpoint.py        # Health endpoint unit tests
├── test_convert_endpoint.py       # Conversion endpoint unit tests  
├── test_api_endpoints.py          # Additional API endpoint tests
└── test_integration_containerized.py  # Container integration tests
```

### **Unit Tests**

#### **Prerequisites**
```bash
# Install test dependencies
cd application/tests
pip install -r requirements.txt
```

#### **Health Endpoint Tests**
```bash
# Test health endpoint functionality
pytest test_health_endpoint.py -v

# Expected coverage:
# ✅ HTTP 200 status code
# ✅ JSON response format
# ✅ Required fields (status, version, timestamp)
# ✅ Healthy status reporting
# ✅ API version consistency
# ✅ Supported currencies list
# ✅ Error handling (405 for wrong methods)
```

#### **Conversion Endpoint Tests**
```bash
# Test currency conversion functionality
pytest test_convert_endpoint.py -v

# Expected coverage:
# ✅ Valid currency conversions
# ✅ Same currency conversions (rate = 1.0)
# ✅ Decimal amount handling
# ✅ Zero amount conversions
# ✅ Calculation accuracy
# ✅ Error handling (invalid amounts, currencies)
# ✅ Case insensitive currency codes
# ✅ All supported currency pairs
```

#### **API Endpoints Tests**
```bash
# Test additional API endpoints
pytest test_api_endpoints.py -v

# Expected coverage:
# ✅ Exchange rates endpoint (/api/rates)
# ✅ API info endpoint (/api/info)
# ✅ Error handling across endpoints
# ✅ Cross-endpoint consistency
# ✅ Base currency parameters
```

#### **Run Unit Tests with Coverage**
```bash
# Generate detailed coverage report
pytest -m "unit" --cov=../backend --cov-report=html --cov-report=term-missing

# View coverage report
open htmlcov/index.html  # macOS
# or visit: application/tests/htmlcov/index.html
```

### **Integration Tests**

#### **Container Integration Tests**
```bash
# Run integration tests against containerized app
pytest test_integration_containerized.py -v

# What it tests:
# ✅ Docker image builds successfully
# ✅ Container starts and becomes healthy
# ✅ All API endpoints work in container
# ✅ Frontend serves correctly
# ✅ Static assets load properly
# ✅ Performance benchmarks
# ✅ Concurrent request handling
# ✅ Edge cases (large amounts, zero amounts)
```

#### **Prerequisites for Integration Tests**
```bash
# Ensure Docker is running
docker --version

# Build the application image (will be done automatically)
docker build -t currency-converter .
```

### **CI/CD Automation**

#### **Local CI/CD Testing**
```bash
# Run complete CI/CD pipeline locally
./application/tests/ci_runner.sh

# Available modes:
./application/tests/ci_runner.sh setup       # Setup environment only
./application/tests/ci_runner.sh quality     # Code quality checks
./application/tests/ci_runner.sh unit        # Unit tests only
./application/tests/ci_runner.sh docker      # Docker build and test
./application/tests/ci_runner.sh integration # Integration tests
./application/tests/ci_runner.sh helm        # Helm chart testing
./application/tests/ci_runner.sh quick       # Quick unit tests
./application/tests/ci_runner.sh all         # Complete pipeline (default)
```

#### **GitHub Actions CI/CD**
The project includes a comprehensive GitHub Actions workflow (`.github/workflows/ci.yml`) that automatically:

1. **Code Quality**: flake8, pylint
2. **Security Scanning**: Bandit security linting, Safety vulnerability scanning
3. **Unit Testing**: Comprehensive test suite with coverage
4. **Docker Testing**: Build and test containerized application
5. **Integration Testing**: Full application stack testing
6. **Helm Testing**: Kubernetes deployment testing with Kind
7. **Performance Testing**: Load testing with Apache Bench
8. **Staging Deployment**: Automated deployment on main branch

#### **CI/CD Pipeline Stages**
```yaml
# Trigger: Push to main/develop or Pull Request to main
lint → security → unit-tests → docker-build → integration-tests → helm-test → deploy-staging
                ↘              ↗
                  performance-test (main branch only)
```

### **Test Reports and Coverage**

#### **HTML Test Reports**
```bash
# Generate comprehensive HTML test report
pytest --html=reports/test_report.html --self-contained-html

# Generate with coverage
pytest --cov=../backend --cov-report=html --html=reports/test_report.html
```

#### **Coverage Requirements**
- **Target Coverage**: 90%+ for critical components
- **Health Endpoint**: 100% coverage
- **Conversion Logic**: 100% coverage  
- **Error Handling**: 95%+ coverage
- **API Endpoints**: 90%+ coverage

### **Manual Testing**

#### **Backend API Testing**
```bash
# Health check
curl http://127.0.0.1:8090/health

# Currency conversion
curl -X POST http://127.0.0.1:8090/api/convert \
  -H "Content-Type: application/json" \
  -d '{"amount": 100, "from": "USD", "to": "EUR"}'

# Exchange rates
curl "http://127.0.0.1:8090/api/rates?base=USD"

# API information
curl http://127.0.0.1:8090/api/info
```

#### **Frontend UI Testing**
- Open http://127.0.0.1:5000
- Test currency conversion form
- Verify error handling
- Check responsive design on different screen sizes
- Test accessibility features

#### **Docker Container Testing**
```bash
# Build and test container
docker build -t currency-converter .
docker run -p 8080:8080 currency-converter

# Test container endpoints
curl http://localhost:8080/health
curl http://localhost:8080/
```

### **Performance Testing**

#### **Load Testing**
```bash
# Install Apache Bench (if not available)
sudo apt-get install apache2-utils  # Ubuntu/Debian
brew install apache2-utils          # macOS

# Test health endpoint performance
ab -n 1000 -c 10 http://localhost:8080/health

# Test conversion endpoint performance
ab -n 500 -c 5 -p conversion_data.json -T application/json http://localhost:8080/api/convert
```

#### **Performance Benchmarks**
- **Health Endpoint**: < 50ms average response time
- **Conversion Endpoint**: < 100ms average response time
- **Frontend Loading**: < 2s initial load
- **Container Startup**: < 10s to healthy state

### **Test Environment Setup**

#### **Local Development**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r application/backend/requirements.txt
pip install -r application/tests/requirements.txt
```

#### **Docker Environment**
```bash
# Ensure Docker is running
docker info

# Clean up previous containers (if any)
docker stop currency-converter-test 2>/dev/null || true
docker rm currency-converter-test 2>/dev/null || true
```

### **Troubleshooting Tests**

#### **Common Issues**

1. **Port Already in Use**
   ```bash
   # Find and kill process using port
   lsof -ti:8080 | xargs kill -9
   ```

2. **Docker Build Failures**
   ```bash
   # Clean Docker cache
   docker system prune -f
   docker build --no-cache -t currency-converter .
   ```

3. **Test Dependencies**
   ```bash
   # Reinstall test dependencies
   pip install --upgrade -r application/tests/requirements.txt
   ```

4. **Permission Issues**
   ```bash
   # Make scripts executable
   chmod +x application/tests/run_tests.py
   chmod +x application/tests/ci_runner.sh
   ```

### **Test Coverage Reports**

After running tests with coverage, you can view detailed reports:

- **Terminal Coverage**: Displayed immediately after test run
- **HTML Coverage**: `application/tests/htmlcov/index.html`
- **Test Reports**: `application/tests/reports/test_report.html`

### **Continuous Integration**

The CI/CD pipeline automatically runs on:
- **Push to main/develop**: Full pipeline including deployment
- **Pull Requests**: All tests except deployment
- **Scheduled**: Nightly performance testing (if configured)

**Pipeline Status**: All tests must pass for deployment to proceed.

## 🌍 Supported Currencies

- **USD** 🇺🇸 - US Dollar
- **EUR** 🇪🇺 - Euro  
- **GBP** 🇬🇧 - British Pound
- **JPY** 🇯🇵 - Japanese Yen

*Exchange rates are hardcoded for demonstration purposes. In production, these would be fetched from external APIs.*

## 🚀 Production Deployment Considerations

### Backend API
- **WSGI Server**: Use Gunicorn or uWSGI instead of development server
- **Environment Variables**: Externalize configuration
- **Database**: Add persistent storage for exchange rates
- **Caching**: Implement Redis for exchange rate caching
- **Rate Limiting**: Add API rate limiting
- **Authentication**: Implement API key authentication

### Frontend Application  
- **CDN**: Serve static assets from CDN
- **Build Process**: Add bundling and minification
- **Service Worker**: Add offline support
- **Analytics**: Add user behavior tracking
- **SEO**: Add meta tags and structured data

### Infrastructure
- **Containerization**: Docker containers for each service
- **Orchestration**: Kubernetes deployment manifests
- **Load Balancing**: NGINX or cloud load balancer
- **SSL/TLS**: HTTPS certificates
- **Monitoring**: Prometheus metrics and Grafana dashboards
- **Logging**: Centralized logging with ELK stack

## 💡 Why This Architecture?

### Benefits of Microservices Approach:
1. **Independent Deployment**: Each service can be deployed separately
2. **Technology Flexibility**: Different tech stacks per service
3. **Scalability**: Scale services independently based on load
4. **Team Organization**: Different teams can own different services
5. **Fault Isolation**: Failure in one service doesn't affect others
6. **Development Velocity**: Parallel development of services

### Production Readiness Features:
- Proper error handling and logging
- Health check endpoints for monitoring
- CORS configuration for security
- Structured configuration management
- Input validation and sanitization
- Graceful error recovery

This architecture demonstrates enterprise-grade practices suitable for production deployment in cloud environments.

## 🐳 Docker Containerization

The application is fully containerized using Docker with production-ready configurations.

### **Container Features:**
- **Multi-stage build** for optimized image size
- **Security hardened** with non-root user execution
- **Combined backend + frontend** in single container
- **Health checks** for container monitoring
- **Production environment** configuration

### **Build and Run the Docker Image:**

#### **Prerequisites:**
- Docker installed and running
- Minimum 1GB RAM available
- Port 8080 available

#### **Build the Image:**
```bash
# Clone the repository
git clone https://github.com/singhavinash2915/avinash-cognyte-devops-test.git
cd avinash-cognyte-devops-test

# Build the Docker image
docker build -t currency-converter .
```

#### **Run the Container:**
```bash
# Run in detached mode
docker run -d -p 8080:8080 --name currency-converter currency-converter

# Or run in interactive mode (see logs)
docker run -p 8080:8080 --name currency-converter currency-converter
```

#### **Access the Application:**
- **Frontend UI**: http://localhost:8080
- **API Health Check**: http://localhost:8080/health
- **API Documentation**: http://localhost:8080/api/info

#### **Container Management:**
```bash
# Check container status
docker ps

# View container logs
docker logs currency-converter

# Stop the container
docker stop currency-converter

# Remove the container
docker rm currency-converter

# Remove the image
docker rmi currency-converter
```

#### **Health Check:**
The container includes automatic health monitoring:
```bash
# Check health status
docker inspect --format='{{.State.Health.Status}}' currency-converter

# View health check logs
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' currency-converter
```

#### **Environment Variables:**
You can customize the container with environment variables:
```bash
docker run -d -p 8080:8080 \
  -e PORT=8080 \
  -e HOST=0.0.0.0 \
  -e FLASK_ENV=production \
  --name currency-converter \
  currency-converter
```

#### **Volume Mounting (Optional):**
For persistent logs:
```bash
docker run -d -p 8080:8080 \
  -v $(pwd)/logs:/app/logs \
  --name currency-converter \
  currency-converter
```

### **Docker Image Details:**
- **Base Image**: python:3.11-slim-bookworm
- **Size**: ~150MB (optimized multi-stage build)
- **User**: Non-root (appuser)
- **Working Directory**: /app
- **Exposed Port**: 8080
- **Health Check**: Every 30 seconds

### **Production Deployment:**
For production environments, consider:
```bash
# Run with resource limits
docker run -d \
  --memory=512m \
  --cpus=1.0 \
  -p 8080:8080 \
  --restart=unless-stopped \
  --name currency-converter \
  currency-converter

# With logging configuration
docker run -d \
  -p 8080:8080 \
  --log-driver=json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  --name currency-converter \
  currency-converter
```

## ⎈ Kubernetes Deployment with Helm

The application includes a production-ready Helm chart for Kubernetes deployment with configurable scaling, ingress, and monitoring.

### **Helm Chart Features:**
- **Configurable replica count** for horizontal scaling
- **Service exposure** with multiple service types
- **Optional Ingress** for external access
- **Horizontal Pod Autoscaler** for automatic scaling
- **Pod Disruption Budget** for high availability
- **Health checks** and monitoring ready
- **Security hardened** with non-root containers

### **Prerequisites:**
- Kubernetes cluster (1.19+)
- Helm 3.2.0+
- kubectl configured
- Docker image available: `currency-converter:latest`

### **Install the Helm Chart:**

#### **Quick Start:**
```bash
# Clone the repository
git clone https://github.com/singhavinash2915/avinash-cognyte-devops-test.git
cd avinash-cognyte-devops-test

# Install with default values (3 replicas, ClusterIP service)
helm install currency-converter ./helm/currency-converter
```

#### **Development Environment:**
```bash
# Single replica with NodePort for easy access
helm install currency-converter ./helm/currency-converter \
  --set replicaCount=1 \
  --set service.type=NodePort \
  --set resources.limits.memory=256Mi

# Get NodePort and access the application
kubectl get svc currency-converter
```

#### **Production Environment:**
```bash
# Multiple replicas with autoscaling and ingress
helm install currency-converter ./helm/currency-converter \
  --set replicaCount=5 \
  --set autoscaling.enabled=true \
  --set autoscaling.minReplicas=3 \
  --set autoscaling.maxReplicas=20 \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=currency-converter.example.com
```

#### **With LoadBalancer (Cloud Environments):**
```bash
# Deploy with LoadBalancer service type
helm install currency-converter ./helm/currency-converter \
  --set service.type=LoadBalancer \
  --set replicaCount=3
```

### **Access the Application:**

#### **ClusterIP (Default):**
```bash
# Port forward to access locally
kubectl port-forward svc/currency-converter 8080:80
# Access at: http://localhost:8080
```

#### **NodePort:**
```bash
# Get the NodePort
export NODE_PORT=$(kubectl get svc currency-converter -o jsonpath='{.spec.ports[0].nodePort}')
export NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[0].address}')
echo "http://$NODE_IP:$NODE_PORT"
```

#### **LoadBalancer:**
```bash
# Get the LoadBalancer IP
kubectl get svc currency-converter
# Access at the EXTERNAL-IP shown
```

#### **Ingress:**
```bash
# Access via configured hostname
curl http://currency-converter.example.com
```

### **Configuration Options:**

#### **Scaling Configuration:**
```bash
# Set specific replica count
helm install currency-converter ./helm/currency-converter \
  --set replicaCount=7

# Enable autoscaling
helm install currency-converter ./helm/currency-converter \
  --set autoscaling.enabled=true \
  --set autoscaling.minReplicas=2 \
  --set autoscaling.maxReplicas=15 \
  --set autoscaling.targetCPUUtilizationPercentage=70
```

#### **Resource Management:**
```bash
# Configure resource limits
helm install currency-converter ./helm/currency-converter \
  --set resources.limits.cpu=1000m \
  --set resources.limits.memory=1Gi \
  --set resources.requests.cpu=500m \
  --set resources.requests.memory=512Mi
```

#### **Custom Values File:**
```bash
# Create custom-values.yaml
cat > custom-values.yaml << EOF
replicaCount: 5
service:
  type: LoadBalancer
ingress:
  enabled: true
  hosts:
    - host: my-currency-app.com
      paths:
        - path: /
          pathType: Prefix
autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 20
EOF

# Install with custom values
helm install currency-converter ./helm/currency-converter -f custom-values.yaml
```

### **Management Commands:**

#### **Check Deployment Status:**
```bash
# View all resources
kubectl get all -l app.kubernetes.io/name=currency-converter

# Check pod status
kubectl get pods -l app.kubernetes.io/name=currency-converter

# View deployment details
kubectl describe deployment currency-converter
```

#### **Monitor Application:**
```bash
# View logs
kubectl logs -l app.kubernetes.io/name=currency-converter

# Check health endpoint
kubectl port-forward svc/currency-converter 8080:80
curl http://localhost:8080/health
```

#### **Scale the Application:**
```bash
# Manual scaling
kubectl scale deployment currency-converter --replicas=10

# Update via Helm
helm upgrade currency-converter ./helm/currency-converter \
  --set replicaCount=10
```

#### **Update the Application:**
```bash
# Upgrade with new image tag
helm upgrade currency-converter ./helm/currency-converter \
  --set image.tag=v2.0.0

# Upgrade with new values
helm upgrade currency-converter ./helm/currency-converter -f new-values.yaml
```

#### **Uninstall:**
```bash
# Remove the deployment
helm uninstall currency-converter

# Verify cleanup
kubectl get all -l app.kubernetes.io/name=currency-converter
```

### **Production Considerations:**

#### **High Availability Setup:**
```bash
# Deploy with anti-affinity and PDB
helm install currency-converter ./helm/currency-converter \
  --set replicaCount=5 \
  --set podDisruptionBudget.enabled=true \
  --set podDisruptionBudget.minAvailable=2 \
  --values ha-values.yaml
```

#### **Monitoring and Observability:**
```bash
# Deploy with monitoring enabled
helm install currency-converter ./helm/currency-converter \
  --set monitoring.enabled=true \
  --set monitoring.serviceMonitor.enabled=true
```

### **Troubleshooting:**

#### **Check Chart Syntax:**
```bash
# Lint the chart
helm lint ./helm/currency-converter

# Dry run installation
helm install currency-converter ./helm/currency-converter --dry-run
```

#### **Debug Deployment:**
```bash
# Get Helm values
helm get values currency-converter

# Get rendered manifests
helm get manifest currency-converter

# Check events
kubectl get events --sort-by=.metadata.creationTimestamp
```

For detailed configuration options and examples, see the [Helm Chart README](./helm/currency-converter/README.md).

## 🏗️ Infrastructure as Code (IaC) with Terraform

The project includes a complete Infrastructure as Code solution using Terraform and Kind for local Kubernetes development and testing.

### **IaC Features:**
- **Multi-node Kubernetes cluster** (1 master + 1 worker)
- **ArgoCD GitOps platform** for automated deployments
- **Metrics Server** for resource monitoring and HPA
- **Automated cluster management** with comprehensive scripts
- **Production-grade networking** and security policies

### **Prerequisites:**
- Docker Desktop or Docker Engine
- Terraform >= 1.0
- Kind (Kubernetes in Docker)
- kubectl
- Helm 3.x

```bash
# Install prerequisites on macOS
brew install docker terraform kind kubectl helm
```

### **Quick Start:**

#### **1. Create the Kubernetes Cluster:**
```bash
# Create cluster with ArgoCD and metrics server
./infrastructure/scripts/setup-cluster.sh

# Custom configuration
./infrastructure/scripts/setup-cluster.sh --cluster-name my-cluster --k8s-version 1.28.0
```

#### **2. Validate the Cluster:**
```bash
# Run comprehensive validation tests
./infrastructure/scripts/validate-cluster.sh

# Verbose output with detailed cluster information
./infrastructure/scripts/validate-cluster.sh --verbose
```

#### **3. Access ArgoCD GitOps Platform:**
```bash
# Set kubectl context
export KUBECONFIG=./infrastructure/terraform/kubeconfig

# Get ArgoCD admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d

# Access ArgoCD UI
kubectl port-forward svc/argocd-server -n argocd 8080:443
# URL: https://localhost:8080 (user: admin)
```

#### **4. Deploy Application via GitOps:**
```bash
# Deploy ArgoCD application (already configured for this repo)
kubectl apply -f argocd/currency-converter-app.yaml

# Monitor deployment
kubectl get applications -n argocd
kubectl get pods -n currency-converter -w
```

#### **5. Clean Up:**
```bash
# Destroy the cluster and clean up resources
./infrastructure/scripts/teardown-cluster.sh

# Force cleanup without confirmation
./infrastructure/scripts/teardown-cluster.sh --force --clean-all
```

### **GitOps Workflow:**

#### **Automatic Deployment:**
The system is configured for **continuous deployment**:
1. **Push changes** to the main branch
2. **GitHub Actions** builds and pushes Docker image
3. **ArgoCD automatically detects** the changes
4. **Deployment happens automatically** without manual intervention

#### **ArgoCD Configuration:**
- **Repository**: https://github.com/singhavinash2915/avinash-cognyte-devops-test.git
- **Path**: `helm/currency-converter`
- **Branch**: `main`
- **Auto-sync**: Enabled (deploys changes automatically)
- **Self-healing**: Enabled (reverts manual changes)

#### **Monitor GitOps:**
```bash
# Watch application status
kubectl get applications -n argocd -w

# View ArgoCD logs
kubectl logs -n argocd deployment/argocd-application-controller

# Check deployment events
kubectl get events -n currency-converter --sort-by='.lastTimestamp'
```

### **Infrastructure Components:**

#### **Terraform Resources:**
- **Kind Cluster**: Multi-node Kubernetes cluster
- **Namespaces**: Application and ArgoCD namespaces
- **ArgoCD**: Complete GitOps platform installation
- **Metrics Server**: Resource monitoring for HPA
- **Networking**: CNI with proper pod/service subnets

#### **Directory Structure:**
```
infrastructure/
├── terraform/
│   ├── main.tf           # Main infrastructure configuration
│   ├── variables.tf      # Configurable parameters
│   ├── outputs.tf        # Cluster information outputs
│   └── versions.tf       # Provider requirements
├── scripts/
│   ├── setup-cluster.sh      # Cluster creation automation
│   ├── teardown-cluster.sh   # Cluster destruction automation
│   └── validate-cluster.sh   # Comprehensive cluster testing
└── README.md             # Infrastructure documentation
```

#### **Automation Scripts:**

**setup-cluster.sh Options:**
```bash
--cluster-name NAME     # Custom cluster name (default: currency-converter)
--k8s-version VERSION   # Kubernetes version (default: 1.29.0)
--skip-argocd          # Skip ArgoCD installation
--skip-metrics         # Skip metrics server installation
--force-recreate       # Delete and recreate existing cluster
```

**validate-cluster.sh Tests:**
- ✅ Cluster connectivity and basic functionality
- ✅ Node configuration (1 master + 1 worker)
- ✅ System pods health
- ✅ ArgoCD installation and functionality
- ✅ Metrics server operation
- ✅ Cluster networking and DNS
- ✅ Storage functionality
- ✅ Load balancer simulation
- ✅ Port forwarding capability

### **Advanced Configuration:**

#### **Custom Terraform Variables:**
```bash
# Create terraform.tfvars
cat > infrastructure/terraform/terraform.tfvars << EOF
cluster_name        = "my-custom-cluster"
kubernetes_version  = "1.28.0"
argocd_enabled      = true
metrics_enabled     = true
namespace          = "my-app"
argocd_namespace   = "argocd"
EOF
```

#### **Manual Terraform Operations:**
```bash
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Plan infrastructure changes
terraform plan

# Apply infrastructure
terraform apply

# View outputs
terraform output

# Destroy infrastructure
terraform destroy
```

### **Production Considerations:**

#### **Security:**
- **RBAC**: Role-based access control enabled
- **Network Policies**: Namespace isolation
- **Non-root containers**: Security hardened images
- **TLS encryption**: All communication encrypted

#### **Monitoring:**
- **Metrics Server**: Resource metrics collection
- **ArgoCD UI**: Application deployment monitoring
- **Health checks**: Comprehensive service monitoring
- **Logging**: Structured logging throughout

#### **High Availability:**
- **Multi-node cluster**: Control plane + worker separation
- **Pod disruption budgets**: Ensure service availability
- **Auto-healing**: ArgoCD self-healing capabilities
- **Resource limits**: Proper resource management

### **Troubleshooting:**

#### **Common Issues:**
```bash
# Docker not running
open -a Docker  # macOS
sudo systemctl start docker  # Linux

# Port conflicts
lsof -i :8080  # Check port usage
kubectl port-forward svc/service 8081:80  # Use different port

# Cluster access issues
export KUBECONFIG=./infrastructure/terraform/kubeconfig
kubectl config current-context

# ArgoCD access
kubectl get pods -n argocd
kubectl logs -n argocd deployment/argocd-server
```

#### **Debug Commands:**
```bash
# Check cluster status
kubectl cluster-info
kubectl get nodes -o wide
kubectl get pods --all-namespaces

# Check ArgoCD
kubectl get applications -n argocd
kubectl describe application currency-converter -n argocd

# View logs
kubectl logs -n currency-converter -l app.kubernetes.io/name=currency-converter
```

### **Git Management:**

For Terraform files, follow these security practices:

**✅ Commit to Git:**
- `*.tf` files (main.tf, variables.tf, outputs.tf, versions.tf)
- `.terraform.lock.hcl` (provider version locks)
- `terraform.tfvars.example` (example configuration)

**❌ Never Commit (in .gitignore):**
- `*.tfstate*` (contains sensitive infrastructure state)
- `*.tfvars` (may contain secrets and credentials)
- `kubeconfig` (cluster access credentials)
- `.terraform/` (downloaded provider plugins)

Use `terraform.tfvars.example` as a template and create your own `terraform.tfvars` with actual values.

This Infrastructure as Code setup provides a **production-ready local development environment** with GitOps capabilities for modern Kubernetes application deployment.

## 🤝 Contributing

This project demonstrates production-grade DevOps practices for technical assessment purposes.

## 📄 License

This project is for educational and assessment purposes.