#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
source_file="$repo_root/smtty"
helper_file=$(mktemp)
trap 'rm -f "$helper_file"' EXIT

sed -n '/^# SMTTY_COMPACT_UI_BEGIN$/,/^# SMTTY_COMPACT_UI_END$/p' "$source_file" >"$helper_file"
# shellcheck disable=SC1090
source "$helper_file"

actions=$(smtty_print_compact_actions)
expected_first='  [P] [1]   Play             [G] [6]   Select game       [O] [11]  Launch options'
expected_edit='  [E] [3]   Edit profile     [M] [8]   MangoHud          [W] [13]  Wayland'
expected_quit='  [T] [5]   Diagnostics      [V] [10]  Version           [Q]       Quit'

grep -Fqx "$expected_first" <<<"$actions"
grep -Fqx "$expected_edit" <<<"$actions"
grep -Fqx "$expected_quit" <<<"$actions"

rate_block=$(sed -n '/^choose_gamescope_rate() {$/,/^choose_vrr_hdr_and_steamos() {$/p' "$source_file")
feature_block=$(sed -n '/^choose_vrr_hdr_and_steamos() {$/,/^choose_pipewire_debug() {$/p' "$source_file")
setup_block=$(sed -n '/^choose_drm_output() {$/,/^get_default_sink() {$/p' "$source_file")

[[ "$rate_block" == *'Display refresh (Hz, 0 = auto)'* ]]
[[ "$rate_block" == *'Unfocused refresh (Hz, empty = off'* ]]
[[ "$rate_block" != *'auto-detect max via modetest'* ]]
[[ "$feature_block" == *'VRR (0 = off, 1 = on)'* ]]
[[ "$feature_block" == *'HDR (0 = off, 1 = on)'* ]]
[[ "$feature_block" == *'Expose Wayland (0 = off, 1 = on)'* ]]
[[ "$setup_block" == *'PipeWire logging'* ]]
[[ "$setup_block" == *'Shader-cache preset'* ]]
[[ "$setup_block" == *'Hooks (optional)'* ]]
[[ "$setup_block" != *'Perf/shader cache preset (optional).'* ]]
[[ "$setup_block" != *'Temporary audio output switching'* ]]

printf 'PASS: compact selection prompts\n'
