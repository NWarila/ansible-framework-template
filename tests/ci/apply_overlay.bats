#!/usr/bin/env bats

setup() {
  repo_root="$(cd "${BATS_TEST_DIRNAME}/../.." && pwd)"
  script="${repo_root}/tools/ci/apply_overlay.sh"
  tmp_root="${BATS_TEST_TMPDIR:-$(mktemp -d)}"
  workspace="${tmp_root}/workspace"
  input="${workspace}/input"
  framework="${workspace}/framework"
  mkdir -p "${input}/inventory" "${input}/vars" "${input}/bad" "${framework}/ansible"
  printf 'all: {}\n' > "${input}/inventory/hosts.yml"
  printf 'profile: ci\n' > "${input}/vars/reference.yml"
  printf 'single\n' > "${input}/vars/one.yml"
}

@test "copies directory contents into allowed ansible destination" {
  run bash "${script}" "${input}" "${framework}" "inventory/ => ansible/inventory/"

  [ "$status" -eq 0 ]
  [ -f "${framework}/ansible/inventory/hosts.yml" ]
}

@test "copies file sources into destination directory" {
  run bash "${script}" "${input}" "${framework}" "vars/one.yml=>ansible/vars/"

  [ "$status" -eq 0 ]
  [ "$(cat "${framework}/ansible/vars/one.yml")" = "single" ]
}

@test "rejects entries without separator" {
  run bash "${script}" "${input}" "${framework}" "vars ansible/vars/"

  [ "$status" -ne 0 ]
  [[ "$output" == *"overlay entry missing '=>' separator"* ]]
}

@test "rejects missing sources" {
  run bash "${script}" "${input}" "${framework}" "missing/=>ansible/vars/"

  [ "$status" -ne 0 ]
  [[ "$output" == *"overlay source missing"* ]]
}

@test "rejects symlinks in overlay sources" {
  ln -s /etc/passwd "${input}/vars/passwd-link"

  run bash "${script}" "${input}" "${framework}" "vars/=>ansible/vars/"

  [ "$status" -ne 0 ]
  [[ "$output" == *"overlay source must not contain symlinks"* ]]
}

@test "rejects destination path traversal" {
  run bash "${script}" "${input}" "${framework}" "vars/=>../outside"

  [ "$status" -ne 0 ]
  [[ "$output" == *"overlay destination must not contain path traversal"* ]]
}

@test "rejects workflow destinations" {
  run bash "${script}" "${input}" "${framework}" "vars/=>.github/workflows/"

  [ "$status" -ne 0 ]
  [[ "$output" == *"overlay destination must be under ansible/files"* ]]
}

@test "rejects role implementation destinations" {
  run bash "${script}" "${input}" "${framework}" "vars/=>ansible/roles/baseline/tasks/"

  [ "$status" -ne 0 ]
  [[ "$output" == *"overlay destination must be under ansible/files"* ]]
}

