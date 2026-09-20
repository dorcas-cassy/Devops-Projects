# Kubernetes Application Platform

Deploys the CI/CD portfolio API with a Deployment, Service, probes, resource requests/limits, and horizontal autoscaling.

```sh
kubectl apply -f k8s/
kubectl get deploy,svc,hpa
kubectl port-forward svc/portfolio-api 8080:80
curl http://localhost:8080/health
```
