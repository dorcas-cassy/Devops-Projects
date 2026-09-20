# Security baseline

- No credentials, state files, keys, or `.env` files may be committed.
- Infrastructure changes require a reviewed Terraform plan.
- Container images must be built from pinned base-image tags and scanned in CI.
- High-confidence secrets are merge blockers and require rotation, not only deletion.
