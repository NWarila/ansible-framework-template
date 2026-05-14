#!/usr/bin/env bash
set -euo pipefail

die() {
  echo "::error::$*" >&2
  exit 1
}

extra_vars_files="${1:-}"
input_prefix="${2:-../../input}"

if [[ -z "${extra_vars_files}" ]]; then
  exit 0
fi

while IFS= read -r vars_file; do
  [[ -z "${vars_file}" ]] && continue
  if [[ "${vars_file}" == *$'\r'* ]]; then
    die "extra_vars_file entries must use LF line endings"
  fi
  if [[ "${vars_file}" == /* ]]; then
    die "extra_vars_file must be relative to the input checkout: ${vars_file}"
  fi
  if [[ "${vars_file}" == "." || "${vars_file}" == ".." || "${vars_file}" == ../* || "${vars_file}" == */../* || "${vars_file}" == */.. ]]; then
    die "extra_vars_file must not contain path traversal: ${vars_file}"
  fi

  printf '%s\n' "--extra-vars" "@${input_prefix%/}/${vars_file}"
done <<< "${extra_vars_files}"

