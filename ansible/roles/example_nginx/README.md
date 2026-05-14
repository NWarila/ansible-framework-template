# example_nginx

Production-shaped example role for framework authors. It installs and manages
NGINX while demonstrating the role format this template expects real framework
roles to follow.

The role uses a Wazuh-derived loader in `tasks/main.yml`: validate input, gather
only required OS facts, merge defaults, merge OS overlays, merge user overrides,
normalize lifecycle state, resolve the most specific task file, and clean up
scratch state.

## Why NGINX

NGINX is a useful example because it is small enough to understand quickly but
real enough to exercise the framework:

- different package managers across Debian and Red Hat families
- service management
- generated config files and templates
- validation before reload
- lifecycle states for `present`, `absent`, and `clean`
- safe user overrides without replacing the whole defaults tree

## Role Contract

| Path | Purpose |
| --- | --- |
| `defaults/main.yml` | User-facing defaults and schema. |
| `vars/main.yml` | Internal role constants. |
| `vars/<os>.yml` | OS overlays loaded by the shared loader. |
| `tasks/main.yml` | Shared loader. Do not put NGINX behavior here. |
| `tasks/<state>_<os>.yml` | OS-family package and lifecycle entrypoints. |
| `tasks/<state>_linux.yml` | Shared Linux implementation used by each OS family. |
| `templates/*.j2` | Managed NGINX config and content templates. |

## Required Inputs

| Variable | Type | Description |
| --- | --- | --- |
| `ENV` | string | Environment selector used by the overlay loader. |
| `example_nginx.state` | string | Optional lifecycle override: `present`, `absent`, or `clean`. |

## Defaults Pattern

Defaults expose one top-level dictionary named after the role plus `_defaults`.
Callers override the matching role-name dictionary.

```yaml
example_nginx_defaults:
  state: present
  service:
    name: nginx
    enabled: true
    state: started
```

Caller override:

```yaml
example_nginx:
  default_site:
    server_name:
      - app.internal.example
    index_title: Platform landing page
    index_body: Served from the platform Ansible framework.
```

## Overlay Pattern

OS overlays are wrapped in `example_nginx_overlay` so static analysis can tell
that the file is intentional overlay data:

```yaml
example_nginx_overlay:
  package:
    manager: apt
  nginx:
    user: www-data
    group: www-data
```

The loader unwraps and recursively merges overlays into the running config.
User overrides always have the highest precedence.

## Example Play

```yaml
- name: Configure web tier
  hosts: web
  gather_facts: false
  become: true
  vars:
    ENV: lab
    example_nginx:
      default_site:
        server_name:
          - _
        index_body: Built by ansible-framework-template.
  roles:
    - role: example_nginx
```

## Lifecycle

`present` installs NGINX, writes config, validates with `nginx -t`, and starts
the service.

`absent` removes the managed config and optionally removes the package when
`package.remove_on_absent` is true.

`clean` removes role runtime scratch space without uninstalling NGINX.
