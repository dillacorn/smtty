#!/usr/bin/env python3
from pathlib import Path

smtty_path = Path("smtty")
test_path = Path("tests/test-launch-options-normalizer.sh")
smtty = smtty_path.read_text(encoding="utf-8")
tests = test_path.read_text(encoding="utf-8")

helper = r'''smtty_print_gamescope_launch_prefix() {
  local use_flatpak_prefix=$1
  local env_prefix=$2
  local normalized_env=$3

  if (( use_flatpak_prefix )); then
    printf 'flatpak-spawn --host '
    if [[ -n "$env_prefix$normalized_env" ]]; then
      printf 'env '
      printf '%s' "$env_prefix"
      if [[ -n "$normalized_env" ]]; then
        printf '%s ' "$normalized_env"
      fi
    fi
  else
    printf '%s' "$env_prefix"
    if [[ -n "$normalized_env" ]]; then
      printf '%s ' "$normalized_env"
    fi
  fi
}

'''

helper_anchor = "# SMTTY_LAUNCH_OPTIONS_NORMALIZER_END\n"
if "smtty_print_gamescope_launch_prefix()" not in smtty:
    if smtty.count(helper_anchor) != 1:
        raise SystemExit("expected one normalizer end marker")
    smtty = smtty.replace(helper_anchor, helper + helper_anchor, 1)

old_output = r'''  printf '%s' "$env_prefix"
  if [[ -n "$NORMALIZED_LAUNCH_ENV" ]]; then
    printf '%s ' "$NORMALIZED_LAUNCH_ENV"
  fi
  if (( use_flatpak_prefix )); then
    printf 'flatpak-spawn --host '
  fi
  printf 'gamescope'
'''
new_output = r'''  smtty_print_gamescope_launch_prefix \
    "$use_flatpak_prefix" \
    "$env_prefix" \
    "$NORMALIZED_LAUNCH_ENV"
  printf 'gamescope'
'''

if old_output in smtty:
    smtty = smtty.replace(old_output, new_output, 1)
elif new_output not in smtty:
    raise SystemExit("launch prefix output block did not match")

assert_helper = r'''assert_prefix() {
  local name=$1
  local use_flatpak=$2
  local profile_env=$3
  local normalized_env=$4
  local expected=$5
  local actual

  tests_run=$((tests_run + 1))
  actual=$(smtty_print_gamescope_launch_prefix \
    "$use_flatpak" \
    "$profile_env" \
    "$normalized_env")

  [[ "$actual" == "$expected" ]] ||
    fail "$name: prefix expected <$expected>, got <$actual>"
}

'''
assert_anchor = "assert_reject() {\n"
if "assert_prefix()" not in tests:
    if tests.count(assert_anchor) != 1:
        raise SystemExit("expected one assert_reject anchor")
    tests = tests.replace(assert_anchor, assert_helper + assert_anchor, 1)

prefix_cases = r'''assert_prefix \
  "native env prefix" \
  0 \
  'PIPEWIRE_DEBUG=0 ' \
  'PROTON_FSR4_RDNA3_UPGRADE=1' \
  'PIPEWIRE_DEBUG=0 PROTON_FSR4_RDNA3_UPGRADE=1 '

assert_prefix \
  "flatpak env forwarding" \
  1 \
  'PIPEWIRE_DEBUG=0 ' \
  'PROTON_FSR4_RDNA3_UPGRADE=1' \
  'flatpak-spawn --host env PIPEWIRE_DEBUG=0 PROTON_FSR4_RDNA3_UPGRADE=1 '

assert_prefix \
  "flatpak without env" \
  1 \
  '' \
  '' \
  'flatpak-spawn --host '

'''
prefix_anchor = "assert_ok \\\n  \"reported broken ordering\""
if '"flatpak env forwarding"' not in tests:
    if tests.count(prefix_anchor) != 1:
        raise SystemExit("expected one first test anchor")
    tests = tests.replace(prefix_anchor, prefix_cases + prefix_anchor, 1)

old_static = r'''[[ "$generator_block" == *'printf '\''%s '\'' "$NORMALIZED_LAUNCH_ENV"'* ]] ||
  fail "generator does not emit normalized assignments before gamescope"
'''
new_static = r'''[[ "$generator_block" == *'smtty_print_gamescope_launch_prefix'* ]] ||
  fail "generator does not use the tested launch-prefix formatter"
'''
if old_static in tests:
    tests = tests.replace(old_static, new_static, 1)
elif new_static not in tests:
    raise SystemExit("generator static assertion did not match")

smtty_path.write_text(smtty, encoding="utf-8")
test_path.write_text(tests, encoding="utf-8")
print("patched Flatpak environment forwarding and tests")
