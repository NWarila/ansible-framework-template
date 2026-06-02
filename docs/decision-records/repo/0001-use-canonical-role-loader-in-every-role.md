# ADR-repo/0001: Use Canonical Role-Loader In Every Role

| Field          | Value                                   |
| -------------- | --------------------------------------- |
| Status         | Accepted                                |
| Date           | 2026-06-02                              |
| Authors        | Nick Warila (@NWarila)                  |
| Decision-maker | Nick Warila (sole portfolio maintainer) |
| Consulted      | Packer and Terraform template baselines |
| Informed       | Derivative Ansible frameworks           |
| Reversibility  | Medium                                  |
| Review-by      | N/A (Accepted)                          |

## TL;DR

Every Ansible role in this framework carries an identical `tasks/main.yml` that handles variable loading, OS resolution, state validation, and cleanup. Application behavior lives exclusively in OS- and state-scoped task files, never in the loader itself.

## Context and Problem Statement

Ansible roles commonly merge variable loading, OS branching, and application logic into a single `tasks/main.yml`. As roles grow, that file becomes the hardest to read, hardest to test, and hardest to audit, because every concern is interleaved. Derivative frameworks copying roles from this template need a consistent structure they can rely on without reading every line.

## Decision Drivers

1. Reviewability: a maintainer should be able to audit the loader separately from application logic.
2. Consistency: every role in a framework (and every framework derived from this template) should present the same entry-point shape.
3. Testability: the loader pattern is exercised once; OS- and state-scoped files can be tested or replaced independently.
4. Safe credential handling: variable loading must be centralized so `no_log` coverage is applied uniformly.

## Considered Options

1. Canonical loader copied verbatim into every role; application behavior in OS/state task files.
2. A shared role or module that other roles call via `include_role`.
3. No enforced structure; each role author decides independently.

## Decision Outcome

Chosen option: **Option 1, canonical loader copied verbatim into each role.**

The loader is the first thing a reviewer reads. Making it structurally identical across all roles lets reviewers quickly confirm it has not been tampered with. The inline copy also means the role is self-contained and works without a shared dependency that could drift or fail separately.

## Pros and Cons of the Options

### Option 1: Verbatim copy per role

- Good, because each role is self-contained and readable without cross-referencing other roles.
- Good, because the loader shape is reviewable by pattern-matching, not by reading arbitrary logic.
- Good, because derivative frameworks inherit the pattern without an extra runtime dependency.
- Bad, because bug fixes to the loader must be propagated to every role copy.

### Option 2: Shared role or module

- Good, because loader logic exists in one place.
- Bad, because roles gain a hidden runtime dependency that can drift or fail at collection-install time.
- Bad, because `include_role` adds indirection that is harder to trace in CI output.

### Option 3: No enforced structure

- Good, because each role author has full flexibility.
- Bad, because frameworks become inconsistent; reviewers must read every `tasks/main.yml` from scratch.

## Confirmation

1. `ansible/roles/example_nginx/tasks/main.yml` contains the full canonical loader: input validation, OS fact gathering, OS-candidate resolution, overlay loading, user-override application, state resolution, state validation, password scoping, temp-directory management, OS task dispatch, and cleanup.
2. Application behavior (`present`, `absent`, `clean` states; Debian/RedHat variants) lives exclusively in the companion task files.
3. The comment at the top of `ansible/roles/example_nginx/tasks/main.yml` explicitly instructs: "Keep role-specific NGINX behavior in state/OS task files, not here."
4. Derivative frameworks that add new roles must follow the same structure; the baseline role (`ansible/roles/baseline/`) is the minimal degenerate case (no OS branching required).

## Consequences

### Positive

- Reviewers can audit the loader across all roles in a single pass.
- OS and state behavior is isolated in small, focused files.
- The pattern is teachable: new contributors can read `example_nginx/tasks/main.yml` to understand the full contract.

### Negative

- Loader bug fixes require touching every role copy.
- Roles carry more boilerplate than strictly necessary for simple use cases.

### Neutral

- The `baseline` role is the sanctioned exception: it has no OS branching or state dispatch because it only validates variables and writes evidence.

## Assumptions

1. Roles in derivative frameworks are complex enough to benefit from the separation.
2. The loader pattern evolves slowly enough that manual propagation is manageable.

## Supersedes

None.

## Superseded by

None (current).

## Implementing PRs

Initial template implementation (see `example_nginx` role).

## Related ADRs

- [Template ADR-0001](../template/0001-pin-ansible-and-collection-versions-exactly.md)
- [Template ADR-0002](../template/0002-keep-reference-framework-credential-free.md)

## Compliance Notes

None.
