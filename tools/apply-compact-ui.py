#!/usr/bin/env python3
from pathlib import Path

path = Path("smtty")
text = path.read_text(encoding="utf-8")
original = text

helpers = r'''# SMTTY_COMPACT_UI_BEGIN
smtty_ui_on_off() {
  if (( ${1:-0} )); then
    printf 'On'
  else
    printf 'Off'
  fi
}

smtty_ui_title_case() {
  local value=${1:-}
  case "$value" in
    native) printf 'Native' ;;
    flatpak) printf 'Flatpak' ;;
    inherit) printf 'Inherit' ;;
    stretch) printf 'Stretch' ;;
    none|"") printf 'Native' ;;
    *) printf '%s' "${value^}" ;;
  esac
}

smtty_print_compact_summary() {
  local include_game=${1:-1}
  local mangohud_state=${2:-}

  if (( HAVE_CONFIG == 0 )); then
    echo "Profile: None"
    if (( include_game )); then
      echo "Game:    None"
    fi
    return 0
  fi

  local profile_name=${CURRENT_PROFILE:-default}
  local game_name="None"
  local refresh="Auto"
  local scaling
  local steam
  local grab
  local vrr
  local hdr
  local wayland
  local audio="unchanged"
  local hooks="None"
  local runtime

  if (( G_FPS > 0 )); then
    refresh="${G_FPS} Hz"
  fi

  scaling=$(smtty_ui_title_case "${STRETCH_FLAG:-none}")
  steam=$(smtty_ui_title_case "${STEAM_TYPE:-native}")
  grab=$(smtty_ui_on_off "${FORCE_GRAB_CURSOR:-0}")
  vrr=$(smtty_ui_on_off "${ADAPTIVE_SYNC:-0}")
  hdr=$(smtty_ui_on_off "${ENABLE_GAMESCOPE_HDR:-0}")
  wayland=$(smtty_ui_on_off "${EXPOSE_WAYLAND:-0}")

  if (( AUDIO_SWITCH_ENABLED )); then
    audio="switch On"
  fi

  if [[ -n "${PRE_CMD:-}" && -n "${POST_CMD:-}" ]]; then
    hooks="Pre + Post"
  elif [[ -n "${PRE_CMD:-}" ]]; then
    hooks="Pre"
  elif [[ -n "${POST_CMD:-}" ]]; then
    hooks="Post"
  fi

  if [[ -n "${SMTTY_APPLAUNCH_APPID:-}" ]]; then
    game_name=${SMTTY_APPLAUNCH_NAME:-"App ${SMTTY_APPLAUNCH_APPID}"}
    if [[ -f "${SMTTY_LOCKED_GAME_FILE:-/nonexistent}" ]]; then
      game_name+=" · Locked"
    fi
  fi

  printf 'Profile: %s\n' "$profile_name"
  if (( include_game )); then
    printf 'Game:    %s\n' "$game_name"
  fi
  echo
  printf 'Display  %s · %s @ %s\n' "${DRM_SHORT:-Unknown}" "${DRM_NATIVE_MODE:-Unknown}" "$refresh"
  printf 'Render   %sx%s · %s\n' "${GAME_W:-0}" "${GAME_H:-0}" "$scaling"
  printf 'Steam    %s\n' "$steam"
  printf 'Options  Grab %s · VRR %s · HDR %s · Wayland %s\n' "$grab" "$vrr" "$hdr" "$wayland"

  runtime="PipeWire ${PIPEWIRE_DEBUG_MODE:-inherit}"
  if [[ -n "$mangohud_state" ]]; then
    runtime+=" · MangoHud ${mangohud_state}"
  fi
  runtime+=" · Audio ${audio}"
  printf 'Runtime  %s\n' "$runtime"
  printf 'Hooks    %s\n' "$hooks"
}

smtty_print_compact_actions() {
  echo "Actions"
  printf '  %-19s %-21s %s\n' "[P] Play" "[G] Select game" "[O] Launch options"
  printf '  %-19s %-21s %s\n' "[S] Profiles" "[E] Edit profile" "[M] MangoHud"
  printf '  %-19s %-21s %s\n' "[W] Wayland" "[T] Diagnostics" "[A] More"
  echo "  [Q] Quit"
}

smtty_more_actions_menu() {
  echo
  echo "More actions"
  printf '  %-20s %-20s %s\n' "[L] Lock game" "[U] Unlock game" "[C] Clear game"
  printf '  %-20s %-20s %s\n' "[N] New profile" "[D] Delete profile" "[V] Version"
  echo "  [B] Back"

  local selected
  if ! read_key_or_number selected "Choose [L,U,C,N,D,V,B]: "; then
    return 1
  fi
  selected="${selected//[[:space:]]/}"
  selected="${selected,,}"

  case "$selected" in
    l|u|c|n|d|v)
      REPLY=$selected
      return 0
      ;;
    b|q|"")
      return 1
      ;;
    *)
      echo "Choose L, U, C, N, D, V, or B."
      return 1
      ;;
  esac
}
# SMTTY_COMPACT_UI_END
'''

anchor = "\ninteractive_profile_settings_editor() {"
if "# SMTTY_COMPACT_UI_BEGIN" not in text:
    if text.count(anchor) != 1:
        raise SystemExit("expected one profile editor anchor")
    text = text.replace(anchor, "\n" + helpers.rstrip() + "\n\ninteractive_profile_settings_editor() {", 1)

old_editor = r'''    echo "Edit profile: ${prof}"
    echo
    print_config_summary
    echo

    echo "Edit sections:"
    echo "  [1] Steam (native/flatpak + launch mode)"
    echo "  [2] Output (DRM connector)"
    echo "  [3] Resolution / scaling"
    echo "  [4] Refresh + FPS limits"
    echo "  [5] VRR / HDR / cursor / expose-wayland / low-latency"
    echo "  [6] PipeWire (debug + latency)"
    echo "  [7] Perf env preset"
    echo "  [8] LD_PRELOAD mode"
    echo "  [9] Audio switching"
    echo "  [0] Pre/Post commands"
    echo "  [S] Save profile"
    echo "  [b] Back"

    local c
    if ! read_key_or_number c "Choose section [1-9,0,S,b]: " ; then
'''
new_editor = r'''    echo "Edit profile: ${prof}"
    echo
    smtty_print_compact_summary 0 ""
    echo

    echo "Sections"
    printf '  %-20s %-20s %s\n' "[1] Steam" "[2] Output" "[3] Resolution"
    printf '  %-20s %-20s %s\n' "[4] Refresh" "[5] Features" "[6] PipeWire"
    printf '  %-20s %-20s %s\n' "[7] Performance" "[8] LD_PRELOAD" "[9] Audio"
    printf '  %-20s %-20s %s\n' "[0] Hooks" "[S] Save" "[B] Back"

    local c
    if ! read_key_or_number c "Choose [1-9,0,S,B]: " ; then
'''
if old_editor in text:
    text = text.replace(old_editor, new_editor, 1)
elif new_editor not in text:
    raise SystemExit("profile editor layout block did not match")

menu_start = text.find("interactive_profile_menu() {")
menu_end = text.find("\ncleanup_old_session_artifacts() {", menu_start)
if menu_start < 0 or menu_end < 0:
    raise SystemExit("interactive profile menu boundaries not found")

new_menu = r'''interactive_profile_menu() {
  smtty_load_locked_game_if_any || true
  while :; do
    smtty_ui_menu_break
    detect_session_mode
    init_default_refresh_for_output

    local mh_state="Off"
    if (( FLAG_MANGOHUD )); then
      mh_state="On"
    fi

    printf 'smtty %s\n\n' "${SMTTY_VERSION#v}"
    smtty_print_compact_summary 1 "$mh_state"
    echo
    smtty_print_compact_actions
    echo

    local choice
    if ! read_key_or_number choice "Choose [P,G,O,S,E,M,W,T,A,Q]: "; then
      echo "Exiting."
      exit 0
    fi
    choice="${choice//[[:space:]]/}"
    choice="${choice,,}"
    [[ -z "$choice" ]] && continue

    if [[ "$choice" == "a" ]]; then
      if ! smtty_more_actions_menu; then
        continue
      fi
      choice=$REPLY
    fi

    case "$choice" in
      m|4)
        if (( FLAG_MANGOHUD )); then
          FLAG_MANGOHUD=0
          echo "MangoHud: Off"
        else
          if command -v mangohud >/dev/null 2>&1; then
            FLAG_MANGOHUD=1
            echo "MangoHud: On"
          else
            detect_pkg_manager
            local pkg=""
            pkg="$(pkg_for_cmd mangohud || true)"
            echo "[ERROR] MangoHud is not installed."
            if [[ -n "$pkg" ]]; then
              echo "Install: ${PKG_INSTALL_CMD} $pkg"
            else
              echo "Install MangoHud with your distro package manager."
            fi
          fi
        fi
        ;;
      w|13)
        if (( HAVE_CONFIG == 0 )); then
          echo "No profile loaded. Create one first."
        else
          if (( EXPOSE_WAYLAND )); then
            EXPOSE_WAYLAND=0
            echo "Wayland exposure: Off"
          else
            EXPOSE_WAYLAND=1
            echo "Wayland exposure: On (may break some games)"
          fi
          save_config || true
        fi
        ;;
      e|14)
        interactive_profile_settings_editor
        ;;
      p|8)
        run_from_current_config
        ;;
      s|9)
        if select_profile_interactive "use"; then
          if load_profile_by_name "$CURRENT_PROFILE"; then
            echo "Profile: ${CURRENT_PROFILE}"
          else
            echo "[ERROR] Failed to load profile: ${CURRENT_PROFILE}"
          fi
        else
          echo "No profiles available."
        fi
        continue
        ;;
      n|10)
        if ! interactive_new_config 1; then
          continue
        fi
        continue
        ;;
      d|11)
        if select_profile_interactive "delete"; then
          delete_profile "$CURRENT_PROFILE" || true
        else
          echo "No profiles available to delete."
        fi
        continue
        ;;
      g|1)
        if pick_installed_steam_game; then
          echo "Game: ${SMTTY_APPLAUNCH_NAME} (${SMTTY_APPLAUNCH_APPID})"
          rm -f "$SMTTY_LOCKED_GAME_FILE" 2>/dev/null || true
          echo "Selection is temporary. Use More > Lock game to persist it."
        fi
        ;;
      t|h|5)
        echo
        smtty_doctor
        echo
        read -r -p "Press Enter to return..." _smtty_doc_pause || true
        ;;
      l|2)
        smtty_lock_selected_game || true
        ;;
      u|3)
        smtty_unlock_selected_game || true
        ;;
      c|6)
        SMTTY_APPLAUNCH_APPID=""
        SMTTY_APPLAUNCH_NAME=""
        export SMTTY_APPLAUNCH_APPID SMTTY_APPLAUNCH_NAME
        rm -f "$SMTTY_LOCKED_GAME_FILE" 2>/dev/null || true
        echo "Game selection cleared."
        ;;
      v|7)
        echo
        smtty_print_version
        echo
        read -r -p "Press Enter to return..." _smtty_ver_pause || true
        ;;
      o|12)
        echo
        ( print_steam_launch_options ) || true
        echo
        read -r -p "Press Enter to return..." _smtty_o_pause || true
        ;;
      q|b)
        echo "Exiting."
        exit 0
        ;;
      *)
        echo "Choose P, G, O, S, E, M, W, T, A, or Q."
        ;;
    esac
  done
}
'''

current_menu = text[menu_start:menu_end]
if "smtty_print_compact_actions" not in current_menu:
    text = text[:menu_start] + new_menu.rstrip() + text[menu_end:]

if text != original:
    path.write_text(text, encoding="utf-8")
    print("patched compact terminal UI")
else:
    print("compact terminal UI already patched")
