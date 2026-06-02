# Tutorial: Derive Your First Ansible Framework

This tutorial walks through creating a new Ansible framework repository from this template. By the end you will have a working framework that passes all CI gates, has an inventory, a role, and can be called by a Terraform or Packer repo through the reusable workflow.

## Prerequisites

- Python 3.12+
- ansible-core 2.18.6 (or the version pinned in `requirements-dev.txt`)
- ansible-lint 25.6.1
- OPA 1.10.0
- shellcheck
- bats

Install the toolchain:

```sh
make setup
```

## Step 1 — Create The Repo From The Template

Use the GitHub UI or the CLI to create a new repository from `NWarila/ansible-framework-template`. Name the new repo after the system it will configure, for example `my-platform-ansible`.

Clone it locally:

```sh
git clone https://github.com/<owner>/my-platform-ansible
cd my-platform-ansible
```

## Step 2 — Confirm The Reference Framework Passes

Before changing anything, verify the reference framework is intact:

```sh
make setup
python tools/verify.py ci
python tools/verify.py integration
```

All checks should pass. The integration run writes evidence under `.tmp/ansible-framework/` and exits 0.

## Step 3 — Replace The Baseline Role

The `baseline` role validates variables and writes evidence. It is the minimal role that proves the controller can load the full Ansible stack. For most real frameworks you will add a new role alongside it rather than deleting it.

Create your first real role by copying the `example_nginx` structure:

```sh
cp -r ansible/roles/example_nginx ansible/roles/my_service
```

Edit the copies:

1. Rename all `example_nginx_` fact and variable prefixes to `my_service_`.
2. Replace the nginx package steps in `tasks/present_linux.yml` (and the OS variants) with your service's steps.
3. Update `defaults/main.yml` with your service's default configuration keys.
4. Update `meta/main.yml` with the correct role name and description.
5. Update `ansible/playbooks/site.yml` to include the new role.

Keep `tasks/main.yml` structurally identical to the template's canonical loader. That is the file reviewed for privilege and trust boundaries; do not add application logic to it.

## Step 4 — Update Inventory And Variables

Edit `ansible/inventory/localhost.yml` if you need additional host groups. For a real framework targeting remote hosts, add a new inventory file. The `localhost.yml` reference inventory remains for CI validation.

Add a matching example input under `examples/reference/`:

```sh
cp examples/reference/framework-vars.yml examples/reference/my-service-vars.yml
```

Edit the example to match the variable schema your new role expects.

## Step 5 — Update The Ansible Requirements

If your role depends on Galaxy collections or roles, add exact pins to `ansible/requirements.yml`:

```yaml
collections:
  - name: community.general
    version: "10.1.0"
```

Ranged versions are rejected by `tools/check_ansible_requirements.py`. Renovate will propose individual pin bumps through pull requests.

## Step 6 — Run The Full Gate

```sh
python tools/verify.py ci
```

This runs ansible-lint, syntax check, Python tooling, YAML checks, OPA policy, docs layout, ADR schema, workflow helper tests, and the manifest check.

Fix any failures before proceeding. Common first failures:

- `ansible-lint` complains about missing `name:` on tasks — add a name to every task.
- `check_ansible_requirements.py` rejects a ranged version — replace it with an exact pin.

## Step 7 — Add A Repo ADR

Document the first design decision that is specific to this repository. Copy the ADR schema from an existing template ADR and save it as `docs/decision-records/repo/0001-<slug>.md`. Add a row to `docs/decision-records/README.md` so the index stays current.

The ADR schema check (`tools/check_adr_schema.py`) validates that all required sections are present and in order.

## Step 8 — Wire Up A Caller

To call this framework from a Terraform or Packer repo, add the reusable workflow call to the caller repo. Pin to the exact commit SHA of the release you want:

```yaml
jobs:
  configure:
    uses: <owner>/my-platform-ansible/.github/workflows/reusable-ansible-framework-run.yaml@<40-char-sha>
    with:
      framework_ref: <40-char-sha>
      inventory: ansible/inventory/localhost.yml
      extra_vars_file: examples/reference/my-service-vars.yml
```

The reusable workflow validates the ref match, applies any overlays from the caller repo into the allowed Ansible data paths, and runs the playbook. See `docs/reference/runner-protocol.md` for the full caller contract.

## Next Steps

- Replace `README.md` and repo-specific docs to describe your real framework.
- Add OS-specific task files as you support more distributions.
- Add template ADRs under `docs/decision-records/template/` for decisions that downstream frameworks should inherit.
- Consult `docs/reference/mirroring.md` for files that derivative frameworks must keep byte-identical with this template.
