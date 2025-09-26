#!/bin/bash
# CI Runner Script for Currency Converter Application
# Runs comprehensive tests in CI/CD environments

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TEST_DIR="$PROJECT_ROOT/application/tests"
BACKEND_DIR="$PROJECT_ROOT/application/backend"
DOCKER_IMAGE_NAME="currency-converter"
CONTAINER_NAME="currency-converter-ci-test"
TEST_PORT=8080

# Function to print colored output
print_status() {
    echo -e "${BLUE}[CI]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to cleanup on exit
cleanup() {
    print_status "Cleaning up..."
    
    # Stop and remove Docker container if running
    if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
        docker stop $CONTAINER_NAME >/dev/null 2>&1 || true
        docker rm $CONTAINER_NAME >/dev/null 2>&1 || true
    fi
    
    # Kill any processes using the test port
    if command_exists lsof; then
        lsof -ti:$TEST_PORT | xargs kill -9 2>/dev/null || true
    fi
}

# Trap cleanup on exit
trap cleanup EXIT

# Function to setup test environment
setup_environment() {
    print_status "Setting up test environment..."
    
    # Check required tools
    if ! command_exists python3; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    if ! command_exists docker; then
        print_error "Docker is required but not installed"
        exit 1
    fi
    
    # Setup Python virtual environment
    if [ ! -d "$PROJECT_ROOT/venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv "$PROJECT_ROOT/venv"
    fi
    
    # Activate virtual environment
    source "$PROJECT_ROOT/venv/bin/activate"
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install --upgrade pip >/dev/null
    pip install -r "$BACKEND_DIR/requirements.txt" >/dev/null
    pip install -r "$TEST_DIR/requirements.txt" >/dev/null
    
    print_success "Environment setup completed"
}

# Function to run code quality checks
run_code_quality() {
    print_status "Running code quality checks..."
    
    source "$PROJECT_ROOT/venv/bin/activate"
    
    # Install code quality tools
    pip install black flake8 isort pylint >/dev/null 2>&1 || true
    
    cd "$BACKEND_DIR"
    
    # Check formatting with black
    print_status "Checking code formatting..."
    if ! black --check --diff . 2>/dev/null; then
        print_warning "Code formatting issues found. Run 'black .' to fix."
    else
        print_success "Code formatting is correct"
    fi
    
    # Check import sorting
    print_status "Checking import sorting..."
    if ! isort --check-only --diff . 2>/dev/null; then
        print_warning "Import sorting issues found. Run 'isort .' to fix."
    else
        print_success "Import sorting is correct"
    fi
    
    # Run flake8 linting
    print_status "Running flake8 linting..."
    if flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 >/dev/null; then
        print_success "No major linting issues found"
    else
        print_warning "Some linting issues found (non-blocking)"
    fi
    
    cd "$PROJECT_ROOT"
}

# Function to run unit tests
run_unit_tests() {
    print_status "Running unit tests..."
    
    source "$PROJECT_ROOT/venv/bin/activate"
    cd "$TEST_DIR"
    
    # Run unit tests with coverage
    if python -m pytest -m "unit" --cov=../backend --cov-report=term-missing --cov-report=html:htmlcov -v; then
        print_success "All unit tests passed"
        return 0
    else
        print_error "Unit tests failed"
        return 1
    fi
}

# Function to build Docker image
build_docker_image() {
    print_status "Building Docker image..."
    
    cd "$PROJECT_ROOT"
    
    if docker build -t "$DOCKER_IMAGE_NAME:ci" . >/dev/null; then
        print_success "Docker image built successfully"
        return 0
    else
        print_error "Docker image build failed"
        return 1
    fi
}

# Function to test Docker container
test_docker_container() {
    print_status "Testing Docker container..."
    
    # Start container
    if ! docker run -d -p $TEST_PORT:8080 --name $CONTAINER_NAME "$DOCKER_IMAGE_NAME:ci" >/dev/null; then
        print_error "Failed to start Docker container"
        return 1
    fi
    
    # Wait for container to be ready
    print_status "Waiting for container to be ready..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s http://localhost:$TEST_PORT/health >/dev/null 2>&1; then
            print_success "Container is ready"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            print_error "Container failed to become ready within timeout"
            docker logs $CONTAINER_NAME
            return 1
        fi
        
        sleep 2
        ((attempt++))
    done
    
    # Test basic functionality
    print_status "Testing container endpoints..."
    
    # Test health endpoint
    if ! curl -f -s http://localhost:$TEST_PORT/health >/dev/null; then
        print_error "Health endpoint test failed"
        return 1
    fi
    
    # Test frontend
    if ! curl -f -s http://localhost:$TEST_PORT/ >/dev/null; then
        print_error "Frontend endpoint test failed"
        return 1
    fi
    
    # Test API conversion
    if ! curl -f -s -X POST http://localhost:$TEST_PORT/api/convert \
        -H "Content-Type: application/json" \
        -d '{"amount": 100, "from": "USD", "to": "EUR"}' >/dev/null; then
        print_error "API conversion test failed"
        return 1
    fi
    
    print_success "Docker container tests passed"
    return 0
}

# Function to run integration tests
run_integration_tests() {
    print_status "Running integration tests..."
    
    source "$PROJECT_ROOT/venv/bin/activate"
    cd "$TEST_DIR"
    
    # Run integration tests
    if python -m pytest -m "integration" -v --tb=short; then
        print_success "All integration tests passed"
        return 0
    else
        print_error "Integration tests failed"
        return 1
    fi
}

# Function to test Helm chart
test_helm_chart() {
    print_status "Testing Helm chart..."
    
    # Check if helm is available
    if ! command_exists helm; then
        print_warning "Helm not found, skipping Helm chart tests"
        return 0
    fi
    
    cd "$PROJECT_ROOT"
    
    # Lint Helm chart
    if helm lint helm/currency-converter/; then
        print_success "Helm chart linting passed"
    else
        print_error "Helm chart linting failed"
        return 1
    fi
    
    # Template test
    if helm template test-release helm/currency-converter/ >/dev/null; then
        print_success "Helm chart templating passed"
    else
        print_error "Helm chart templating failed"
        return 1
    fi
    
    return 0
}

# Function to generate reports
generate_reports() {
    print_status "Generating test reports..."
    
    source "$PROJECT_ROOT/venv/bin/activate"
    cd "$TEST_DIR"
    
    # Create reports directory
    mkdir -p reports
    
    # Generate comprehensive test report
    python -m pytest --html=reports/test_report.html --self-contained-html --tb=short || true
    
    # Generate coverage report
    if [ -d "htmlcov" ]; then
        print_success "Coverage report available at: $TEST_DIR/htmlcov/index.html"
    fi
    
    if [ -f "reports/test_report.html" ]; then
        print_success "Test report available at: $TEST_DIR/reports/test_report.html"
    fi
}

# Main execution function
main() {
    local run_mode="${1:-all}"
    
    echo "=================================================="
    echo "Currency Converter CI/CD Test Runner"
    echo "=================================================="
    echo "Mode: $run_mode"
    echo "Project Root: $PROJECT_ROOT"
    echo "Test Directory: $TEST_DIR"
    echo "=================================================="
    
    case $run_mode in
        "setup")
            setup_environment
            ;;
        "quality")
            setup_environment
            run_code_quality
            ;;
        "unit")
            setup_environment
            run_unit_tests
            ;;
        "docker")
            build_docker_image
            test_docker_container
            ;;
        "integration")
            setup_environment
            build_docker_image
            run_integration_tests
            ;;
        "helm")
            test_helm_chart
            ;;
        "quick")
            setup_environment
            run_unit_tests
            ;;
        "all"|*)
            print_status "Running complete CI/CD pipeline..."
            
            # Setup
            setup_environment
            
            # Code quality
            run_code_quality
            
            # Unit tests
            if ! run_unit_tests; then
                print_error "Unit tests failed, stopping pipeline"
                exit 1
            fi
            
            # Docker build and test
            if ! build_docker_image; then
                print_error "Docker build failed, stopping pipeline"
                exit 1
            fi
            
            if ! test_docker_container; then
                print_error "Docker container tests failed, stopping pipeline"
                exit 1
            fi
            
            # Integration tests
            if ! run_integration_tests; then
                print_error "Integration tests failed, stopping pipeline"
                exit 1
            fi
            
            # Helm tests
            test_helm_chart
            
            # Generate reports
            generate_reports
            
            print_success "Complete CI/CD pipeline passed! 🎉"
            ;;
    esac
}

# Run main function with all arguments
main "$@"