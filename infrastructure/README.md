# Infrastructure as Code - Kubernetes Cluster with Terraform and Kind

This directory contains Infrastructure as Code (IaC) configuration to create a local Kubernetes cluster using Terraform and Kind (Kubernetes in Docker).

## Overview

This setup creates a **multi-node Kubernetes cluster** with:
- **1 Master node** (control-plane)
- **1 Worker node**
- **ArgoCD** for GitOps workflow management
- **Metrics Server** for resource monitoring
- **Application namespace** ready for deployment

## Prerequisites

Before running the setup, ensure you have the following tools installed:

### Required Tools

1. **Docker Desktop or Docker Engine**
   ```bash
   # Verify Docker is running
   docker info
   ```

2. **Terraform (>= 1.0)**
   ```bash
   # Install on macOS
   brew install terraform
   
   # Verify installation
   terraform --version
   ```

3. **Kind (Kubernetes in Docker)**
   ```bash
   # Install on macOS
   brew install kind
   
   # Verify installation
   kind --version
   ```

4. **kubectl**
   ```bash
   # Install on macOS
   brew install kubectl
   
   # Verify installation
   kubectl version --client
   ```

### Installation Commands (macOS with Homebrew)

```bash
# Install all prerequisites at once
brew install docker terraform kind kubectl

# Start Docker Desktop (if not already running)
open -a Docker
```

## Quick Start

### 1. Create the Cluster

```bash
# Navigate to project root
cd /path/to/currency-converter

# Create the cluster
./infrastructure/scripts/setup-cluster.sh
```

This will:
- Initialize Terraform with the Kind provider
- Create a 2-node Kubernetes cluster (1 master + 1 worker)
- Install ArgoCD for GitOps workflow management
- Install Metrics Server for resource monitoring
- Create application namespace
- Configure kubectl context

### 2. Validate the Cluster

```bash
# Run validation tests
./infrastructure/scripts/validate-cluster.sh
```

### 3. Access the Cluster

```bash
# Set kubectl context
export KUBECONFIG=./infrastructure/terraform/kubeconfig

# Check cluster status
kubectl cluster-info
kubectl get nodes
kubectl get pods --all-namespaces
```

### 4. Clean Up

```bash
# Destroy the cluster
./infrastructure/scripts/teardown-cluster.sh
```

## Directory Structure

```
infrastructure/
├── terraform/
│   ├── main.tf           # Main Terraform configuration
│   ├── variables.tf      # Input variables
│   ├── outputs.tf        # Output values
│   ├── versions.tf       # Provider requirements
│   └── kubeconfig        # Generated kubectl config (after setup)
├── scripts/
│   ├── setup-cluster.sh      # Cluster creation script
│   ├── teardown-cluster.sh   # Cluster destruction script
│   └── validate-cluster.sh   # Cluster validation script
└── README.md             # This file
```

## Scripts Documentation

### setup-cluster.sh

Creates and configures the Kubernetes cluster.

**Usage:**
```bash
# Basic setup
./infrastructure/scripts/setup-cluster.sh

# Custom cluster name
./infrastructure/scripts/setup-cluster.sh --cluster-name my-cluster

# Specific Kubernetes version
./infrastructure/scripts/setup-cluster.sh --k8s-version 1.28.0

# Skip optional components
./infrastructure/scripts/setup-cluster.sh --skip-argocd --skip-metrics

# Force recreate existing cluster
./infrastructure/scripts/setup-cluster.sh --force-recreate

# Show help
./infrastructure/scripts/setup-cluster.sh --help
```

**Options:**
- `--cluster-name NAME`: Custom cluster name (default: currency-converter)
- `--k8s-version VERSION`: Kubernetes version (default: 1.29.0)
- `--skip-argocd`: Skip ArgoCD installation
- `--skip-metrics`: Skip metrics server installation
- `--force-recreate`: Delete and recreate existing cluster

### teardown-cluster.sh

Destroys the cluster and cleans up resources.

**Usage:**
```bash
# Interactive teardown (with confirmation)
./infrastructure/scripts/teardown-cluster.sh

# Force teardown without confirmation
./infrastructure/scripts/teardown-cluster.sh --force

# Clean all Terraform files
./infrastructure/scripts/teardown-cluster.sh --clean-all

# Show help
./infrastructure/scripts/teardown-cluster.sh --help
```

**Options:**
- `--force`: Skip confirmation prompts
- `--clean-all`: Remove all Terraform state and cache files

### validate-cluster.sh

Validates cluster functionality and health.

**Usage:**
```bash
# Run all validation tests
./infrastructure/scripts/validate-cluster.sh

# Verbose output
./infrastructure/scripts/validate-cluster.sh --verbose

# Show cluster info only
./infrastructure/scripts/validate-cluster.sh --info

# Show help
./infrastructure/scripts/validate-cluster.sh --help
```

**Tests performed:**
- ✅ Cluster connectivity
- ✅ Node count and roles (1 master + 1 worker)
- ✅ System pods health
- ✅ ArgoCD installation and functionality
- ✅ Metrics server operation
- ✅ Network connectivity and DNS
- ✅ Storage provisioning
- ✅ Load balancer simulation
- ✅ Port forwarding capability

## Terraform Configuration

### Key Resources Created

1. **Kind Cluster** with multi-node configuration
2. **Kubernetes Namespace** for the application
3. **ArgoCD** for GitOps workflow management
4. **Metrics Server** for resource monitoring
5. **Kubeconfig file** for kubectl access

### Variables

Customize the cluster by modifying these variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `cluster_name` | Name of the Kind cluster | `currency-converter` |
| `kubernetes_version` | Kubernetes version | `1.29.0` |
| `argocd_enabled` | Enable ArgoCD installation | `true` |
| `metrics_enabled` | Enable metrics server | `true` |
| `namespace` | Application namespace | `currency-converter` |
| `argocd_namespace` | ArgoCD namespace | `argocd` |

### Outputs

After successful creation, Terraform provides:

```bash
# View all outputs
cd infrastructure/terraform
terraform output

# Specific outputs
terraform output cluster_name
terraform output cluster_endpoint
terraform output kubeconfig_path
```

## Manual Terraform Usage

For advanced users who prefer direct Terraform commands:

```bash
cd infrastructure/terraform

# Initialize
terraform init

# Plan
terraform plan

# Apply
terraform apply

# Destroy
terraform destroy
```

## Cluster Access

### Setting up kubectl

```bash
# Option 1: Export KUBECONFIG
export KUBECONFIG=./infrastructure/terraform/kubeconfig

# Option 2: Copy to default location
cp ./infrastructure/terraform/kubeconfig ~/.kube/config

# Verify access
kubectl cluster-info
```

### Accessing Applications

**ArgoCD UI:**
```bash
# Forward ArgoCD server port
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Access at https://localhost:8080
# Username: admin
# Password: kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d
```

**Application Port Forwarding:**
```bash
# Forward application service port
kubectl port-forward svc/your-service 8080:80 -n currency-converter

# Access at http://localhost:8080
```

## Troubleshooting

### Common Issues

1. **Docker not running**
   ```bash
   # Start Docker Desktop
   open -a Docker
   
   # Verify Docker is running
   docker info
   ```

2. **Port conflicts**
   ```bash
   # Check what's using port 8080
   lsof -i :8080
   
   # Use different port
   kubectl port-forward svc/service 8081:80
   ```

3. **Cluster creation fails**
   ```bash
   # Clean up and retry
   kind delete cluster --name currency-converter
   ./infrastructure/scripts/setup-cluster.sh
   ```

4. **kubectl connection issues**
   ```bash
   # Verify kubeconfig
   export KUBECONFIG=./infrastructure/terraform/kubeconfig
   kubectl config current-context
   ```

### Debug Commands

```bash
# Check cluster status
kubectl cluster-info
kubectl get nodes -o wide

# Check system pods
kubectl get pods -n kube-system

# Check ArgoCD
kubectl get pods -n argocd

# View logs
kubectl logs -n kube-system -l component=kube-apiserver
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-server

# Check Kind clusters
kind get clusters

# Check Docker containers
docker ps --filter "label=io.x-k8s.kind.cluster"
```

### Reset Everything

If you encounter persistent issues:

```bash
# 1. Destroy with Terraform
./infrastructure/scripts/teardown-cluster.sh --force --clean-all

# 2. Remove all Kind clusters
kind get clusters | xargs -I {} kind delete cluster --name {}

# 3. Clean Docker containers
docker ps -a --filter "label=io.x-k8s.kind.cluster" --format "{{.Names}}" | xargs -r docker rm -f

# 4. Recreate
./infrastructure/scripts/setup-cluster.sh
```

## Resource Requirements

### System Requirements

- **CPU**: 2+ cores recommended
- **RAM**: 4GB+ available
- **Disk**: 10GB+ free space
- **OS**: macOS, Linux, or Windows with WSL2

### Cluster Resources

The Kind cluster uses:
- Docker containers for nodes
- Bridge networking
- Local storage with hostPath
- Port forwarding for external access

## Security Considerations

### Default Security Features

- RBAC enabled by default
- Network policies supported
- Pod Security Standards
- Resource quotas and limits
- TLS encryption for all communication

### Production Considerations

This setup is designed for **local development and testing**. For production:

- Use managed Kubernetes services (EKS, GKE, AKS)
- Implement proper authentication and authorization
- Configure network security policies
- Set up monitoring and logging
- Use external secrets management
- Implement backup and disaster recovery

## Advanced Configuration

### Custom Terraform Variables

Create a `terraform.tfvars` file:

```hcl
cluster_name        = "my-custom-cluster"
kubernetes_version  = "1.28.0"
ingress_enabled     = true
metrics_enabled     = true
namespace          = "my-app"
host_port          = 9090
```

### Multi-Worker Setup

To add more worker nodes, modify `main.tf`:

```hcl
# Add additional worker nodes
node {
  role  = "worker"
  image = "kindest/node:v${var.kubernetes_version}"
}

node {
  role  = "worker"
  image = "kindest/node:v${var.kubernetes_version}"
}
```

### Custom Kind Configuration

For advanced Kind configurations, modify the `kind_config` block in `main.tf`:

```hcl
kind_config {
  kind        = "Cluster"
  api_version = "kind.x-k8s.io/v1alpha4"
  
  # Custom networking
  networking {
    pod_subnet     = "10.244.0.0/16"
    service_subnet = "10.96.0.0/12"
    disable_default_cni = false
  }
  
  # Additional nodes
  node {
    role = "control-plane"
    # ... configuration
  }
  
  node {
    role = "worker"
    # ... configuration
  }
}
```

## Integration with CI/CD

This infrastructure can be integrated with CI/CD pipelines:

```yaml
# Example GitHub Actions integration
- name: Setup Kind Cluster
  run: ./infrastructure/scripts/setup-cluster.sh --force-recreate

- name: Validate Cluster
  run: ./infrastructure/scripts/validate-cluster.sh

- name: Deploy Application
  run: |
    export KUBECONFIG=./infrastructure/terraform/kubeconfig
    helm install app ./helm/currency-converter

- name: Run Tests
  run: |
    export KUBECONFIG=./infrastructure/terraform/kubeconfig
    kubectl wait --for=condition=ready pod -l app=currency-converter --timeout=300s
    # Run your tests here

- name: Cleanup
  if: always()
  run: ./infrastructure/scripts/teardown-cluster.sh --force
```

## Next Steps

After setting up the cluster:

1. **Access ArgoCD UI**:
   ```bash
   export KUBECONFIG=./infrastructure/terraform/kubeconfig
   kubectl port-forward svc/argocd-server -n argocd 8080:443
   # Access: https://localhost:8080 (admin / get password from secret)
   ```

2. **Get ArgoCD admin password**:
   ```bash
   kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d
   ```

3. **Deploy your application via ArgoCD**:
   ```bash
   # Create ArgoCD application
   kubectl apply -f argocd/currency-converter-app.yaml
   ```

4. **Run validation tests**:
   ```bash
   ./infrastructure/scripts/validate-cluster.sh
   ```

## Git Management for Terraform Files

### ✅ **Files to Commit:**
```
infrastructure/terraform/
├── main.tf                    # Infrastructure configuration
├── variables.tf               # Input variable definitions  
├── outputs.tf                 # Output value definitions
├── versions.tf                # Provider requirements
├── .terraform.lock.hcl        # Provider version locks (for reproducibility)
└── terraform.tfvars.example   # Example configuration
```

### ❌ **Files in .gitignore:**
```
# Terraform runtime and sensitive files
*.tfstate              # Current infrastructure state (sensitive)
*.tfstate.*            # State backups (sensitive)
*.tfvars               # Variable values (may contain secrets)
*.tfplan               # Execution plans (temporary)
.terraform/            # Downloaded provider plugins
kubeconfig             # Cluster access credentials (sensitive)
*-config               # Generated configuration files
```

### 🔒 **Security Considerations:**
- **Never commit** `terraform.tfstate` - contains sensitive data about infrastructure
- **Never commit** `terraform.tfvars` - may contain secrets, passwords, API keys
- **Never commit** `kubeconfig` files - contain cluster access credentials
- **Always commit** `.terraform.lock.hcl` - ensures reproducible provider versions
- **Use** `terraform.tfvars.example` to document required variables without exposing values

### 📝 **Best Practices:**
1. **Copy example file**: `cp terraform.tfvars.example terraform.tfvars`
2. **Customize variables** in `terraform.tfvars` for your environment
3. **Commit configuration changes** to `.tf` files
4. **Never commit sensitive runtime files**

This Infrastructure as Code setup provides a solid foundation for local Kubernetes development and testing, with production-grade practices and comprehensive automation.