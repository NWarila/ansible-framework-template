# Reference Integration Fixture

The reference case runs `ansible/playbooks/site.yml` against the local inventory and passes `examples/reference/framework-vars.yml`.

It must remain credential-free: no SSH target, no cloud account, no `become`, and no writes outside `.tmp/ansible-framework/`.

