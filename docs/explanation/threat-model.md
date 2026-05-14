# Threat Model

Primary risks:

- Mutable GitHub Action tags.
- Privileged `pull_request_target` workflows reading attacker-controlled PR content.
- Caller overlays modifying framework implementation files.
- Floating Galaxy collection or role versions.
- Accidental credential use in the reference framework.

Controls:

- OPA enforces workflow SHA pinning and `pull_request_target` isolation.
- Overlay helper scripts restrict destinations and reject symlinks and path traversal.
- `tools/check_ansible_requirements.py` rejects floating Galaxy versions.
- The reference inventory uses localhost and the reference playbook uses `become: false`.
- Release evidence captures validation output for published versions.

