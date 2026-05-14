# Testing Strategy

The testing strategy has four layers:

1. Static workflow and shell validation through actionlint, ShellCheck, and Bats.
2. Ansible validation through ansible-lint and `ansible-playbook --syntax-check`.
3. Policy validation through OPA and Python checks for Ansible requirements pins.
4. Credential-free integration through a localhost playbook run that generates evidence under `.tmp/ansible-framework/`.

The reference integration is intentionally narrow. It proves the framework shape and reusable workflow contract without requiring a VM, SSH target, or cloud account.

