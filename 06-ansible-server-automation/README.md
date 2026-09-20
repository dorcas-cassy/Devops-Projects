# Ansible Linux Web-Server Automation

Idempotent role that installs Nginx, creates a portfolio status page, enables the service, and permits HTTP through UFW when it is available.

```sh
ansible-playbook -i inventory/hosts.ini playbooks/site.yml --check
ansible-playbook -i inventory/hosts.ini playbooks/site.yml
```

Set the inventory host to an authorized Ubuntu/Debian lab server. Do not place passwords or private keys in this repository.
