#!/bin/bash
# Currency Converter - Kubernetes Cluster Teardown Script
# Destroys the local Kind cluster using Terraform

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
FORCE=false
CLEAN_ALL=false

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

# Function to check if Terraform state exists
check_terraform_state() {
    if [ ! -f "$TERRAFORM_DIR/terraform.tfstate" ]; then
        print_warning "No Terraform state file found"
        return 1
    fi
    
    # Check if state contains resources
    if terraform -chdir="$TERRAFORM_DIR" state list 2>/dev/null | grep -q .; then
        return 0
    else
        print_warning "Terraform state exists but contains no resources"
        return 1
    fi
}

# Function to check for orphaned Kind clusters
check_orphaned_clusters() {
    print_status "Checking for orphaned Kind clusters..."
    
    local kind_clusters=$(kind get clusters 2>/dev/null || echo "")
    
    if [ -n "$kind_clusters" ]; then
        print_warning "Found Kind clusters:"
        echo "$kind_clusters"
        echo ""
        
        if [ "$FORCE" = true ]; then
            print_status "Force cleanup enabled, removing all Kind clusters..."
            echo "$kind_clusters" | while read cluster; do
                if [ -n "$cluster" ]; then
                    print_status "Deleting cluster: $cluster"
                    kind delete cluster --name "$cluster"
                fi
            done
        else
            read -p "Remove all Kind clusters? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                echo "$kind_clusters" | while read cluster; do
                    if [ -n "$cluster" ]; then
                        print_status "Deleting cluster: $cluster"
                        kind delete cluster --name "$cluster"
                    fi
                done
            fi
        fi
    else
        print_success "No orphaned Kind clusters found"
    fi
}

# Function to destroy infrastructure with Terraform
destroy_with_terraform() {
    print_status "Destroying infrastructure with Terraform..."
    
    cd "$TERRAFORM_DIR"
    
    # Show what will be destroyed
    print_status "Planning Terraform destroy..."
    if ! terraform plan -destroy -out=destroy.tfplan; then
        print_error "Terraform plan failed"
        exit 1
    fi
    
    if [ "$FORCE" = false ]; then
        echo ""
        read -p "Are you sure you want to destroy the infrastructure? (y/N): " -n 1 -r
        echo
        
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_status "Destroy cancelled by user"
            rm -f destroy.tfplan
            exit 0
        fi
    fi
    
    # Apply the destroy plan
    print_status "Destroying infrastructure..."
    if terraform apply destroy.tfplan; then
        print_success "Infrastructure destroyed successfully"
    else
        print_error "Terraform destroy failed"
        print_status "Attempting manual cleanup..."
        check_orphaned_clusters
    fi
    
    # Clean up plan file
    rm -f destroy.tfplan
}

# Function to force destroy without Terraform
force_destroy() {
    print_warning "Force destroying without Terraform state..."
    
    # Get cluster name from tfvars or use default
    local cluster_name="currency-converter"
    if [ -f "$TERRAFORM_DIR/terraform.tfvars" ]; then
        cluster_name=$(grep "cluster_name" "$TERRAFORM_DIR/terraform.tfvars" | sed 's/.*=\s*"\([^"]*\)".*/\1/' || echo "currency-converter")
    fi
    
    print_status "Attempting to delete cluster: $cluster_name"
    if kind get clusters 2>/dev/null | grep -q "^${cluster_name}$"; then
        kind delete cluster --name "$cluster_name"
        print_success "Cluster deleted: $cluster_name"
    else
        print_warning "Cluster not found: $cluster_name"
    fi
    
    # Check for other orphaned clusters
    check_orphaned_clusters
}

# Function to cleanup local files
cleanup_local_files() {
    print_status "Cleaning up local files..."
    
    cd "$TERRAFORM_DIR"
    
    # Remove kubeconfig file
    if [ -f "kubeconfig" ]; then
        rm -f kubeconfig
        print_status "Removed kubeconfig file"
    fi
    
    # Remove Terraform plan files
    if [ -f "tfplan" ]; then
        rm -f tfplan
        print_status "Removed Terraform plan file"
    fi
    
    if [ -f "destroy.tfplan" ]; then
        rm -f destroy.tfplan
        print_status "Removed destroy plan file"
    fi
    
    # Remove terraform.tfvars
    if [ -f "terraform.tfvars" ]; then
        rm -f terraform.tfvars
        print_status "Removed terraform.tfvars file"
    fi
    
    if [ "$CLEAN_ALL" = true ]; then
        # Remove .terraform directory
        if [ -d ".terraform" ]; then
            rm -rf .terraform
            print_status "Removed .terraform directory"
        fi
        
        # Remove terraform.tfstate.backup
        if [ -f "terraform.tfstate.backup" ]; then
            rm -f terraform.tfstate.backup
            print_status "Removed Terraform state backup"
        fi
        
        # Remove lock file
        if [ -f ".terraform.lock.hcl" ]; then
            rm -f .terraform.lock.hcl
            print_status "Removed Terraform lock file"
        fi
    fi
    
    print_success "Local cleanup completed"
}

# Function to verify cleanup
verify_cleanup() {
    print_status "Verifying cleanup..."
    
    # Check for remaining Kind clusters
    local remaining_clusters=$(kind get clusters 2>/dev/null || echo "")
    if [ -n "$remaining_clusters" ]; then
        print_warning "Remaining Kind clusters found:"
        echo "$remaining_clusters"
    else
        print_success "No Kind clusters remaining"
    fi
    
    # Check for Docker containers with Kind labels
    local kind_containers=$(docker ps -a --filter "label=io.x-k8s.kind.cluster" --format "{{.Names}}" 2>/dev/null || echo "")
    if [ -n "$kind_containers" ]; then
        print_warning "Found Kind containers that may need manual cleanup:"
        echo "$kind_containers"
        
        if [ "$FORCE" = true ]; then
            print_status "Force cleanup enabled, removing containers..."
            echo "$kind_containers" | xargs -r docker rm -f
            print_success "Containers removed"
        fi
    else
        print_success "No Kind containers found"
    fi
    
    # Check for Terraform state
    if [ -f "$TERRAFORM_DIR/terraform.tfstate" ]; then
        local resource_count=$(terraform -chdir="$TERRAFORM_DIR" state list 2>/dev/null | wc -l || echo "0")
        if [ "$resource_count" -gt 0 ]; then
            print_warning "Terraform state still contains $resource_count resources"
        else
            print_success "Terraform state is clean"
        fi
    else
        print_success "No Terraform state file found"
    fi
}

# Function to display cleanup summary
display_summary() {
    print_status "Cleanup Summary"
    echo ""
    echo "✅ Infrastructure destroyed"
    echo "✅ Local files cleaned up"
    echo "✅ Cluster verification completed"
    echo ""
    echo "The Kubernetes cluster has been completely removed."
    echo ""
    echo "To recreate the cluster, run:"
    echo "  ./infrastructure/scripts/setup-cluster.sh"
    echo ""
    echo "Useful commands to verify cleanup:"
    echo "  kind get clusters              # Should show no clusters"
    echo "  docker ps -a | grep kind       # Should show no Kind containers"
    echo "  kubectl config get-contexts   # Check for leftover contexts"
}

# Function to show help
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --force          Skip confirmation prompts and force cleanup"
    echo "  --clean-all      Remove all Terraform files (.terraform, backups, locks)"
    echo "  -h, --help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Interactive teardown with confirmation"
    echo "  $0 --force           # Force teardown without confirmation"
    echo "  $0 --clean-all       # Teardown and clean all Terraform files"
    echo "  $0 --force --clean-all  # Complete cleanup without prompts"
    echo ""
    echo "This script will:"
    echo "  1. Destroy Terraform-managed infrastructure"
    echo "  2. Remove orphaned Kind clusters if found"
    echo "  3. Clean up local configuration files"
    echo "  4. Verify complete cleanup"
}

# Main function
main() {
    echo "=================================================="
    echo "Currency Converter - Kubernetes Cluster Teardown"
    echo "=================================================="
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --force)
                FORCE=true
                shift
                ;;
            --clean-all)
                CLEAN_ALL=true
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
    
    # Check if Terraform directory exists
    if [ ! -d "$TERRAFORM_DIR" ]; then
        print_error "Terraform directory not found: $TERRAFORM_DIR"
        exit 1
    fi
    
    # Check for Terraform state and destroy accordingly
    cd "$TERRAFORM_DIR"
    
    if check_terraform_state; then
        print_status "Found Terraform state, using Terraform to destroy..."
        destroy_with_terraform
    else
        print_warning "No Terraform state found, attempting manual cleanup..."
        force_destroy
    fi
    
    # Cleanup local files
    cleanup_local_files
    
    # Verify cleanup
    verify_cleanup
    
    # Display summary
    display_summary
    
    print_success "Teardown completed successfully! 🧹"
}

# Run main function with all arguments
main "$@"