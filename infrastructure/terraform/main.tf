# Main Terraform configuration for Kind cluster
# Creates a local Kubernetes cluster with 1 master and 1 worker node

# Kind cluster configuration with multi-node setup
resource "kind_cluster" "currency_converter" {
  name           = var.cluster_name
  wait_for_ready = true

  kind_config {
    kind        = "Cluster"
    api_version = "kind.x-k8s.io/v1alpha4"

    # Control plane node (master)
    node {
      role = "control-plane"
      
      # Kubernetes version
      image = "kindest/node:v${var.kubernetes_version}"
    }

    # Worker node
    node {
      role  = "worker"
      image = "kindest/node:v${var.kubernetes_version}"
    }

    # Networking configuration
    networking {
      api_server_address = "127.0.0.1"
      api_server_port    = 6443
      pod_subnet         = "10.244.0.0/16"
      service_subnet     = "10.96.0.0/12"
    }
  }
}

# Create application namespace
resource "null_resource" "create_namespace" {
  depends_on = [kind_cluster.currency_converter]

  provisioner "local-exec" {
    command = <<-EOT
      # Create application namespace
      kubectl apply --kubeconfig ${kind_cluster.currency_converter.kubeconfig_path} -f - <<EOF
apiVersion: v1
kind: Namespace
metadata:
  name: ${var.namespace}
  labels:
    name: ${var.namespace}
    app.kubernetes.io/name: currency-converter
EOF
    EOT
  }

  # Cleanup namespace on destroy
  provisioner "local-exec" {
    when    = destroy
    command = <<-EOT
      kubectl delete namespace currency-converter --ignore-not-found=true || true
    EOT
  }
}

# Create ArgoCD namespace
resource "null_resource" "create_argocd_namespace" {
  count      = var.argocd_enabled ? 1 : 0
  depends_on = [kind_cluster.currency_converter]

  provisioner "local-exec" {
    command = <<-EOT
      # Create ArgoCD namespace
      kubectl apply --kubeconfig ${kind_cluster.currency_converter.kubeconfig_path} -f - <<EOF
apiVersion: v1
kind: Namespace
metadata:
  name: ${var.argocd_namespace}
  labels:
    name: ${var.argocd_namespace}
    app.kubernetes.io/name: argocd
EOF
    EOT
  }

  # Cleanup namespace on destroy
  provisioner "local-exec" {
    when    = destroy
    command = <<-EOT
      kubectl delete namespace argocd --ignore-not-found=true || true
    EOT
  }
}

# Install ArgoCD
resource "null_resource" "install_argocd" {
  count      = var.argocd_enabled ? 1 : 0
  depends_on = [null_resource.create_argocd_namespace]

  provisioner "local-exec" {
    command = <<-EOT
      # Install ArgoCD
      kubectl apply --kubeconfig ${kind_cluster.currency_converter.kubeconfig_path} \
        -n ${var.argocd_namespace} \
        -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
      
      # Wait for ArgoCD server to be ready
      kubectl wait --kubeconfig ${kind_cluster.currency_converter.kubeconfig_path} \
        --namespace ${var.argocd_namespace} \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/name=argocd-server \
        --timeout=300s
      
      # Wait for ArgoCD application controller to be ready
      kubectl wait --kubeconfig ${kind_cluster.currency_converter.kubeconfig_path} \
        --namespace ${var.argocd_namespace} \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/name=argocd-application-controller \
        --timeout=300s
    EOT
  }

  # Cleanup ArgoCD on destroy
  provisioner "local-exec" {
    when    = destroy
    command = <<-EOT
      kubectl delete --ignore-not-found=true \
        -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml || true
    EOT
  }
}

# Install Metrics Server
resource "null_resource" "install_metrics_server" {
  count      = var.metrics_enabled ? 1 : 0
  depends_on = [kind_cluster.currency_converter]

  provisioner "local-exec" {
    command = <<-EOT
      # Install Metrics Server with insecure TLS for Kind
      kubectl apply --kubeconfig ${kind_cluster.currency_converter.kubeconfig_path} -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
      
      # Patch metrics server for Kind compatibility
      kubectl patch --kubeconfig ${kind_cluster.currency_converter.kubeconfig_path} deployment metrics-server -n kube-system --type='json' -p='[
        {
          "op": "add",
          "path": "/spec/template/spec/containers/0/args/-",
          "value": "--kubelet-insecure-tls"
        }
      ]'
      
      # Wait for metrics server to be ready
      kubectl wait --kubeconfig ${kind_cluster.currency_converter.kubeconfig_path} --namespace kube-system \
        --for=condition=ready pod \
        --selector=k8s-app=metrics-server \
        --timeout=120s
    EOT
  }

  # Cleanup metrics server on destroy
  provisioner "local-exec" {
    when    = destroy
    command = <<-EOT
      kubectl delete --ignore-not-found=true -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml || true
    EOT
  }
}

# Save kubeconfig to local file
resource "local_file" "kubeconfig" {
  content  = kind_cluster.currency_converter.kubeconfig
  filename = "${path.module}/kubeconfig"
}

# Wait for cluster to be fully ready
resource "null_resource" "wait_for_cluster" {
  depends_on = [
    kind_cluster.currency_converter,
    null_resource.create_namespace,
    null_resource.install_argocd,
    null_resource.install_metrics_server
  ]

  provisioner "local-exec" {
    command = <<-EOT
      # Wait for all nodes to be ready
      kubectl wait --kubeconfig ${kind_cluster.currency_converter.kubeconfig_path} \
        --for=condition=ready nodes \
        --all \
        --timeout=300s
      
      # Wait for system pods to be ready
      kubectl wait --kubeconfig ${kind_cluster.currency_converter.kubeconfig_path} \
        --namespace kube-system \
        --for=condition=ready pod \
        --selector=tier=control-plane \
        --timeout=300s
    EOT
  }
}