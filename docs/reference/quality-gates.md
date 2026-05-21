# Quality Gates

Each automated check enforced by this repository plays one of four roles. The
role determines *when* the check runs and *what failure means*.

| Role | Meaning | When it runs |
| --- | --- | --- |
| **Blocking** | Required for PR merge to `main`. Failure blocks the PR. | `pull_request` / `merge_group` triggers in `ci.yaml`, `drift-gate.yaml`, `security.yaml` |
| **Scheduled** | Periodic posture telemetry. Runs on a cron; does **not** block PRs. | `schedule` trigger in `security.yaml` |
| **Release** | Runs at release-cut time. Failure blocks the release tag and prevents the evidence bundle from being attached. | `release.yaml` and the reusables it calls |
| **Advisory** | Surfaces signal without blocking. Reserved for steps whose *publishing channel* is best-effort, or where the gate is explicitly opt-in. | Specific steps marked `continue-on-error: true` (see below) |

## Gate inventory

| Gate | Source | Role | Notes |
| --- | --- | --- | --- |
| ansible verify (`verify.py verify`) | `ci.yaml` job running `verify.py verify` | Blocking | Wraps `ansible-lint`, syntax check, `ansible-playbook --check`, ruff, yamllint, requirements/test checks, OPA (test + repo-hygiene), `workflow-helper-tests`, `privileged-workflows`, docs-layout, ADR schema, manifest, integration. |
| ansible-lint | `verify.py ansible-lint` | Blocking | Enforces proven Ansible practices. Necessary, not sufficient; see "What is intentionally not yet a gate" below. |
| syntax / check-mode | `verify.py syntax` and `verify.py check` | Blocking | `ansible-playbook --syntax-check` and `--check`. Catches structural and module-resolution errors without touching real hosts. |
| workflow-helper-tests | `verify.py workflow-helper-tests` (in `ci` target) | Blocking | ShellCheck on `tools/ci/*.sh`, Python workflow-input checks, Bats coverage. |
| privileged-workflows | `verify.py privileged-workflows` (in `ci` target) | Blocking | `check_privileged_workflows.py` + fixture-driven test runner. Rejects `actions/checkout` and PR-controlled refs in any `pull_request_target` workflow, transitively through local reusables. |
| drift-gate | `drift-gate.yaml` | Blocking | Verifies the org-baseline overlay matches `NWarila/.github` at the pinned source ref. |
| Trivy IaC misconfig + secrets | `security.yaml` -> `reusable-iac-security.yaml` (PR path) | Blocking | Trivy scan exit status is the gate; SARIF upload is advisory. |
| Gitleaks | `security.yaml` -> `reusable-iac-security.yaml` | Blocking by default | Caller-configurable via `inputs.gitleaks_advisory`. |
| zizmor (Actions posture) | `security.yaml` -> `reusable-iac-security.yaml` | Blocking | Exit status is the gate; SARIF upload is advisory. |
| CodeQL | `security.yaml` -> `reusable-codeql.yaml` | Blocking | SARIF upload is advisory. |
| OpenSSF Scorecard | `security.yaml` -> `reusable-scorecard.yaml` | Scheduled / push / branch protection / manual; skipped on PR and merge queue | Posture telemetry; skipped on PR paths because Scorecard GraphQL is gated on private repos. |
| Release evidence + SBOM + attestations | `release.yaml` -> `reusable-release-evidence.yaml` | Release | Bundles rendered playbook/role inventory, SBOM, attestations. |
| Auto-merge (trusted bots) | `auto-merge.yaml` -> `reusable-auto-merge.yaml` | Not a gate | Operates on `pull_request_target` with no PR checkout; must keep passing `privileged-workflows`. |

## What is intentionally **not yet** a gate

Ansible quality is about idempotence, OS normalization, and cleanup;
lint and syntax-check alone are necessary but not sufficient. The
following are deliberately gaps to be closed by a separate workstream
(scheduled containerised role tests), not by stretching the PR path:

- **Containerised role tests.** Running each shipped role (e.g.,
  `example_nginx`) inside Debian-family and RHEL-family containers, with
  the standard lifecycle of `present` -> `present` (idempotence) ->
  `absent` -> clean. Belongs on a scheduled `deep-validation.yaml`, not
  on the PR critical path, because it requires Docker and additional
  runtime.
- **Negative-input playbook tests.** Bad `state:`, unsupported overlays,
  invalid var types must fail-fast. Will be added under
  `tests/fixtures/` once the containerised harness lands.

Until those tests exist, the documentation must not claim the shipped
roles are fully tested; only that they pass lint, syntax, and
check-mode against the reference inventory.

## When `continue-on-error: true` is allowed

The repository deliberately limits this flag to three narrow contexts.
Anywhere else, it would mask a gate's failure and should be removed.

1. **SARIF upload to GitHub Security** (`reusable-iac-security.yaml`,
   `reusable-codeql.yaml`, `reusable-scorecard.yaml`) -- the *scan* is the
   gate and runs without `continue-on-error`. The upload step is
   best-effort because publishing to the Security tab requires GitHub
   Advanced Security on private repos. Findings remain visible in the run
   log and as workflow artifacts.
2. **Scorecard analysis on private repos** (`reusable-scorecard.yaml`) --
   Scorecard's GraphQL queries fail with *Resource not accessible by
   integration* on private repositories.
3. **Gitleaks advisory mode** (`reusable-iac-security.yaml`) -- caller-
   parameterised via `inputs.gitleaks_advisory`.

## Adding a new gate

1. Decide its role from the taxonomy above.
2. If the gate is reproducible locally, wire it through `tools/verify.py`.
3. Add a row to the inventory table.
4. If blocking, ensure it appears in the repository's required status
   checks (branch protection on `main`).
5. Do not add `continue-on-error: true` outside the three contexts listed
   above without an explicit rationale in the workflow file.
