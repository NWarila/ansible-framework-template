# ADR-template/0004: Isolate Pull Request Target Triggers

| Field          | Value                                   |
| -------------- | --------------------------------------- |
| Status         | Accepted                                |
| Date           | 2026-05-14                              |
| Authors        | Nick Warila (@NWarila)                  |
| Decision-maker | Nick Warila (sole portfolio maintainer) |
| Consulted      | zizmor and existing template OPA policy |
| Informed       | Derivative Ansible frameworks           |
| Reversibility  | Medium                                  |
| Review-by      | N/A (Accepted)                          |

## TL;DR

`pull_request_target` is allowed only for the narrow trusted-bot auto-merge surface.

## Context and Problem Statement

`pull_request_target` runs with base-repository privileges. That is useful for enabling auto-merge for trusted dependency bots, but dangerous for validation, release, or Ansible execution paths that could read attacker-controlled PR content.

## Decision Drivers

1. Least privilege.
2. Review locality.
3. Artifact integrity.
4. Consumer safety.
5. Machine enforcement through OPA.

## Considered Options

1. Allow `pull_request_target` wherever workflow authors find it useful.
2. Ban `pull_request_target` entirely.
3. Isolate `pull_request_target` to `auto-merge.yaml`.

## Decision Outcome

Chosen option: **Option 3, isolate `pull_request_target` to auto-merge.**

Release, CI, reusable Ansible execution, and evidence workflows must stay on ordinary events or `workflow_call`.

## Pros and Cons of the Options

### Option 1: Broad allowance

- Good, because it is flexible.
- Bad, because privileged PR workflows are easy to misuse.

### Option 2: Complete ban

- Good, because it removes the trigger class.
- Bad, because trusted dependency-bot auto-merge loses a safe automation path.

### Option 3: Isolated auto-merge

- Good, because the privileged PR event has one narrow purpose.
- Good, because OPA can enforce the allowlist.
- Bad, because future exceptions require a superseding ADR.

## Confirmation

1. `.github/workflows/auto-merge.yaml` is the only workflow allowed to use `pull_request_target`.
2. `reusable-auto-merge.yaml` must not check out PR code or read PR-controlled content.
3. OPA enforces both rules against committed workflow files.
4. Release and Ansible execution workflows must not use `pull_request_target`.

## Consequences

### Positive

- The workflow trust model is easier to review.
- Derivative frameworks inherit a safer default.

### Negative

- A real future exception requires an ADR update.

### Neutral

- Trusted-bot auto-merge remains available.

## Assumptions

1. Release and validation workflows do not require privileged PR context.
2. Trusted dependency bots remain the only auto-merge principals.

## Supersedes

None.

## Superseded by

None (current).

## Implementing PRs

Initial template implementation.

## Related ADRs

- [Template ADR-0001](0001-pin-ansible-and-collection-versions-exactly.md)
- [Org ADR-0004](../org/0004-use-renovate-for-dependency-updates.md)

## Compliance Notes

None.

