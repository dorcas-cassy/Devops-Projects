# Terraform AWS Network Foundation

Reusable VPC foundation for a small application: two public subnets, two private subnets, an Internet gateway, public route table, and explicit tags.

```sh
terraform init
terraform fmt -check
terraform validate
terraform plan -var 'project_name=portfolio'
```

This project is intentionally network-only: it does not create billable compute or NAT gateways by default.
