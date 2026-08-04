#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
source_file="$repo_root/smtty"
helper_file=$(mktemp)
trap 'rm -f "$helper_file"' EXIT

sed -n '/^# SMTTY_COMPACT_UI_BEGIN$/,/^# SMTTY_COMPACT_UI_END$/p' "$source_file" >"$helper_file"
# shellcheck disable=SC1090
source "$helper_file"

HAVE_CONFIG=1
CURRENT_PROFILE=""
SMTTY_PROFILE_DRAFT=1
DRM_SHORT="DP-1"
DRM_NATIVE_MODE="1920x1080"
GAME_W=1920
GAME_H=1080
STRETCH_FLAG="none"
G_FPS=400
STEAM_TYPE="native"
FORCE_GRAB_CURSOR=0
ADAPTIVE_SYNC=0
ENABLE_GAMESCOPE_HDR=0
EXPOSE_WAYLAND=0
PIPEWIRE_DEBUG_MODE=0
AUDIO_SWITCH_ENABLED=0
PRE_CMD=""
POST_CMD=""

summary=$(smtty_print_compact_summary 0 "")
[[ "$summary" == *"Profile: Unsaved"* ]]

creator_block=$(sed -n '/^interactive_new_profile() {$/,/^interactive_profile_settings_editor() {$/p' "$source_file")
editor_block=$(sed -n '/^interactive_profile_settings_editor() {$/,/^interactive_profile_menu() {$/p' "$source_file")
guided_block=$(sed -n '/^interactive_new_config() {$/,/^run_from_current_config() {$/p' "$source_file")
menu_block=$(sed -n '/^interactive_profile_menu() {$/,/^cleanup_old_session_artifacts() {$/p' "$source_file")

[[ "$creator_block" == *'Start from'* ]]
[[ "$creator_block" == *'Current profile'* ]]
[[ "$creator_block" == *'Recommended defaults'* ]]
[[ "$creator_block" == *'Guided setup'* ]]
[[ "$creator_block" == *'[Q] Cancel'* ]]
[[ "$creator_block" == *'smtty_capture_profile_state'* ]]
[[ "$creator_block" == *'eval "$saved_state"'* ]]

[[ "$editor_block" == *'New profile · unsaved'* ]]
[[ "$editor_block" == *'Review this draft. Change only what you need, then save.'* ]]
[[ "$editor_block" == *'Select a section to modify.'* ]]
[[ "$editor_block" == *'smtty_print_action_row "[T] [1]" "Steam"'* ]]
[[ "$editor_block" == *'"[D] [2]" "Display"'* ]]
[[ "$editor_block" == *'"[R] [3]" "Resolution"'* ]]
[[ "$editor_block" == *'smtty_print_action_row "[F] [4]" "Refresh"'* ]]
[[ "$editor_block" == *'"[E] [5]" "Features"'* ]]
[[ "$editor_block" == *'"[P] [6]" "PipeWire"'* ]]
[[ "$editor_block" == *'smtty_print_action_row "[C] [7]" "Shader cache"'* ]]
[[ "$editor_block" == *'"[L] [8]" "LD_PRELOAD"'* ]]
[[ "$editor_block" == *'"[A] [9]" "Audio"'* ]]
[[ "$editor_block" == *'smtty_print_action_row "[H] [10]" "Hooks" "[S]" "Save" "[Q]" "Cancel"'* ]]
[[ "$editor_block" == *'t|1)'* ]]
[[ "$editor_block" == *'d|2)'* ]]
[[ "$editor_block" == *'r|3)'* ]]
[[ "$editor_block" == *'f|4)'* ]]
[[ "$editor_block" == *'e|5)'* ]]
[[ "$editor_block" == *'p|6)'* ]]
[[ "$editor_block" == *'c|7)'* ]]
[[ "$editor_block" == *'l|8)'* ]]
[[ "$editor_block" == *'a|9)'* ]]
[[ "$editor_block" == *'h|10)'* ]]
[[ "$editor_block" == *'Discard unsaved profile?'* ]]
[[ "$editor_block" == *'return 2'* ]]
[[ "$editor_block" == *'if choose_gamescope_rate && (( ! is_new ))'* ]]

[[ "$guided_block" == *'SMTTY_PROMPT_QUIT_ENABLED=1'* ]]
[[ "$guided_block" == *'if choose_drm_output; then'* ]]
[[ "$guided_block" == *'step=3'* ]]
[[ "$guided_block" == *'else'*'step=1'* ]]
[[ "$guided_block" == *'if choose_pipewire_latency; then'* ]]
[[ "$guided_block" == *'step=8'* ]]
[[ "$guided_block" == *'if choose_pre_post_commands; then'* ]]
[[ "$guided_block" == *'step=12'* ]]
[[ "$guided_block" == *'Guided setup cancelled.'* ]]
[[ "$guided_block" == *'SMTTY_PROMPT_QUIT_ENABLED=$previous_quit_mode'* ]]

[[ "$menu_block" == *'interactive_new_profile || true'* ]]
[[ "$menu_block" != *'interactive_new_config 1'* ]]

printf 'PASS: profile draft workflow\n'
