# DevOps Portfolio

Hands-on DevOps projects demonstrating infrastructure as code, CI/CD, containerization, Kubernetes, observability, configuration management, and supply-chain security.

| Project | Focus | Evidence to capture |
| --- | --- | --- |
| 01 — Terraform S3 bucket | Existing AWS object-storage deployment | Existing AWS console screenshots |
| [02 — CI/CD Docker app](02-cicd-docker-app/) | Test, build, scan, and publish a container | GitHub Actions run and container health response |
| [03 — Terraform AWS network](03-terraform-aws-network/) | Reusable VPC, subnets, routes, and security boundaries | `terraform plan` and cloud resource view |
| [04 — Kubernetes platform](04-kubernetes-platform/) | Deployment, service, ingress, probes, autoscaling | `kubectl get` output and application response |
| [05 — Observability incident lab](05-observability-incident-lab/) | Prometheus, Grafana, alerting, and incident response | Grafana dashboard and alert state |
| [06 — Ansible server automation](06-ansible-server-automation/) | Idempotent Linux/web-server configuration | Playbook recap and served site |
| [07 — DevSecOps pipeline](07-devsecops-pipeline/) | Dependency, secret, IaC, and image scanning gates | Security workflow run and findings summary |
| [08 — AI Kubernetes agent foundation](08-ai-kubernetes-troubleshooting-agent/) | Dockerized FastAPI and Next.js monorepo | Health endpoint and starter UI |

## Portfolio standard

Each project is designed to be runnable and should include real screenshots from your own execution. Never publish `.env` files, cloud credentials, Terraform state, or unredacted production logs.
