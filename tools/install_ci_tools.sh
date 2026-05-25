#!/usr/bin/env bash
# Install pinned CI tools that are not provided by pip/apt.
#
# The downloaded OPA binary is verified against the SHA-256 file published
# with the same upstream GitHub release. This protects against mirror or
# transport tampering; release trust still comes from the upstream project.

set -euo pipefail

require_var() {
  local name="$1"
  local value="${!name:-}"
  if [ -z "$value" ]; then
    echo "error: required env var $name is not set" >&2
    exit 2
  fi
}

verify_sha256() {
  local file="$1"
  local expected="$2"
  local actual
  actual="$(sha256sum "$file" | awk '{print $1}')"
  if [ "$actual" != "$expected" ]; then
    echo "error: sha256 mismatch for $file" >&2
    echo "  expected: $expected" >&2
    echo "  actual:   $actual" >&2
    exit 1
  fi
}

install_opa() {
  local v="$OPA_VERSION"
  local bin="opa_linux_amd64_static"
  local base="https://github.com/open-policy-agent/opa/releases/download/v${v}"

  curl --fail --silent --show-error --location -o "${workdir}/${bin}" "${base}/${bin}"
  curl --fail --silent --show-error --location -o "${workdir}/${bin}.sha256" "${base}/${bin}.sha256"

  local expected
  expected="$(awk '{print $1}' "${workdir}/${bin}.sha256")"
  if [ -z "$expected" ]; then
    echo "error: OPA sha256 file is empty" >&2
    exit 1
  fi

  verify_sha256 "${workdir}/${bin}" "$expected"
  install -m 0755 "${workdir}/${bin}" "${bindir}/opa"
  "${bindir}/opa" version
}

install_actionlint() {
  local v="$ACTIONLINT_VERSION"
  local tar="actionlint_${v}_linux_amd64.tar.gz"
  local sums="actionlint_${v}_checksums.txt"
  local base="https://github.com/rhysd/actionlint/releases/download/v${v}"

  curl --fail --silent --show-error --location -o "${workdir}/${tar}" "${base}/${tar}"
  curl --fail --silent --show-error --location -o "${workdir}/${sums}" "${base}/${sums}"

  local expected
  expected="$(awk -v f="${tar}" '$2 == f {print $1}' "${workdir}/${sums}")"
  if [ -z "$expected" ]; then
    echo "error: ${tar} not found in ${sums}" >&2
    exit 1
  fi

  verify_sha256 "${workdir}/${tar}" "$expected"
  mkdir -p "${workdir}/actionlint"
  tar -xzf "${workdir}/${tar}" -C "${workdir}/actionlint"
  install -m 0755 "${workdir}/actionlint/actionlint" "${bindir}/actionlint"
  "${bindir}/actionlint" -version
}

require_var ACTIONLINT_VERSION
require_var OPA_VERSION

bindir="${HOME}/.local/bin"
mkdir -p "$bindir"
if [ -n "${GITHUB_PATH:-}" ]; then
  echo "$bindir" >> "$GITHUB_PATH"
else
  export PATH="${bindir}:$PATH"
fi

workdir="$(mktemp -d)"
trap 'rm -rf "$workdir"' EXIT

install_actionlint
install_opa
