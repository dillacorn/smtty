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
[[ "$summary" == *"Game:    Counter-Strike 2 (locked)"* ]] || fail "selected game state missing"
[[ "$summary" == *"Display  DP-1 · 1920x1080 @ 400 Hz"* ]] || fail "display summary missing"
[[ "$summary" == *"Render   1600x1200 · Stretch"* ]] || fail "render summary missing"
[[ "$summary" == *"Options  Grab On · VRR Off · HDR Off · Wayland Off"* ]] || fail "feature summary missing"
[[ "$summary" == *"Runtime  PipeWire 0 · MangoHud Off · Audio unchanged"* ]] || fail "runtime summary missing"
[[ "$summary" == *"Hooks    None"* ]] || fail "hook summary missing"

rm -f "$lock_file"
unlocked_summary=$(smtty_print_compact_summary 1 "Off")
[[ "$unlocked_summary" == *"Game:    Counter-Strike 2"* ]] || fail "unlocked game name missing"
[[ "$unlocked_summary" != *"(locked)"* ]] || fail "unlocked game incorrectly marked locked"

summary_lines=$(printf '%s\n' "$summary" | wc -l)
(( summary_lines <= 10 )) || fail "summary is too tall: $summary_lines lines"

action_lines=$(printf '%s\n' "$actions" | wc -l)
(( action_lines <= 6 )) || fail "actions are too tall: $action_lines lines"
[[ "$actions" == *"Play"* ]] || fail "play action missing"
[[ "$actions" == *"Select game"* ]] || fail "game action missing"
[[ "$actions" == *"Launch options"* ]] || fail "launch-options action missing"
[[ "$actions" == *"Profiles"* ]] || fail "profiles action missing"
[[ "$actions" == *"New profile"* ]] || fail "new-profile action missing"
[[ "$actions" == *"Delete profile"* ]] || fail "delete-profile action missing"
[[ "$actions" == *"Edit profile"* ]] || fail "edit action missing"
[[ "$actions" == *"MangoHud"* ]] || fail "MangoHud action missing"
[[ "$actions" == *"Wayland"* ]] || fail "Wayland action missing"
[[ "$actions" == *"Lock game"* ]] || fail "lock action missing"
[[ "$actions" == *"Unlock game"* ]] || fail "unlock action missing"
[[ "$actions" == *"Clear game"* ]] || fail "clear action missing"
[[ "$actions" == *"Diagnostics"* ]] || fail "diagnostics action missing"
[[ "$actions" == *"Version"* ]] || fail "version action missing"
[[ "$actions" == *"Quit"* ]] || fail "quit action missing"
[[ "$actions" != *"[A] More"* ]] || fail "More submenu action remains"

[[ "$actions" == *"[P] [1]"* ]] || fail "numeric alias 1 missing"
[[ "$actions" == *"[G] [2]"* ]] || fail "numeric alias 2 missing"
[[ "$actions" == *"[O] [3]"* ]] || fail "numeric alias 3 missing"
[[ "$actions" == *"[S] [4]"* ]] || fail "numeric alias 4 missing"
[[ "$actions" == *"[N] [5]"* ]] || fail "numeric alias 5 missing"
[[ "$actions" == *"[D] [6]"* ]] || fail "numeric alias 6 missing"
[[ "$actions" == *"[E] [7]"* ]] || fail "numeric alias 7 missing"
[[ "$actions" == *"[M] [8]"* ]] || fail "numeric alias 8 missing"
[[ "$actions" == *"[W] [9]"* ]] || fail "numeric alias 9 missing"
[[ "$actions" == *"[L] [10]"* ]] || fail "numeric alias 10 missing"
[[ "$actions" == *"[U] [11]"* ]] || fail "numeric alias 11 missing"
[[ "$actions" == *"[C] [12]"* ]] || fail "numeric alias 12 missing"
[[ "$actions" == *"[T] [13]"* ]] || fail "numeric alias 13 missing"
[[ "$actions" == *"[V] [14]"* ]] || fail "numeric alias 14 missing"

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
[[ "$menu_block" == *'p|1)'* ]] || fail "Play numeric dispatch is not 1"
[[ "$menu_block" == *'g|2)'* ]] || fail "Select game numeric dispatch is not 2"
[[ "$menu_block" == *'o|3)'* ]] || fail "Launch options numeric dispatch is not 3"
[[ "$menu_block" == *'s|4)'* ]] || fail "Profiles numeric dispatch is not 4"
[[ "$menu_block" == *'n|5)'* ]] || fail "New profile numeric dispatch is not 5"
[[ "$menu_block" == *'d|6)'* ]] || fail "Delete profile numeric dispatch is not 6"
[[ "$menu_block" == *'e|7)'* ]] || fail "Edit profile numeric dispatch is not 7"
[[ "$menu_block" == *'m|8)'* ]] || fail "MangoHud numeric dispatch is not 8"
[[ "$menu_block" == *'w|9)'* ]] || fail "Wayland numeric dispatch is not 9"
[[ "$menu_block" == *'l|10)'* ]] || fail "Lock game numeric dispatch is not 10"
[[ "$menu_block" == *'u|11)'* ]] || fail "Unlock game numeric dispatch is not 11"
[[ "$menu_block" == *'c|12)'* ]] || fail "Clear game numeric dispatch is not 12"
[[ "$menu_block" == *'t|h|13)'* ]] || fail "Diagnostics numeric dispatch is not 13"
[[ "$menu_block" == *'v|14)'* ]] || fail "Version numeric dispatch is not 14"
[[ "$editor_block" == *'echo "Sections"'* ]] || fail "editor compact sections missing"
[[ "$editor_block" != *'echo "Edit sections:"'* ]] || fail "legacy editor section list remains"

if (( failures > 0 )); then
  printf '%d compact UI checks failed.\n' "$failures" >&2
  exit 1
fi

printf 'PASS: compact UI layout checks\n'
