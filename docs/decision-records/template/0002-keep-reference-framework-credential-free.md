# ADR-template/0002: Keep Reference Framework Credential-Free

| Field          | Value                                   |
| -------------- | --------------------------------------- |
| Status         | Accepted                                |
| Date           | 2026-05-14                              |
| Authors        | Nick Warila (@NWarila)                  |
| Decision-maker | Nick Warila (sole portfolio maintainer) |
| Consulted      | Terraform and Packer template baselines |
| Informed       | Derivative Ansible frameworks           |
| Reversibility  | Low                                     |
| Review-by      | N/A (Accepted)                          |

## TL;DR

The reference framework runs against localhost, uses `become: false`, and writes local evidence only.

## Context and Problem Statement

Ansible frameworks usually configure real systems. A template repository must still be runnable by CI and by a new maintainer without SSH, cloud, vault, or privileged host access.

## Decision Drivers

1. Safe public CI.
2. Fast local validation.
3. No secret bootstrap requirement.
4. Clear separation between the reference pattern and real target systems.

## Considered Options

1. Localhost reference playbook with generated evidence.
2. SSH fixture host.
3. Mock Ansible with scripts only.

## Decision Outcome

Chosen option: **Option 1, localhost reference playbook with generated evidence.**

Real frameworks replace or extend roles while keeping the credential-free reference case available for template-level validation.

## Pros and Cons of the Options

### Option 1: Localhost evidence

- Good, because validation requires no external systems.
- Good, because Ansible still parses and runs a real playbook and role.
- Bad, because it does not prove provider-specific remote behavior.

### Option 2: SSH fixture host

- Good, because it is closer to production.
- Bad, because it requires credentials or disposable infrastructure.

### Option 3: Script-only mock

- Good, because it is simple.
- Bad, because it stops testing Ansible itself.

## Confirmation

1. `ansible/inventory/localhost.yml` uses `ansible_connection: local`.
2. `ansible/playbooks/site.yml` sets `become: false`.
3. `python tools/verify.py integration` runs without external credentials.
4. Generated evidence remains untracked under `.tmp/`.

## Consequences

### Positive

- The template is safe to run in public CI.
- Consumers can learn the framework contract before choosing target systems.

### Negative

- Remote host semantics must be tested in derivative frameworks.

### Neutral

- The reusable workflow supports caller-provided inventory for real frameworks.

## Assumptions

1. Derivative frameworks add target-specific tests.
2. Local generated evidence is enough for template-level validation.

## Supersedes

None.

## Superseded by

None (current).

## Implementing PRs

Initial template implementation.

## Related ADRs

- [Template ADR-0001](0001-pin-ansible-and-collection-versions-exactly.md)

## Compliance Notes

None.

