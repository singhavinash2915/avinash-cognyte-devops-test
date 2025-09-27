# Output values for the Kind cluster

output "cluster_name" {
  description = "Name of the Kind cluster"
  value       = kind_cluster.currency_converter.name
}

output "cluster_endpoint" {
  description = "Kubernetes cluster endpoint"
  value       = kind_cluster.currency_converter.endpoint
}

output "kubeconfig_path" {
  description = "Path to the kubeconfig file"
  value       = local_file.kubeconfig.filename
}

output "namespace" {
  description = "Application namespace"
  value       = var.namespace
}

output "cluster_info" {
  description = "Cluster information"
  value = {
    name              = kind_cluster.currency_converter.name
    endpoint          = kind_cluster.currency_converter.endpoint
    kubernetes_version = var.kubernetes_version
    nodes             = 2 # 1 master + 1 worker
    argocd_enabled    = var.argocd_enabled
    argocd_namespace  = var.argocd_namespace
    metrics_enabled   = var.metrics_enabled
  }
}

output "access_urls" {
  description = "URLs to access the cluster services"
  value = {
    api_server = kind_cluster.currency_converter.endpoint
    argocd_ui = "Access via: kubectl port-forward svc/argocd-server -n ${var.argocd_namespace} 8080:443"
  }
}

output "kubectl_commands" {
  description = "Useful kubectl commands"
  value = {
    set_context = "export KUBECONFIG=${local_file.kubeconfig.filename}"
    get_nodes   = "kubectl get nodes"
    get_pods    = "kubectl get pods --all-namespaces"
    cluster_info = "kubectl cluster-info"
    argocd_pods = "kubectl get pods -n ${var.argocd_namespace}"
    argocd_password = "kubectl -n ${var.argocd_namespace} get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d"
  }
}