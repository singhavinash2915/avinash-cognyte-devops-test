#!/bin/bash
# Currency Converter - Kubernetes Cluster Validation Script
# Validates the local Kind cluster setup and functionality

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

# Test results
TESTS_PASSED=0
TESTS_FAILED=0
VERBOSE=false

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

print_test_result() {
    local test_name="$1"
    local result="$2"
    local details="$3"
    
    if [ "$result" = "PASS" ]; then
        echo -e "${GREEN}✓${NC} $test_name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        if [ "$VERBOSE" = true ] && [ -n "$details" ]; then
            echo "    $details"
        fi
    else
        echo -e "${RED}✗${NC} $test_name"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        if [ -n "$details" ]; then
            echo "    $details"
        fi
    fi
}

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_result="$3"
    
    if [ "$VERBOSE" = true ]; then
        print_status "Running test: $test_name"
        print_status "Command: $test_command"
    fi
    
    local output
    local exit_code
    
    if output=$(eval "$test_command" 2>&1); then
        exit_code=0
    else
        exit_code=$?
    fi
    
    if [ "$exit_code" -eq 0 ]; then
        if [ -n "$expected_result" ]; then
            if echo "$output" | grep -q "$expected_result"; then
                print_test_result "$test_name" "PASS" "$output"
            else
                print_test_result "$test_name" "FAIL" "Expected '$expected_result' not found in output"
            fi
        else
            print_test_result "$test_name" "PASS" "$output"
        fi
    else
        print_test_result "$test_name" "FAIL" "Command failed with exit code $exit_code: $output"
    fi
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if kubeconfig exists
    if [ ! -f "$TERRAFORM_DIR/kubeconfig" ]; then
        print_error "Kubeconfig file not found at $TERRAFORM_DIR/kubeconfig"
        echo "Please run the setup script first: ./infrastructure/scripts/setup-cluster.sh"
        exit 1
    fi
    
    # Set KUBECONFIG
    export KUBECONFIG="$TERRAFORM_DIR/kubeconfig"
    
    print_success "Prerequisites check passed"
}

# Function to test cluster basic functionality
test_cluster_basics() {
    print_status "Testing cluster basic functionality..."
    echo ""
    
    # Test 1: Cluster connectivity
    run_test "Cluster connectivity" "kubectl cluster-info" "Kubernetes control plane"
    
    # Test 2: Node count and roles
    run_test "Control plane node exists" "kubectl get nodes --no-headers | grep control-plane | wc -l" "1"
    run_test "Worker node exists" "kubectl get nodes --no-headers | grep -v control-plane | wc -l" "1"
    
    # Test 3: Node readiness
    run_test "All nodes ready" "kubectl get nodes --no-headers | grep -v Ready | wc -l" "0"
    
    # Test 4: System pods running
    run_test "System pods running" "kubectl get pods -n kube-system --no-headers | grep -v Running | grep -v Completed | wc -l" "0"
    
    # Test 5: Application namespace exists
    run_test "Application namespace exists" "kubectl get namespace currency-converter" "currency-converter"
}

# Function to test ArgoCD
test_argocd() {
    print_status "Testing ArgoCD..."
    echo ""
    
    # Check if ArgoCD namespace exists
    if kubectl get namespace argocd >/dev/null 2>&1; then
        run_test "ArgoCD namespace exists" "kubectl get namespace argocd" "argocd"
        run_test "ArgoCD server pod running" "kubectl get pods -n argocd -l app.kubernetes.io/name=argocd-server --no-headers | grep Running | wc -l" "1"
        run_test "ArgoCD application controller running" "kubectl get pods -n argocd -l app.kubernetes.io/name=argocd-application-controller --no-headers | grep Running | wc -l" "1"
        run_test "ArgoCD repo server running" "kubectl get pods -n argocd -l app.kubernetes.io/name=argocd-repo-server --no-headers | grep Running | wc -l" "1"
        run_test "ArgoCD server service exists" "kubectl get service -n argocd argocd-server" "argocd-server"
        
        # Test ArgoCD API accessibility
        print_status "Testing ArgoCD API accessibility..."
        if kubectl get secret -n argocd argocd-initial-admin-secret >/dev/null 2>&1; then
            print_test_result "ArgoCD admin secret exists" "PASS" "Initial admin secret found"
        else
            print_test_result "ArgoCD admin secret exists" "WARN" "Initial admin secret not found (may have been deleted)"
        fi
    else
        print_test_result "ArgoCD" "SKIP" "ArgoCD not installed"
    fi
}

# Function to test metrics server
test_metrics_server() {
    print_status "Testing metrics server..."
    echo ""
    
    # Check if metrics server is installed
    if kubectl get deployment -n kube-system metrics-server >/dev/null 2>&1; then
        run_test "Metrics server deployment exists" "kubectl get deployment -n kube-system metrics-server" "metrics-server"
        run_test "Metrics server pod running" "kubectl get pods -n kube-system -l k8s-app=metrics-server --no-headers | grep Running | wc -l" "1"
        
        # Wait a bit for metrics to be available
        sleep 5
        
        # Test metrics availability (this might fail initially, so we'll be lenient)
        if kubectl top nodes >/dev/null 2>&1; then
            print_test_result "Node metrics available" "PASS" "kubectl top nodes working"
        else
            print_test_result "Node metrics available" "WARN" "Metrics not yet available (may need more time)"
        fi
    else
        print_test_result "Metrics server" "SKIP" "Metrics server not installed"
    fi
}

# Function to test networking
test_networking() {
    print_status "Testing cluster networking..."
    echo ""
    
    # Test 1: DNS resolution
    run_test "DNS resolution" "kubectl run test-dns --image=busybox:1.28 --rm -it --restart=Never -- nslookup kubernetes.default" "kubernetes.default.svc.cluster.local"
    
    # Test 2: Pod to pod communication (create test pods)
    print_status "Creating test pods for networking validation..."
    
    # Create test pod 1
    kubectl apply -f - <<EOF >/dev/null 2>&1
apiVersion: v1
kind: Pod
metadata:
  name: test-pod-1
  namespace: currency-converter
  labels:
    app: test
spec:
  containers:
  - name: test
    image: busybox:1.28
    command: ['sleep', '3600']
EOF
    
    # Create test pod 2
    kubectl apply -f - <<EOF >/dev/null 2>&1
apiVersion: v1
kind: Pod
metadata:
  name: test-pod-2
  namespace: currency-converter
  labels:
    app: test
spec:
  containers:
  - name: test
    image: busybox:1.28
    command: ['sleep', '3600']
EOF
    
    # Wait for pods to be ready
    kubectl wait --for=condition=ready pod test-pod-1 -n currency-converter --timeout=60s >/dev/null 2>&1
    kubectl wait --for=condition=ready pod test-pod-2 -n currency-converter --timeout=60s >/dev/null 2>&1
    
    # Get pod IPs
    local pod1_ip=$(kubectl get pod test-pod-1 -n currency-converter -o jsonpath='{.status.podIP}')
    local pod2_ip=$(kubectl get pod test-pod-2 -n currency-converter -o jsonpath='{.status.podIP}')
    
    if [ -n "$pod1_ip" ] && [ -n "$pod2_ip" ]; then
        # Test pod to pod communication
        if kubectl exec test-pod-1 -n currency-converter -- ping -c 1 "$pod2_ip" >/dev/null 2>&1; then
            print_test_result "Pod to pod communication" "PASS" "Pod 1 can ping Pod 2"
        else
            print_test_result "Pod to pod communication" "FAIL" "Pod 1 cannot ping Pod 2"
        fi
    else
        print_test_result "Pod to pod communication" "FAIL" "Could not get pod IPs"
    fi
    
    # Cleanup test pods
    kubectl delete pod test-pod-1 test-pod-2 -n currency-converter >/dev/null 2>&1 || true
}

# Function to test storage
test_storage() {
    print_status "Testing cluster storage..."
    echo ""
    
    # Test default storage class
    run_test "Default storage class exists" "kubectl get storageclass" "standard"
    
    # Test persistent volume creation
    print_status "Testing persistent volume creation..."
    
    # Create test PVC
    kubectl apply -f - <<EOF >/dev/null 2>&1
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: test-pvc
  namespace: currency-converter
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
EOF
    
    # Wait for PVC to be bound
    sleep 10
    
    local pvc_status=$(kubectl get pvc test-pvc -n currency-converter -o jsonpath='{.status.phase}' 2>/dev/null || echo "NotFound")
    
    if [ "$pvc_status" = "Bound" ]; then
        print_test_result "Persistent volume creation" "PASS" "PVC bound successfully"
    else
        print_test_result "Persistent volume creation" "FAIL" "PVC status: $pvc_status"
    fi
    
    # Cleanup test PVC
    kubectl delete pvc test-pvc -n currency-converter >/dev/null 2>&1 || true
}

# Function to test load balancer simulation
test_load_balancer() {
    print_status "Testing load balancer functionality..."
    echo ""
    
    # Create test service
    kubectl apply -f - <<EOF >/dev/null 2>&1
apiVersion: v1
kind: Service
metadata:
  name: test-lb-service
  namespace: currency-converter
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8080
  selector:
    app: test-lb
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: test-lb-deployment
  namespace: currency-converter
spec:
  replicas: 1
  selector:
    matchLabels:
      app: test-lb
  template:
    metadata:
      labels:
        app: test-lb
    spec:
      containers:
      - name: test
        image: nginx:alpine
        ports:
        - containerPort: 80
EOF
    
    # Wait for deployment
    sleep 15
    
    # Check if service gets external IP (in Kind, this should be localhost)
    local external_ip=$(kubectl get service test-lb-service -n currency-converter -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
    local external_hostname=$(kubectl get service test-lb-service -n currency-converter -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "")
    
    if [ -n "$external_ip" ] || [ -n "$external_hostname" ]; then
        print_test_result "LoadBalancer service" "PASS" "External access configured"
    else
        print_test_result "LoadBalancer service" "WARN" "LoadBalancer pending (normal for Kind)"
    fi
    
    # Cleanup
    kubectl delete deployment test-lb-deployment -n currency-converter >/dev/null 2>&1 || true
    kubectl delete service test-lb-service -n currency-converter >/dev/null 2>&1 || true
}

# Function to test port forwarding
test_port_forwarding() {
    print_status "Testing port forwarding..."
    echo ""
    
    # Create test pod
    kubectl apply -f - <<EOF >/dev/null 2>&1
apiVersion: v1
kind: Pod
metadata:
  name: test-port-forward
  namespace: currency-converter
spec:
  containers:
  - name: nginx
    image: nginx:alpine
    ports:
    - containerPort: 80
EOF
    
    # Wait for pod
    kubectl wait --for=condition=ready pod test-port-forward -n currency-converter --timeout=60s >/dev/null 2>&1
    
    # Test port forwarding (in background)
    kubectl port-forward pod/test-port-forward -n currency-converter 8888:80 >/dev/null 2>&1 &
    local pf_pid=$!
    
    # Wait a moment for port forward to establish
    sleep 3
    
    # Test connection
    if curl -f http://localhost:8888 >/dev/null 2>&1; then
        print_test_result "Port forwarding" "PASS" "Can access pod via port-forward"
    else
        print_test_result "Port forwarding" "FAIL" "Cannot access pod via port-forward"
    fi
    
    # Cleanup
    kill $pf_pid 2>/dev/null || true
    wait $pf_pid 2>/dev/null || true
    kubectl delete pod test-port-forward -n currency-converter >/dev/null 2>&1 || true
}

# Function to display detailed cluster information
display_cluster_info() {
    print_status "Detailed cluster information:"
    echo ""
    
    echo "🔍 Cluster Details:"
    kubectl cluster-info
    echo ""
    
    echo "🖥️  Nodes:"
    kubectl get nodes -o wide
    echo ""
    
    echo "📦 System Pods:"
    kubectl get pods -n kube-system
    echo ""
    
    echo "🌐 Services:"
    kubectl get services --all-namespaces
    echo ""
    
    if kubectl get namespace argocd >/dev/null 2>&1; then
        echo "🔄 ArgoCD:"
        kubectl get pods,services -n argocd
        echo ""
    fi
    
    echo "📊 Resource Usage:"
    if kubectl top nodes >/dev/null 2>&1; then
        kubectl top nodes
        kubectl top pods --all-namespaces --sort-by=cpu | head -10
    else
        echo "Metrics not available yet"
    fi
    echo ""
}

# Function to show test summary
show_test_summary() {
    echo ""
    echo "=================================================="
    echo "Validation Summary"
    echo "=================================================="
    echo ""
    
    local total_tests=$((TESTS_PASSED + TESTS_FAILED))
    
    echo "📊 Test Results:"
    echo "  Total tests: $total_tests"
    echo "  Passed: $TESTS_PASSED"
    echo "  Failed: $TESTS_FAILED"
    echo ""
    
    if [ $TESTS_FAILED -eq 0 ]; then
        print_success "All tests passed! ✨"
        echo ""
        echo "🎉 Your Kubernetes cluster is working perfectly!"
        echo ""
        echo "Next steps:"
        echo "  1. Access ArgoCD UI:"
        echo "     kubectl port-forward svc/argocd-server -n argocd 8080:443"
        echo "     URL: https://localhost:8080 (user: admin)"
        echo ""
        echo "  2. Get ArgoCD admin password:"
        echo "     kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d"
        echo ""
        echo "  3. Monitor your cluster:"
        echo "     kubectl get pods --all-namespaces"
        return 0
    else
        print_error "Some tests failed!"
        echo ""
        echo "❌ Please check the failed tests above and ensure:"
        echo "  1. All prerequisites are installed"
        echo "  2. Docker is running"
        echo "  3. Cluster was created successfully"
        echo ""
        echo "To recreate the cluster:"
        echo "  ./infrastructure/scripts/teardown-cluster.sh"
        echo "  ./infrastructure/scripts/setup-cluster.sh"
        return 1
    fi
}

# Function to show help
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --verbose, -v    Show verbose output for all tests"
    echo "  --info          Show detailed cluster information only"
    echo "  -h, --help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0              # Run all validation tests"
    echo "  $0 --verbose    # Run tests with detailed output"
    echo "  $0 --info       # Show cluster information only"
    echo ""
    echo "This script validates:"
    echo "  ✓ Cluster connectivity and basic functionality"
    echo "  ✓ Node configuration (1 master + 1 worker)"
    echo "  ✓ System pods health"
    echo "  ✓ ArgoCD installation and functionality"
    echo "  ✓ Metrics server (if installed)"
    echo "  ✓ Cluster networking and DNS"
    echo "  ✓ Storage functionality"
    echo "  ✓ Load balancer simulation"
    echo "  ✓ Port forwarding capability"
}

# Main function
main() {
    echo "=================================================="
    echo "Currency Converter - Kubernetes Cluster Validation"
    echo "=================================================="
    
    local info_only=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --verbose|-v)
                VERBOSE=true
                shift
                ;;
            --info)
                info_only=true
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
    
    if [ "$info_only" = true ]; then
        display_cluster_info
        exit 0
    fi
    
    # Run validation tests
    test_cluster_basics
    test_argocd
    test_metrics_server
    test_networking
    test_storage
    test_load_balancer
    test_port_forwarding
    
    # Show detailed info if verbose
    if [ "$VERBOSE" = true ]; then
        echo ""
        display_cluster_info
    fi
    
    # Show summary and exit with appropriate code
    show_test_summary
}

# Run main function with all arguments
main "$@"