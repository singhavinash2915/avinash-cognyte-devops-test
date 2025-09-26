# Currency Converter Helm Chart

A production-grade Helm chart for deploying the Currency Converter application on Kubernetes.

## Overview

This Helm chart deploys a containerized currency converter application with:
- Flask backend API for currency conversion
- Modern responsive frontend interface
- Support for USD, EUR, GBP, JPY currencies
- Production-ready configuration with health checks
- Configurable scaling and security settings

## Prerequisites

- Kubernetes 1.19+
- Helm 3.2.0+
- Docker image built and available (`currency-converter:latest`)

## Installing the Chart

To install the chart with the release name `my-currency-converter`:

```bash
# Install from local chart
helm install my-currency-converter ./helm/currency-converter

# Install with custom values
helm install my-currency-converter ./helm/currency-converter -f custom-values.yaml

# Install with inline value overrides
helm install my-currency-converter ./helm/currency-converter \
  --set replicaCount=5 \
  --set service.type=LoadBalancer
```

## Uninstalling the Chart

To uninstall/delete the `my-currency-converter` deployment:

```bash
helm uninstall my-currency-converter
```

## Configuration

The following table lists the configurable parameters and their default values:

### Application Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `3` |
| `image.repository` | Container image repository | `currency-converter` |
| `image.tag` | Container image tag | `latest` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |

### Service Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `service.type` | Kubernetes service type | `ClusterIP` |
| `service.port` | Service port | `80` |
| `service.targetPort` | Container port | `8080` |

### Ingress Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ingress.enabled` | Enable ingress | `false` |
| `ingress.className` | Ingress class name | `""` |
| `ingress.hosts[0].host` | Hostname | `currency-converter.local` |
| `ingress.hosts[0].paths[0].path` | Path | `/` |

### Resource Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `resources.limits.cpu` | CPU limit | `500m` |
| `resources.limits.memory` | Memory limit | `512Mi` |
| `resources.requests.cpu` | CPU request | `250m` |
| `resources.requests.memory` | Memory request | `256Mi` |

### Autoscaling Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `autoscaling.enabled` | Enable HPA | `false` |
| `autoscaling.minReplicas` | Minimum replicas | `2` |
| `autoscaling.maxReplicas` | Maximum replicas | `10` |
| `autoscaling.targetCPUUtilizationPercentage` | CPU target | `80` |

## Example Configurations

### Development Environment

```yaml
# dev-values.yaml
replicaCount: 1
resources:
  limits:
    cpu: 200m
    memory: 256Mi
  requests:
    cpu: 100m
    memory: 128Mi
service:
  type: NodePort
```

### Production Environment

```yaml
# prod-values.yaml
replicaCount: 5
autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 20
  targetCPUUtilizationPercentage: 70
ingress:
  enabled: true
  className: nginx
  hosts:
    - host: currency-converter.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: currency-converter-tls
      hosts:
        - currency-converter.example.com
podDisruptionBudget:
  enabled: true
  minAvailable: 2
```

### High Availability Setup

```yaml
# ha-values.yaml
replicaCount: 3
affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      podAffinityTerm:
        labelSelector:
          matchExpressions:
          - key: app.kubernetes.io/name
            operator: In
            values:
            - currency-converter
        topologyKey: kubernetes.io/hostname
```

## Deployment Examples

### Basic Deployment

```bash
helm install currency-converter ./helm/currency-converter
```

### Development Deployment

```bash
helm install currency-converter ./helm/currency-converter \
  --set replicaCount=1 \
  --set service.type=NodePort \
  --set resources.limits.memory=256Mi
```

### Production Deployment

```bash
helm install currency-converter ./helm/currency-converter \
  --set replicaCount=5 \
  --set autoscaling.enabled=true \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=currency-converter.example.com
```

### Staging with Custom Image

```bash
helm install currency-converter ./helm/currency-converter \
  --set image.repository=myregistry/currency-converter \
  --set image.tag=v1.2.0 \
  --set replicaCount=2
```

## Monitoring and Observability

The chart includes:
- **Health checks**: Liveness and readiness probes
- **Resource monitoring**: CPU and memory metrics
- **Pod disruption budget**: Ensures availability during updates
- **Horizontal Pod Autoscaler**: Automatic scaling based on metrics

## Security Features

- **Non-root containers**: Runs with unprivileged user
- **Security contexts**: Dropped capabilities and read-only filesystem options
- **Service accounts**: Dedicated service account for the application
- **Network policies**: Optional network segmentation (when enabled)

## Troubleshooting

### Check Pod Status

```bash
kubectl get pods -l app.kubernetes.io/name=currency-converter
```

### View Logs

```bash
kubectl logs -l app.kubernetes.io/name=currency-converter
```

### Test Health Endpoint

```bash
kubectl port-forward svc/currency-converter 8080:80
curl http://localhost:8080/health
```

### Debug Deployment

```bash
helm get values currency-converter
helm get manifest currency-converter
```

## Chart Development

### Lint Chart

```bash
helm lint ./helm/currency-converter
```

### Template Rendering

```bash
helm template currency-converter ./helm/currency-converter
```

### Package Chart

```bash
helm package ./helm/currency-converter
```

## Support

For issues and questions:
- Check the application logs
- Verify resource quotas and limits
- Ensure the Docker image is available
- Review Kubernetes events: `kubectl get events`