# Develop This Module

## Local Setup

```sh
make setup
```

Install OPA, ShellCheck, and Bats when running the full local gate.

## Development Loop

```sh
python tools/verify.py test
python tools/verify.py docs-check
python tools/verify.py ci
```

Use `python tools/verify.py integration` when `ansible-playbook` is available. It writes generated evidence under `.tmp/ansible-framework/`.

## Before Opening A PR

```sh
python tools/verify.py verify
```

If external tools are missing locally, run the specific targets that are available and rely on GitHub CI for the full Linux toolchain.

