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
[[ "$editor_block" == *'"[S] Save" "[Q] Cancel"'* ]]
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
