package repo_hygiene_test

import data.repo_hygiene
import rego.v1

test_sha_pinned_action_allowed if {
	count(repo_hygiene.deny) == 0 with input as {
		"workflows": {"ci.yml": [{"line": 12, "uses": "actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd"}]},
		"files": {"ansible.cfg": "host_key_checking = True\nretry_files_enabled = False\n"},
	}
}

test_tag_pinned_action_denied if {
	denials := repo_hygiene.deny with input as {
		"workflows": {"ci.yml": [{"line": 7, "uses": "actions/checkout@v6"}]},
		"files": {"ansible.cfg": "host_key_checking = True\n"},
	}
	count(denials) >= 1
}

test_local_ref_allowed if {
	count(repo_hygiene.deny) == 0 with input as {
		"workflows": {"ci.yml": [{"line": 5, "uses": "./.github/actions/setup"}]},
		"files": {},
	}
}

test_docker_without_digest_denied if {
	denials := repo_hygiene.deny with input as {
		"workflows": {"ci.yml": [{"line": 4, "uses": "docker://ghcr.io/example/tool:v1.0.0"}]},
		"files": {},
	}
	count(denials) >= 1
}

test_pull_request_target_checkout_denied if {
	denials := repo_hygiene.deny with input as {
		"workflows": {},
		"files": {".github/workflows/auto-merge.yaml": `on:
  pull_request_target:
    types: [opened]
jobs:
  dangerous:
    steps:
      - uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd`},
	}
	count(denials) >= 1
}

test_release_workflow_pull_request_target_denied if {
	denials := repo_hygiene.deny with input as {
		"workflows": {},
		"files": {".github/workflows/release.yaml": "on:\n  pull_request_target:\n"},
	}
	count(denials) >= 1
}

test_host_key_checking_false_denied if {
	denials := repo_hygiene.deny with input as {
		"workflows": {},
		"files": {"ansible.cfg": "host_key_checking = False\n"},
	}
	count(denials) >= 1
}

test_retry_files_enabled_true_denied if {
	denials := repo_hygiene.deny with input as {
		"workflows": {},
		"files": {"ansible.cfg": "retry_files_enabled = True\n"},
	}
	count(denials) >= 1
}
