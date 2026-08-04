#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
helper_file=$(mktemp)
lock_file=$(mktemp)
trap 'rm -f "$helper_file" "$lock_file"' EXIT

sed -n \
  '/^# SMTTY_COMPACT_UI_BEGIN$/,/^# SMTTY_COMPACT_UI_END$/p' \
  "$repo_root/smtty" >"$helper_file"

if [[ ! -s "$helper_file" ]]; then
  echo "FAIL: compact UI helper block was not found" >&2
  exit 1
fi

# shellcheck disable=SC1090
source "$helper_file"

failures=0
fail() {
  printf 'FAIL: %s\n' "$*" >&2
  failures=$((failures + 1))
}

HAVE_CONFIG=1
CURRENT_PROFILE="Zowie-43-Hyprland"
SMTTY_APPLAUNCH_APPID="730"
SMTTY_APPLAUNCH_NAME="Counter-Strike 2"
SMTTY_LOCKED_GAME_FILE=$lock_file
DRM_SHORT="DP-1"
DRM_NATIVE_MODE="1920x1080"
GAME_W=1600
GAME_H=1200
STRETCH_FLAG="stretch"
G_FPS=400
STEAM_TYPE="native"
FORCE_GRAB_CURSOR=1
ADAPTIVE_SYNC=0
ENABLE_GAMESCOPE_HDR=0
EXPOSE_WAYLAND=0
PIPEWIRE_DEBUG_MODE=0
AUDIO_SWITCH_ENABLED=0
PRE_CMD=""
POST_CMD=""

summary=$(smtty_print_compact_summary 1 "Off")
actions=$(smtty_print_compact_actions)

[[ "$summary" == *"Profile: Zowie-43-Hyprland"* ]] || fail "profile name missing"
[[ "$summary" == *"Game:    Counter-Strike 2 · Locked"* ]] || fail "selected game state missing"
[[ "$summary" == *"Display  DP-1 · 1920x1080 @ 400 Hz"* ]] || fail "display summary missing"
[[ "$summary" == *"Render   1600x1200 · Stretch"* ]] || fail "render summary missing"
[[ "$summary" == *"Options  Grab On · VRR Off · HDR Off · Wayland Off"* ]] || fail "feature summary missing"
[[ "$summary" == *"Runtime  PipeWire 0 · MangoHud Off · Audio unchanged"* ]] || fail "runtime summary missing"
[[ "$summary" == *"Hooks    None"* ]] || fail "hook summary missing"

summary_lines=$(printf '%s\n' "$summary" | wc -l)
(( summary_lines <= 10 )) || fail "summary is too tall: $summary_lines lines"

action_lines=$(printf '%s\n' "$actions" | wc -l)
(( action_lines <= 6 )) || fail "actions are too tall: $action_lines lines"
[[ "$actions" == *"[P] [8] Play"* ]] || fail "play action missing"
[[ "$actions" == *"[G] [1] Select game"* ]] || fail "game action missing"
[[ "$actions" == *"[O] [12] Launch options"* ]] || fail "launch-options action missing"
[[ "$actions" == *"[S] [9] Profiles"* ]] || fail "profiles action missing"
[[ "$actions" == *"[N] [10] New profile"* ]] || fail "new-profile action missing"
[[ "$actions" == *"[D] [11] Delete profile"* ]] || fail "delete-profile action missing"
[[ "$actions" == *"[E] [14] Edit profile"* ]] || fail "edit action missing"
[[ "$actions" == *"[M] [4] MangoHud"* ]] || fail "MangoHud action missing"
[[ "$actions" == *"[W] [13] Wayland"* ]] || fail "Wayland action missing"
[[ "$actions" == *"[L] [2] Lock game"* ]] || fail "lock action missing"
[[ "$actions" == *"[U] [3] Unlock game"* ]] || fail "unlock action missing"
[[ "$actions" == *"[C] [6] Clear game"* ]] || fail "clear action missing"
[[ "$actions" == *"[T] [5] Diagnostics"* ]] || fail "diagnostics action missing"
[[ "$actions" == *"[V] [7] Version"* ]] || fail "version action missing"
[[ "$actions" == *"[Q] Quit"* ]] || fail "quit action missing"
[[ "$actions" != *"[A] More"* ]] || fail "More submenu action remains"

[[ "$actions" == *"[G] [1]"* ]] || fail "numeric alias 1 missing"
[[ "$actions" == *"[L] [2]"* ]] || fail "numeric alias 2 missing"
[[ "$actions" == *"[U] [3]"* ]] || fail "numeric alias 3 missing"
[[ "$actions" == *"[M] [4]"* ]] || fail "numeric alias 4 missing"
[[ "$actions" == *"[T] [5]"* ]] || fail "numeric alias 5 missing"
[[ "$actions" == *"[C] [6]"* ]] || fail "numeric alias 6 missing"
[[ "$actions" == *"[V] [7]"* ]] || fail "numeric alias 7 missing"
[[ "$actions" == *"[P] [8]"* ]] || fail "numeric alias 8 missing"
[[ "$actions" == *"[S] [9]"* ]] || fail "numeric alias 9 missing"
[[ "$actions" == *"[N] [10]"* ]] || fail "numeric alias 10 missing"
[[ "$actions" == *"[D] [11]"* ]] || fail "numeric alias 11 missing"
[[ "$actions" == *"[O] [12]"* ]] || fail "numeric alias 12 missing"
[[ "$actions" == *"[W] [13]"* ]] || fail "numeric alias 13 missing"
[[ "$actions" == *"[E] [14]"* ]] || fail "numeric alias 14 missing"

menu_block=$(
  sed -n \
    '/^interactive_profile_menu() {$/,/^cleanup_old_session_artifacts() {$/p' \
    "$repo_root/smtty"
)
editor_block=$(
  sed -n \
    '/^interactive_profile_settings_editor() {$/,/^interactive_profile_menu() {$/p' \
    "$repo_root/smtty"
)

[[ "$menu_block" == *"smtty_print_compact_summary"* ]] || fail "main menu does not use compact summary"
[[ "$menu_block" == *"smtty_print_compact_actions"* ]] || fail "main menu does not use compact actions"
[[ "$menu_block" == *'echo "Steam Machine TTY Wrapper"'* ]] || fail "product title missing"
[[ "$menu_block" != *"smtty_more_actions_menu"* ]] || fail "More submenu dispatch remains"
[[ "$menu_block" != *"smtty %s"* ]] || fail "version banner remains at top"
[[ "$menu_block" != *'echo "Options:"'* ]] || fail "legacy tall Options list remains"
[[ "$editor_block" == *'echo "Sections"'* ]] || fail "editor compact sections missing"
[[ "$editor_block" != *'echo "Edit sections:"'* ]] || fail "legacy editor section list remains"

if (( failures > 0 )); then
  printf '%d compact UI checks failed.\n' "$failures" >&2
  exit 1
fi

printf 'PASS: compact UI layout checks\n'
