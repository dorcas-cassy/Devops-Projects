# DevSecOps Pipeline

Security gates for this repository: secret detection, Terraform IaC scanning, and dependency review. Findings are visible in the workflow log and should be reviewed before merge.

The workflow runs on pull requests and changes to `main`. It intentionally does not auto-remediate or publish secrets.
