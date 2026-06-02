# ansible-framework-template

[![CI](https://github.com/NWarila/ansible-framework-template/actions/workflows/ci.yaml/badge.svg)](https://github.com/NWarila/ansible-framework-template/actions/workflows/ci.yaml)
[![Security](https://github.com/NWarila/ansible-framework-template/actions/workflows/security.yaml/badge.svg)](https://github.com/NWarila/ansible-framework-template/actions/workflows/security.yaml)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/NWarila/ansible-framework-template/badge)](https://securityscorecards.dev/viewer/?uri=github.com/NWarila/ansible-framework-template)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Canonical template for Ansible framework repositories: repos that own reusable configuration contracts, validation tooling, release evidence, and caller integration patterns for Terraform and Packer workflows.

System context diagram: [docs/diagrams/architecture.mmd](docs/diagrams/architecture.mmd) — rendered in [docs/explanation/architecture.md](docs/explanation/architecture.md).

The reference framework is intentionally credential-free. It targets `localhost` with `ansible_connection: local`, writes evidence under `.tmp/ansible-framework/`, and never uses `become`. Real frameworks replace the baseline role with operating-system, application, or platform-specific roles while keeping the same repo-quality surface.

## Prerequisites

Install the same external tools CI uses before running the full local gates:

- Python 3.12+
- ansible-core 2.18.6
- ansible-lint 25.6.1
- OPA 1.10.0
- shellcheck
- bats

## Quickstart

```sh
make help
make setup
python tools/verify.py ci
python tools/verify.py integration
```

`python tools/verify.py ci` runs Ansible linting, syntax checks, Python tooling, YAML checks, OPA policy, docs layout, ADR schema, workflow helper tests, and manifest checks. `python tools/verify.py integration` executes the credential-free localhost playbook and asserts the generated evidence.

The complete gate inventory lives in [`docs/reference/quality-gates.md`](docs/reference/quality-gates.md).

## Ansible Framework Shape

| File | Role |
| --- | --- |
| [`ansible.cfg`](ansible.cfg) | Framework-local Ansible defaults. |
| [`ansible/requirements.yml`](ansible/requirements.yml) | Galaxy collection and role pins. Empty by default, exact pins required when populated. |
| [`ansible/inventory/localhost.yml`](ansible/inventory/localhost.yml) | Credential-free reference inventory. |
| [`ansible/playbooks/site.yml`](ansible/playbooks/site.yml) | Reference entrypoint playbook. |
| [`ansible/roles/baseline/`](ansible/roles/baseline/) | Minimal role that validates variables and writes integration evidence. |
| [`ansible/roles/example_nginx/`](ansible/roles/example_nginx/) | Production-shaped example role with OS normalization, package install, templates, handlers, and lifecycle states. |
| [`examples/reference/framework-vars.yml`](examples/reference/framework-vars.yml) | Example framework input used by CI. |

## Normalized Repo Interface

| Command | Purpose |
| --- | --- |
| `make lint` | Ansible lint/syntax plus Python and workflow YAML checks. |
| `make policy` | OPA policy tests plus source-aware policy evaluation. |
| `make docs-check` | Diataxis and ADR documentation layout checks. |
| `python tools/verify.py ci` | Repo-local quality gate. |
| `python tools/verify.py integration` | Credential-free localhost playbook run. |
| `python tools/verify.py verify` | Full local verification: `ci` plus `integration`. |

To exercise the reference run directly:

```sh
ansible-playbook \
  -i ansible/inventory/localhost.yml \
  ansible/playbooks/site.yml \
  -e @examples/reference/framework-vars.yml
```

## Deriving A Real Framework

For a real Ansible framework derived from this template, edit these first:

1. `README.md` and repo-specific docs.
2. `ansible/roles/` and `ansible/playbooks/site.yml`. Use `ansible/roles/example_nginx/` as the role-format reference.
3. `ansible/requirements.yml` with exact collection/role pins.
4. `examples/` for safe local and CI inputs.
5. `docs/decision-records/repo/` for local decisions.

The mirroring rules live in [`docs/reference/mirroring.md`](docs/reference/mirroring.md). Terraform and Packer callers should follow the pinned checkout, overlay, inventory, and release-evidence protocol in [`docs/reference/runner-protocol.md`](docs/reference/runner-protocol.md).

## License

MIT - see [LICENSE](LICENSE).
