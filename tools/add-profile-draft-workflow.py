#!/usr/bin/env python3
from pathlib import Path

path = Path("smtty")
text = path.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 match, found {count}")
    text = text.replace(old, new, 1)


def replace_region(start_marker: str, end_marker: str, replacement: str, label: str) -> None:
    global text
    start = text.find(start_marker)
    if start < 0:
        raise SystemExit(f"{label}: start marker not found")
    end = text.find(end_marker, start)
    if end < 0:
        raise SystemExit(f"{label}: end marker not found")
    text = text[:start] + replacement + text[end:]


replace_once(
    '  local profile_name=${CURRENT_PROFILE:-default}\n',
    '  local profile_name=${CURRENT_PROFILE:-default}\n'
    '  if (( ${SMTTY_PROFILE_DRAFT:-0} )); then\n'
    '    profile_name="Unsaved"\n'
    '  fi\n',
    "draft summary label",
)

new_guided = r'''interactive_new_config() {
  local from_menu=${1:-0}

  CURRENT_PROFILE=""
  PRE_CMD=""
  POST_CMD=""
  LD_PRELOAD_MODE="inherit"
  detect_session_mode

  G_FPS=0
  G_FPS_BG=0

  local step=1
  while :; do
    case "$step" in
      1)
        if ! detect_steam_installations; then
          if (( from_menu )); then
            return 1
          fi
          echo "Aborting interactive setup."
          exit 0
        fi
        if ! choose_steam_launch_mode; then
          if (( from_menu )); then
            return 1
          fi
          echo "Aborting interactive setup."
          exit 0
        fi
        step=2
        ;;
      2)
        if choose_drm_output; then step=3; else step=1; fi
        ;;
      3)
        if choose_resolution_profile; then step=4; else step=2; fi
        ;;
      4)
        if choose_gamescope_rate; then step=5; else step=3; fi
        ;;
      5)
        if choose_vrr_hdr_and_steamos; then step=6; else step=4; fi
        ;;
      6)
        if choose_pipewire_debug; then step=7; else step=5; fi
        ;;
      7)
        if choose_pipewire_latency; then step=8; else step=6; fi
        ;;
      8)
        if choose_perf_env_preset; then step=9; else step=7; fi
        ;;
      9)
        if choose_ld_preload_mode; then step=10; else step=8; fi
        ;;
      10)
        if choose_audio_switch; then step=11; else step=9; fi
        ;;
      11)
        if choose_pre_post_commands; then step=12; else step=10; fi
        ;;
      12)
        if ! save_config; then
          step=11
          continue
        fi
        load_profile_by_name "$CURRENT_PROFILE" >/dev/null 2>&1 || HAVE_CONFIG=1
        return 0
        ;;
      *)
        return 1
        ;;
    esac
  done
}

'''
replace_region(
    "interactive_new_config() {\n",
    "run_from_current_config() {\n",
    new_guided,
    "guided setup",
)

new_editor_and_creator = r'''smtty_capture_profile_state() {
  local var
  local -a vars=(
    CURRENT_PROFILE HAVE_CONFIG DRM_SHORT DRM_NATIVE_MODE NATIVE_W NATIVE_H
    GAME_W GAME_H STRETCH_FLAG G_FPS G_FPS_BG STEAM_TYPE STEAM_LAUNCH_MODE
    ADAPTIVE_SYNC ENABLE_GAMESCOPE_HDR GAMESCOPE_HDR_NITS FORCE_GRAB_CURSOR
    EXPOSE_WAYLAND LOW_LATENCY_TEARING PIPEWIRE_DEBUG_MODE PIPEWIRE_LATENCY
    PERF_ENV_PRESET LD_PRELOAD_MODE AUDIO_SWITCH_ENABLED AUDIO_SINK_NAME
    PRE_CMD POST_CMD SMTTY_EDID_HDR_PEAK_NITS SMTTY_ACTIVE_GPU_VENDOR
  )

  for var in "${vars[@]}"; do
    printf '%s=%q\n' "$var" "${!var-}"
  done
}

smtty_init_recommended_profile() {
  CURRENT_PROFILE=""
  HAVE_CONFIG=1
  DRM_SHORT=""
  DRM_NATIVE_MODE=""
  NATIVE_W=0
  NATIVE_H=0
  GAME_W=0
  GAME_H=0
  STRETCH_FLAG="none"
  G_FPS=0
  G_FPS_BG=0
  STEAM_TYPE=""
  STEAM_LAUNCH_MODE="gamepad"
  ADAPTIVE_SYNC=0
  ENABLE_GAMESCOPE_HDR=0
  GAMESCOPE_HDR_NITS=1000
  FORCE_GRAB_CURSOR=0
  EXPOSE_WAYLAND=0
  LOW_LATENCY_TEARING=0
  PIPEWIRE_DEBUG_MODE=0
  PIPEWIRE_LATENCY="inherit"
  PERF_ENV_PRESET=0
  LD_PRELOAD_MODE="inherit"
  AUDIO_SWITCH_ENABLED=0
  AUDIO_SINK_NAME=""
  PRE_CMD=""
  POST_CMD=""

  detect_session_mode
  detect_steam_installations || return 1
  choose_drm_output || return 1

  GAME_W=$NATIVE_W
  GAME_H=$NATIVE_H
  STRETCH_FLAG="none"
  init_default_refresh_for_output
  return 0
}

interactive_new_profile() {
  local saved_state
  saved_state=$(smtty_capture_profile_state)

  while :; do
    smtty_ui_menu_break
    echo "New profile"
    echo
    echo "Start from"
    if (( HAVE_CONFIG )); then
      printf '  [1] Current profile · %s\n' "${CURRENT_PROFILE:-default}"
    else
      echo "  [1] Current profile · unavailable"
    fi
    echo "  [2] Recommended defaults"
    echo "  [3] Guided setup"
    echo "  [Q] Cancel"
    echo

    local choice=""
    printf 'Choose [1]: '
    IFS= read -rsn1 choice || return 1
    printf '\n'
    [[ -z "$choice" || "$choice" == $'\r' || "$choice" == $'\n' ]] && choice=1
    choice="${choice,,}"

    case "$choice" in
      1)
        if (( HAVE_CONFIG == 0 )); then
          echo "No current profile to copy."
          continue
        fi
        CURRENT_PROFILE=""
        HAVE_CONFIG=1
        ;;
      2)
        eval "$saved_state"
        if ! smtty_init_recommended_profile; then
          eval "$saved_state"
          echo "Could not build recommended defaults."
          continue
        fi
        ;;
      3)
        eval "$saved_state"
        if interactive_new_config 1; then
          return 0
        fi
        eval "$saved_state"
        return 1
        ;;
      q|b)
        eval "$saved_state"
        return 1
        ;;
      *)
        echo "Choose 1, 2, 3, or Q."
        continue
        ;;
    esac

    SMTTY_PROFILE_DRAFT=1
    if interactive_profile_settings_editor new; then
      unset SMTTY_PROFILE_DRAFT
      return 0
    else
      local status=$?
      unset SMTTY_PROFILE_DRAFT
      eval "$saved_state"
      if (( status == 2 )); then
        continue
      fi
      return 1
    fi
  done
}

interactive_profile_settings_editor() {
  local mode=${1:-edit}
  local is_new=0
  [[ "$mode" == "new" ]] && is_new=1

  if (( ! is_new && HAVE_CONFIG == 0 )); then
    echo
    echo "No profile loaded. Create one first."
    read -r -p "Press Enter to return..." _smtty_edit_pause || true
    return 0
  fi

  local prof="${CURRENT_PROFILE:-default}"

  while :; do
    smtty_ui_menu_break
    detect_session_mode
    init_default_refresh_for_output

    if (( is_new )); then
      echo "New profile · unsaved"
    else
      echo "Edit profile: ${prof}"
    fi
    echo
    smtty_print_compact_summary 0 ""
    echo

    echo "Sections"
    printf '  %-20s %-20s %s\n' "[1] Steam" "[2] Display" "[3] Resolution"
    printf '  %-20s %-20s %s\n' "[4] Refresh" "[5] Features" "[6] PipeWire"
    printf '  %-20s %-20s %s\n' "[7] Performance" "[8] LD_PRELOAD" "[9] Audio"
    if (( is_new )); then
      printf '  %-20s %-20s %s\n' "[0] Hooks" "[S] Save" "[Q] Cancel"
    else
      printf '  %-20s %-20s %s\n' "[0] Hooks" "[S] Save" "[B] Back"
    fi

    local c
    if ! read_key_or_number c "Choose: "; then
      if (( is_new )); then
        return 2
      fi
      return 0
    fi
    c="${c//[[:space:]]/}"
    c="${c,,}"
    [[ -z "$c" ]] && continue

    case "$c" in
      1)
        if ! detect_steam_installations; then
          echo "[ERROR] Steam not found."
          continue
        fi
        if choose_steam_launch_mode && (( ! is_new )); then save_config || true; fi
        ;;
      2)
        if choose_drm_output && (( ! is_new )); then
          save_config || true
          prof="${CURRENT_PROFILE:-$prof}"
        fi
        ;;
      3)
        if choose_resolution_profile && (( ! is_new )); then save_config || true; fi
        ;;
      4)
        if choose_gamescope_rate && (( ! is_new )); then save_config || true; fi
        ;;
      5)
        if choose_vrr_hdr_and_steamos && (( ! is_new )); then save_config || true; fi
        ;;
      6)
        if choose_pipewire_debug; then
          if choose_pipewire_latency && (( ! is_new )); then save_config || true; fi
        fi
        ;;
      7)
        if choose_perf_env_preset && (( ! is_new )); then save_config || true; fi
        ;;
      8)
        if choose_ld_preload_mode && (( ! is_new )); then save_config || true; fi
        ;;
      9)
        if choose_audio_switch && (( ! is_new )); then save_config || true; fi
        ;;
      0)
        if choose_pre_post_commands && (( ! is_new )); then save_config || true; fi
        ;;
      s)
        if save_config; then
          if (( is_new )); then
            load_profile_by_name "$CURRENT_PROFILE" >/dev/null 2>&1 || HAVE_CONFIG=1
            return 0
          fi
          read -r -p "Press Enter to return..." _smtty_save_pause || true
        fi
        ;;
      q)
        if (( is_new )); then
          local discard=""
          read -r -p "Discard unsaved profile? [y/N]: " discard
          case "$discard" in
            y|Y|yes|YES) return 1 ;;
            *) continue ;;
          esac
        fi
        ;;
      b)
        if (( is_new )); then
          return 2
        fi
        return 0
        ;;
      *)
        if (( is_new )); then
          echo "Choose 1-9, 0, S, or Q."
        else
          echo "Choose 1-9, 0, S, or B."
        fi
        ;;
    esac
  done
}

'''
replace_region(
    "interactive_profile_settings_editor() {\n",
    "interactive_profile_menu() {\n",
    new_editor_and_creator,
    "profile editor and creator",
)

replace_once(
'''      n|10)
        if ! interactive_new_config 1; then
          continue
        fi
        continue
        ;;
''',
'''      n|10)
        interactive_new_profile || true
        continue
        ;;
''',
    "main menu new-profile action",
)

path.write_text(text, encoding="utf-8")
print("added section-based profile draft workflow")
