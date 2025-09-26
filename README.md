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

### Manual Testing
1. **Backend API Tests**:
   ```bash
   # Health check
   curl http://127.0.0.1:8090/health
   
   # Currency conversion
   curl -X POST http://127.0.0.1:8090/api/convert \
     -H "Content-Type: application/json" \
     -d '{"amount": 100, "from": "USD", "to": "EUR"}'
   ```

2. **Frontend UI Tests**:
   - Open http://127.0.0.1:5000
   - Test currency conversion form
   - Verify error handling
   - Check responsive design

### Automated Testing (Future)
- Unit tests for backend API
- Integration tests for frontend-backend communication
- End-to-end tests with Selenium
- Performance testing with load tests

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

## 🤝 Contributing

This project demonstrates production-grade DevOps practices for technical assessment purposes.

## 📄 License

This project is for educational and assessment purposes.