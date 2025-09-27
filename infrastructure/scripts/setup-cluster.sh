#!/bin/bash
# Currency Converter - Kubernetes Cluster Setup Script
# Creates a local Kind cluster with 1 master and 1 worker node using Terraform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory and paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TERRAFORM_DIR="$PROJECT_ROOT/infrastructure/terraform"

# Default values
CLUSTER_NAME="currency-converter"
KUBERNETES_VERSION="1.29.0"
SKIP_ARGOCD=false
SKIP_METRICS=false
FORCE_RECREATE=false

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
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

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    local missing_tools=()
    
    # Check Docker
    if ! command_exists docker; then
        missing_tools+=("docker")
    elif ! docker info >/dev/null 2>&1; then
        print_error "Docker is installed but not running"
        echo "Please start Docker and try again"
        exit 1
    fi
    
    # Check Terraform
    if ! command_exists terraform; then
        missing_tools+=("terraform")
    fi
    
    # Check Kind
    if ! command_exists kind; then
        missing_tools+=("kind")
    fi
    
    # Check kubectl
    if ! command_exists kubectl; then
        missing_tools+=("kubectl")
    fi
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        print_error "Missing required tools: ${missing_tools[*]}"
        echo ""
        echo "Please install the missing tools:"
        echo "  Docker: https://docs.docker.com/get-docker/"
        echo "  Terraform: https://learn.hashicorp.com/tutorials/terraform/install-cli"
        echo "  Kind: https://kind.sigs.k8s.io/docs/user/quick-start/#installation"
        echo "  kubectl: https://kubernetes.io/docs/tasks/tools/"
        echo ""
        echo "On macOS with Homebrew:"
        echo "  brew install docker terraform kind kubectl"
        exit 1
    fi
    
    print_success "All prerequisites are satisfied"
}

# Function to check for existing cluster
check_existing_cluster() {
    if kind get clusters 2>/dev/null | grep -q "^${CLUSTER_NAME}$"; then
        print_warning "Cluster '$CLUSTER_NAME' already exists"
        
        if [ "$FORCE_RECREATE" = true ]; then
            print_status "Force recreate enabled, deleting existing cluster..."
            kind delete cluster --name "$CLUSTER_NAME"
            return 0
        fi
        
        echo ""
        read -p "Do you want to delete and recreate it? (y/N): " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Deleting existing cluster..."
            kind delete cluster --name "$CLUSTER_NAME"
        else
            print_status "Using existing cluster"
            return 1
        fi
    fi
    return 0
}

# Function to initialize Terraform
init_terraform() {
    print_status "Initializing Terraform..."
    
    cd "$TERRAFORM_DIR"
    
    # Initialize Terraform
    terraform init
    
    print_success "Terraform initialized"
}

# Function to create cluster with Terraform
create_cluster() {
    print_status "Creating Kubernetes cluster with Terraform..."
    
    cd "$TERRAFORM_DIR"
    
    # Create terraform.tfvars file
    cat > terraform.tfvars <<EOF
cluster_name        = "$CLUSTER_NAME"
kubernetes_version  = "$KUBERNETES_VERSION"
argocd_enabled      = $([ "$SKIP_ARGOCD" = false ] && echo "true" || echo "false")
metrics_enabled     = $([ "$SKIP_METRICS" = false ] && echo "true" || echo "false")
namespace          = "currency-converter"
argocd_namespace   = "argocd"
EOF
    
    # Plan the infrastructure
    print_status "Planning Terraform deployment..."
    terraform plan -out=tfplan
    
    # Apply the infrastructure
    print_status "Applying Terraform configuration..."
    terraform apply tfplan
    
    print_success "Cluster created successfully"
}

# Function to configure kubectl
configure_kubectl() {
    print_status "Configuring kubectl..."
    
    cd "$TERRAFORM_DIR"
    
    # Set KUBECONFIG environment variable
    export KUBECONFIG="$TERRAFORM_DIR/kubeconfig"
    
    # Verify cluster access
    kubectl cluster-info
    
    print_status "kubectl configuration:"
    echo "  export KUBECONFIG=$TERRAFORM_DIR/kubeconfig"
    
    print_success "kubectl configured successfully"
}

# Function to validate cluster
validate_cluster() {
    print_status "Validating cluster setup..."
    
    cd "$TERRAFORM_DIR"
    export KUBECONFIG="$TERRAFORM_DIR/kubeconfig"
    
    # Check nodes
    print_status "Checking cluster nodes..."
    kubectl get nodes -o wide
    
    # Verify we have 1 master and 1 worker
    local control_plane_count=$(kubectl get nodes --no-headers | grep -c "control-plane")
    local worker_count=$(kubectl get nodes --no-headers | grep -c "worker\|none")
    
    if [ "$control_plane_count" -ne 1 ]; then
        print_error "Expected 1 control-plane node, found $control_plane_count"
        exit 1
    fi
    
    if [ "$worker_count" -ne 1 ]; then
        print_error "Expected 1 worker node, found $worker_count"
        exit 1
    fi
    
    # Check system pods
    print_status "Checking system pods..."
    kubectl get pods -n kube-system
    
    # Check ArgoCD if enabled
    if [ "$SKIP_ARGOCD" = false ]; then
        print_status "Checking ArgoCD..."
        kubectl get pods -n argocd
    fi
    
    # Check metrics server if enabled
    if [ "$SKIP_METRICS" = false ]; then
        print_status "Checking metrics server..."
        kubectl get pods -n kube-system -l k8s-app=metrics-server
    fi
    
    # Check application namespace
    print_status "Checking application namespace..."
    kubectl get namespace currency-converter
    
    print_success "Cluster validation completed"
}

# Function to display cluster information
display_cluster_info() {
    print_status "Cluster Information"
    
    cd "$TERRAFORM_DIR"
    
    echo ""
    echo "🎉 Kubernetes cluster created successfully!"
    echo ""
    
    # Display Terraform outputs
    terraform output
    
    echo ""
    echo "📋 Cluster Details:"
    echo "  Name: $CLUSTER_NAME"
    echo "  Kubernetes Version: $KUBERNETES_VERSION"
    echo "  Nodes: 1 master + 1 worker"
    echo "  ArgoCD: $([ "$SKIP_ARGOCD" = false ] && echo "Enabled" || echo "Disabled")"
    echo "  Metrics: $([ "$SKIP_METRICS" = false ] && echo "Enabled" || echo "Disabled")"
    echo ""
    
    echo "🔧 Usage Commands:"
    echo "  Set kubectl context:"
    echo "    export KUBECONFIG=$TERRAFORM_DIR/kubeconfig"
    echo ""
    echo "  Check cluster:"
    echo "    kubectl cluster-info"
    echo "    kubectl get nodes"
    echo "    kubectl get pods --all-namespaces"
    echo ""
    echo "  Access ArgoCD UI:"
    echo "    kubectl port-forward svc/argocd-server -n argocd 8080:443"
    echo "    URL: https://localhost:8080 (user: admin)"
    echo "    Password: kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d"
    echo ""
    echo "  Teardown cluster:"
    echo "    ./infrastructure/scripts/teardown-cluster.sh"
}

# Function to show help
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --cluster-name NAME     Name of the Kind cluster (default: currency-converter)"
    echo "  --k8s-version VERSION   Kubernetes version (default: 1.29.0)"
    echo "  --skip-argocd           Skip ArgoCD installation"
    echo "  --skip-metrics          Skip metrics server installation"
    echo "  --force-recreate        Force recreate cluster if it exists"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                  # Create cluster with defaults (ArgoCD + Metrics)"
    echo "  $0 --cluster-name my-cluster       # Create cluster with custom name"
    echo "  $0 --k8s-version 1.28.0           # Create cluster with specific K8s version"
    echo "  $0 --skip-argocd --skip-metrics    # Create minimal cluster"
    echo "  $0 --force-recreate                # Force recreate existing cluster"
    echo ""
    echo "Prerequisites:"
    echo "  - Docker (running)"
    echo "  - Terraform >= 1.0"
    echo "  - Kind"
    echo "  - kubectl"
}

# Main function
main() {
    echo "=================================================="
    echo "Currency Converter - Kubernetes Cluster Setup"
    echo "=================================================="
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --cluster-name)
                CLUSTER_NAME="$2"
                shift 2
                ;;
            --k8s-version)
                KUBERNETES_VERSION="$2"
                shift 2
                ;;
            --skip-argocd)
                SKIP_ARGOCD=true
                shift
                ;;
            --skip-metrics)
                SKIP_METRICS=true
                shift
                ;;
            --force-recreate)
                FORCE_RECREATE=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Check prerequisites
    check_prerequisites
    
    # Check for existing cluster
    if ! check_existing_cluster; then
        display_cluster_info
        exit 0
    fi
    
    # Initialize Terraform
    init_terraform
    
    # Create cluster
    create_cluster
    
    # Configure kubectl
    configure_kubectl
    
    # Validate cluster
    validate_cluster
    
    # Display information
    display_cluster_info
    
    print_success "Setup completed successfully! 🚀"
}

# Run main function with all arguments
main "$@"