# Architecture

The template separates the Ansible implementation from the repo-quality surface.

The repo-quality surface includes workflow pinning, security scans, OPA policy, documentation layout, ADR schema checks, and release evidence. These files are mirrored by derivative frameworks through the baseline manifest.

The Ansible implementation lives under `ansible/`. The reference role is deliberately small: it validates variables and writes evidence. That keeps CI credential-free while still proving that the controller can load inventory, variables, roles, templates, and playbooks.

Callers such as Terraform and Packer repos use the reusable workflow to check out this framework, overlay caller-owned data into safe Ansible paths, install the pinned Ansible toolchain, lint, syntax-check, and run the playbook.

