# Release Gates

PRs to `main` must pass:

- `actionlint`
- workflow helper tests
- markdownlint
- `ansible verify`
- drift gate against the org baseline
- Trivy, Gitleaks, and zizmor
- CodeQL

OpenSSF Scorecard runs on push, branch-protection, schedule, and manual paths;
it is skipped on PR and merge queue because private-repo Scorecard GraphQL
access is not reliable.

Release candidates must also pass release evidence before publishing a versioned release. Release evidence records Ansible linting, reference integration, OPA policy evaluation, docs layout checks, and the generated reference evidence bundle.
