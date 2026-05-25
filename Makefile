PYTHON ?= python3
INTEGRATION_CASE ?= reference

.PHONY: help setup lint ansible-lint syntax check ruff yamllint test workflow-helper-tests opa-test opa-policy manifest-check docs-layout adr-schema policy docs-check integration ci verify

help:
	@printf "Targets:\n"
	@printf "  setup          Install local Python and Ansible tooling\n"
	@printf "  lint           Run Ansible, Python, and YAML checks\n"
	@printf "  test           Run fast Python assertions\n"
	@printf "  policy         Run OPA tests and policy evaluation\n"
	@printf "  docs-check     Check docs layout and ADR schema\n"
	@printf "  integration    Run the credential-free localhost playbook\n"
	@printf "  ci             Run the repo-local quality gate\n"
	@printf "  verify         Run ci plus integration\n"

setup:
	$(PYTHON) -m pip install --upgrade -r requirements-dev.txt

ansible-lint:
	ansible-lint -c .ansible-lint ansible examples

syntax:
	ansible-playbook -i ansible/inventory/localhost.yml ansible/playbooks/site.yml --syntax-check -e @examples/reference/framework-vars.yml

check:
	ansible-playbook -i ansible/inventory/localhost.yml ansible/playbooks/site.yml --check -e @examples/reference/framework-vars.yml

ruff:
	$(PYTHON) tools/verify.py ruff

yamllint:
	$(PYTHON) tools/verify.py yamllint

test:
	$(PYTHON) tools/verify.py test

workflow-helper-tests:
	$(PYTHON) tools/verify.py workflow-helper-tests

opa-test:
	opa test policies/opa

opa-policy:
	$(PYTHON) tools/verify.py opa-policy

manifest-check:
	$(PYTHON) tools/verify.py manifest-check

docs-layout:
	$(PYTHON) tools/verify.py docs-layout

adr-schema:
	$(PYTHON) tools/verify.py adr-schema

lint:
	$(MAKE) ansible-lint
	$(MAKE) syntax
	$(MAKE) check
	$(MAKE) ruff
	$(MAKE) yamllint

policy:
	$(MAKE) opa-test
	$(MAKE) opa-policy

docs-check:
	$(MAKE) docs-layout
	$(MAKE) adr-schema

integration:
	$(PYTHON) tools/verify.py integration --case $(INTEGRATION_CASE)

ci:
	$(PYTHON) tools/verify.py ci

verify:
	$(PYTHON) tools/verify.py verify --case $(INTEGRATION_CASE)

