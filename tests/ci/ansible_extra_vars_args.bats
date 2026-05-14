#!/usr/bin/env bats

setup() {
  repo_root="$(cd "${BATS_TEST_DIRNAME}/../.." && pwd)"
  script="${repo_root}/tools/ci/ansible_extra_vars_args.sh"
}

@test "empty input prints nothing" {
  run bash "${script}" ""

  [ "$status" -eq 0 ]
  [ "$output" = "" ]
}

@test "renders one extra vars file argument" {
  run bash "${script}" "vars/reference.yml" "../../input"

  [ "$status" -eq 0 ]
  [ "${lines[0]}" = "--extra-vars" ]
  [ "${lines[1]}" = "@../../input/vars/reference.yml" ]
}

@test "renders multiple extra vars file arguments" {
  run bash "${script}" $'vars/base.yml\nvars/env.yml' "input"

  [ "$status" -eq 0 ]
  [ "${lines[0]}" = "--extra-vars" ]
  [ "${lines[1]}" = "@input/vars/base.yml" ]
  [ "${lines[2]}" = "--extra-vars" ]
  [ "${lines[3]}" = "@input/vars/env.yml" ]
}

@test "rejects absolute path" {
  run bash "${script}" "/tmp/vars.yml"

  [ "$status" -ne 0 ]
  [[ "$output" == *"must be relative"* ]]
}

@test "rejects path traversal" {
  run bash "${script}" "../vars.yml"

  [ "$status" -ne 0 ]
  [[ "$output" == *"must not contain path traversal"* ]]
}

