# Variables for Kind cluster configuration

variable "cluster_name" {
  description = "Name of the Kind cluster"
  type        = string
  default     = "currency-converter"
}

variable "kubernetes_version" {
  description = "Kubernetes version for the cluster"
  type        = string
  default     = "1.29.0"
}

variable "argocd_enabled" {
  description = "Enable ArgoCD installation"
  type        = bool
  default     = true
}

variable "metrics_enabled" {
  description = "Enable metrics server installation"
  type        = bool
  default     = true
}

variable "namespace" {
  description = "Kubernetes namespace for the application"
  type        = string
  default     = "currency-converter"
}

variable "argocd_namespace" {
  description = "Namespace for ArgoCD installation"
  type        = string
  default     = "argocd"
}