#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
source_file="$repo_root/smtty"
helper_file=$(mktemp)
trap 'rm -f "$helper_file"' EXIT

awk '
  /^backable_read\(\) \{/ { capture=1 }
  /^print_help\(\) \{/ { capture=0 }
  capture { print }
' "$source_file" >"$helper_file"

BACK_SENTINEL="__SMTTY_BACK__"
QUIT_SENTINEL="__SMTTY_QUIT__"
SMTTY_PROMPT_QUIT_ENABLED=1
SMTTY_QUIT_REQUESTED=0

# shellcheck disable=SC1090
source "$helper_file"

set +e
backable_read value "Value (b = back): " <<<"q" >/dev/null
rc=$?
set -e
[[ $rc -eq 3 ]]
[[ $SMTTY_QUIT_REQUESTED -eq 1 ]]

SMTTY_QUIT_REQUESTED=0
set +e
read_one_key value "Choose (b = back): " <<<"Q" >/dev/null
rc=$?
set -e
[[ $rc -eq 3 ]]
[[ $SMTTY_QUIT_REQUESTED -eq 1 ]]

SMTTY_QUIT_REQUESTED=0
result=$(read_default "Value" "42" <<<"q")
[[ "$result" == "$QUIT_SENTINEL" ]]

nav_block=$(sed -n '/^# back \/ quit navigation$/,/^# SMTTY_GUIDED_QUIT_END$/p' "$source_file")
guided_block=$(sed -n '/^interactive_new_config() {$/,/^run_from_current_config() {$/p' "$source_file")
resolution_block=$(sed -n '/^choose_resolution_profile() {$/,/^choose_gamescope_rate() {$/p' "$source_file")

[[ "$nav_block" == *'QUIT_SENTINEL="__SMTTY_QUIT__"'* ]]
[[ "$nav_block" == *'SMTTY_PROMPT_QUIT_ENABLED=0'* ]]
[[ "$guided_block" == *'SMTTY_PROMPT_QUIT_ENABLED=1'* ]]
[[ "$guided_block" == *'Guided setup cancelled.'* ]]
[[ "$guided_block" == *'elif (( SMTTY_QUIT_REQUESTED ))'* ]]
[[ "$guided_block" == *'SMTTY_PROMPT_QUIT_ENABLED=$previous_quit_mode'* ]]
[[ "$resolution_block" == *'Width [${NATIVE_W}] (b = back, q = quit)'* ]]
[[ "$resolution_block" == *'Height [${NATIVE_H}] (b = back, q = quit)'* ]]
[[ "$resolution_block" == *'q) SMTTY_QUIT_REQUESTED=1; return 1 ;;'* ]]

quit_checks=$(grep -c '== "$QUIT_SENTINEL"' "$source_file")
(( quit_checks >= 8 ))

printf 'PASS: guided setup quit handling\n'
