#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
helper_file=$(mktemp)
trap 'rm -f "$helper_file"' EXIT

sed -n \
  '/^# SMTTY_LAUNCH_OPTIONS_NORMALIZER_BEGIN$/,/^# SMTTY_LAUNCH_OPTIONS_NORMALIZER_END$/p' \
  "$repo_root/smtty" >"$helper_file"

if [[ ! -s "$helper_file" ]]; then
  echo "FAIL: launch-option normalizer block was not found in smtty" >&2
  exit 1
fi

# shellcheck disable=SC1090
source "$helper_file"

failures=0
tests_run=0

fail() {
  printf 'FAIL: %s\n' "$*" >&2
  failures=$((failures + 1))
}

assert_ok() {
  local name=$1
  local input=$2
  local expected_env=$3
  local expected_command=$4
  local expected_count=$5

  tests_run=$((tests_run + 1))
  if ! smtty_normalize_launch_options "$input"; then
    fail "$name: unexpected error: $SMTTY_LAUNCH_NORMALIZE_ERROR"
    return
  fi

  [[ "$SMTTY_NORMALIZED_ENV" == "$expected_env" ]] ||
    fail "$name: env expected <$expected_env>, got <$SMTTY_NORMALIZED_ENV>"
  [[ "$SMTTY_NORMALIZED_COMMAND" == "$expected_command" ]] ||
    fail "$name: command expected <$expected_command>, got <$SMTTY_NORMALIZED_COMMAND>"
  [[ "$SMTTY_NORMALIZED_COUNT" == "$expected_count" ]] ||
    fail "$name: count expected <$expected_count>, got <$SMTTY_NORMALIZED_COUNT>"
}

assert_reject() {
  local name=$1
  local input=$2
  local expected_fragment=$3

  tests_run=$((tests_run + 1))
  if smtty_normalize_launch_options "$input"; then
    fail "$name: expected rejection, got env <$SMTTY_NORMALIZED_ENV> command <$SMTTY_NORMALIZED_COMMAND>"
    return
  fi

  [[ "$SMTTY_LAUNCH_NORMALIZE_ERROR" == *"$expected_fragment"* ]] ||
    fail "$name: error expected to contain <$expected_fragment>, got <$SMTTY_LAUNCH_NORMALIZE_ERROR>"
}

assert_ok \
  "reported broken ordering" \
  'PROTON_FSR4_RDNA3_UPGRADE=1 gamemoderun %command% -novid +fps_max 0 -high -dx12' \
  'PROTON_FSR4_RDNA3_UPGRADE=1' \
  'gamemoderun %command% -novid +fps_max 0 -high -dx12' \
  1

assert_ok \
  "multiple leading assignments" \
  'MANGOHUD=1 PROTON_FSR4_RDNA3_UPGRADE=1 gamemoderun %command%' \
  'MANGOHUD=1 PROTON_FSR4_RDNA3_UPGRADE=1' \
  'gamemoderun %command%' \
  2

assert_ok \
  "quoted value with spaces" \
  'FOO="value with spaces" gamemoderun %command%' \
  'FOO="value with spaces"' \
  'gamemoderun %command%' \
  1

assert_ok \
  "single quoted control character" \
  "FOO='a;b' gamemoderun %command%" \
  "FOO='a;b'" \
  'gamemoderun %command%' \
  1

assert_ok \
  "escaped spaces" \
  'FOO=value\ with\ spaces gamemoderun %command%' \
  'FOO=value\ with\ spaces' \
  'gamemoderun %command%' \
  1

assert_ok \
  "empty value" \
  'FOO= gamemoderun %command%' \
  'FOO=' \
  'gamemoderun %command%' \
  1

assert_ok \
  "assignment after wrapper" \
  'gamemoderun PROTON_FSR4_RDNA3_UPGRADE=1 %command%' \
  'PROTON_FSR4_RDNA3_UPGRADE=1' \
  'gamemoderun %command%' \
  1

assert_ok \
  "env form" \
  'env PROTON_FSR4_RDNA3_UPGRADE=1 gamemoderun %command%' \
  'PROTON_FSR4_RDNA3_UPGRADE=1' \
  'gamemoderun %command%' \
  1

assert_ok \
  "env double dash form" \
  'env FOO=1 BAR=2 -- gamemoderun %command%' \
  'FOO=1 BAR=2' \
  'gamemoderun %command%' \
  2

assert_ok \
  "env after wrapper" \
  'mangohud gamemoderun env FOO=1 %command%' \
  'FOO=1' \
  'mangohud gamemoderun %command%' \
  1

assert_ok \
  "no assignments" \
  'gamemoderun %command% -novid' \
  '' \
  'gamemoderun %command% -novid' \
  0

assert_ok \
  "assignment after command stays game argument" \
  'gamemoderun %command% FOO=bar' \
  '' \
  'gamemoderun %command% FOO=bar' \
  0

assert_ok \
  "duplicate assignments preserve order" \
  'FOO=old FOO=new %command%' \
  'FOO=old FOO=new' \
  '%command%' \
  2

assert_ok \
  "env without assignments remains command" \
  'env --ignore-environment %command%' \
  '' \
  'env --ignore-environment %command%' \
  0

assert_ok \
  "option containing equals stays command" \
  'wrapper --config=value %command%' \
  '' \
  'wrapper --config=value %command%' \
  0

assert_reject \
  "nested gamescope" \
  'PIPEWIRE_DEBUG=0 gamescope -f -- gamemoderun %command%' \
  'already contain gamescope'

assert_reject \
  "unterminated quote" \
  'FOO="broken gamemoderun %command%' \
  'unterminated quote'

assert_reject \
  "trailing escape" \
  'FOO=broken\' \
  'incomplete escape'

assert_reject \
  "unquoted command separator" \
  'FOO=1 gamemoderun %command% ; echo broken' \
  'too ambiguous'

assert_reject \
  "missing command placeholder" \
  'FOO=1 gamemoderun' \
  'must contain %command%'

generator_block=$(
  sed -n \
    '/^print_steam_launch_options() {$/,/^# ---------------- Steam launch mode/p' \
    "$repo_root/smtty"
)

[[ "$generator_block" == *'printf '\''%s '\'' "$NORMALIZED_LAUNCH_ENV"'* ]] ||
  fail "generator does not emit normalized assignments before gamescope"
[[ "$generator_block" == *'printf '\'' -- %s\n'\'' "$CURRENT_LAUNCH_OPTS"'* ]] ||
  fail "generator does not emit the normalized command after gamescope --"

if (( failures > 0 )); then
  printf '%d/%d launch-option parser tests failed.\n' "$failures" "$tests_run" >&2
  exit 1
fi

printf 'PASS: %d launch-option parser cases\n' "$tests_run"
