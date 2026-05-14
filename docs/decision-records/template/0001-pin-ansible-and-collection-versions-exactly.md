# ADR-template/0001: Pin Ansible And Collection Versions Exactly

| Field          | Value                                   |
| -------------- | --------------------------------------- |
| Status         | Accepted                                |
| Date           | 2026-05-14                              |
| Authors        | Nick Warila (@NWarila)                  |
| Decision-maker | Nick Warila (sole portfolio maintainer) |
| Consulted      | Terraform and Packer template baselines |
| Informed       | Derivative Ansible frameworks           |
| Reversibility  | Medium                                  |
| Review-by      | N/A (Accepted)                          |

## TL;DR

Ansible controller tooling, Galaxy collections, and Galaxy roles are pinned exactly.

## Context and Problem Statement

Configuration management code can change behavior when controller packages or Galaxy dependencies drift. Framework templates must make dependency movement explicit and reviewable.

## Decision Drivers

1. Reproducible CI.
2. Reviewable dependency movement.
3. Consistency with the Terraform and Packer template family.
4. Safe downstream reuse by Terraform and Packer callers.

## Considered Options

1. Exact pins for controller packages and Galaxy dependencies.
2. Semver ranges for Galaxy dependencies.
3. Floating latest versions.

## Decision Outcome

Chosen option: **Option 1, exact pins.**

Controller packages are pinned in `requirements-dev.txt` and workflows. Galaxy dependencies are pinned in `ansible/requirements.yml`; git roles must pin to commit SHAs.

## Pros and Cons of the Options

### Option 1: Exact pins

- Good, because CI is reproducible.
- Good, because Renovate can propose one reviewed movement at a time.
- Bad, because routine upgrades require pull requests.

### Option 2: Semver ranges

- Good, because compatible updates can arrive quickly.
- Bad, because behavior can change without review.

### Option 3: Floating latest

- Good, because it has the least maintenance friction.
- Bad, because it is not reproducible.

## Confirmation

1. `requirements-dev.txt` pins Ansible tooling exactly.
2. `tools/check_ansible_requirements.py` rejects missing or ranged Galaxy versions.
3. CI runs the requirements check.
4. Renovate is configured to keep pins current through reviewed PRs.

## Consequences

### Positive

- Framework and caller runs are easier to reproduce.
- Dependency updates are visible in review.

### Negative

- Dependency maintenance is explicit work.

### Neutral

- Derivative frameworks may add dependencies, but they inherit the same pinning rule.

## Assumptions

1. Renovate remains the normal dependency update mechanism.
2. Derivative frameworks record local exceptions in repo ADRs.

## Supersedes

None.

## Superseded by

None (current).

## Implementing PRs

Initial template implementation.

## Related ADRs

- [Org ADR-0004](../org/0004-use-renovate-for-dependency-updates.md)

## Compliance Notes

None.

