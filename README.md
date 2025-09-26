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

## 🤝 Contributing

This project demonstrates production-grade DevOps practices for technical assessment purposes.

## 📄 License

This project is for educational and assessment purposes.