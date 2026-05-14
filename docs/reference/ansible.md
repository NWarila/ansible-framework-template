# Ansible Reference

## Controller Contract

The framework runs from a Linux controller with Python 3.12+, ansible-core, and ansible-lint installed from exact pins. The reference inventory uses `ansible_connection: local` so CI can execute without SSH targets or secrets.

## Directory Contract

| Path | Purpose |
| --- | --- |
| `ansible.cfg` | Repository-local Ansible configuration. |
| `ansible/requirements.yml` | Galaxy collections and roles. Empty is allowed; populated entries require exact pins. |
| `ansible/inventory/` | Safe reference inventory and caller overlays. |
| `ansible/playbooks/` | Playbook entrypoints. |
| `ansible/roles/` | Framework-owned role implementation. |
| `ansible/files/`, `ansible/templates/`, `ansible/vars/` | Caller overlay destinations. |
| `ansible/fixtures/runtime/` | Runtime fixtures copied in by caller workflows. |

## Role Contract

Use `ansible/roles/example_nginx/` as the canonical example for application roles.
It demonstrates the Wazuh-derived loader pattern:

- validate required inputs
- gather only required OS facts
- merge defaults, OS overlays, and user overrides
- normalize lifecycle state
- resolve the most specific OS task file
- keep application behavior outside `tasks/main.yml`

The role defaults expose one role-prefixed dictionary, OS overlays live in
`vars/<os>.yml`, and lifecycle task files follow `<state>_<os>.yml`.

## Reference Run

The reference playbook writes evidence under `.tmp/ansible-framework/reference/` and records:

- framework name
- selected profile
- inventory host
- managed file declarations
- `become=false`

Derivative frameworks can add real remote hosts and privileged tasks, but the template reference case must remain credential-free.
