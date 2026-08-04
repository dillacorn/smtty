#!/usr/bin/env python3
from pathlib import Path
import re

path = Path("smtty")
text = path.read_text(encoding="utf-8")

if "# SMTTY_GUIDED_QUIT_BEGIN" in text:
    print("guided quit support already applied")
    raise SystemExit(0)


def replace_function(source: str, name: str, next_name: str, replacement: str) -> str:
    pattern = re.compile(
        rf"(?ms)^{re.escape(name)}\(\) \{{.*?(?=^{re.escape(next_name)}\(\) \{{)"
    )
    updated, count = pattern.subn(replacement.rstrip() + "\n\n", source, count=1)
    if count != 1:
        raise SystemExit(f"could not replace function {name}")
    return updated


old_nav = '# back navigation\nBACK_SENTINEL="__SMTTY_BACK__"\n'
new_nav = '''# back / quit navigation
BACK_SENTINEL="__SMTTY_BACK__"
# SMTTY_GUIDED_QUIT_BEGIN
QUIT_SENTINEL="__SMTTY_QUIT__"
SMTTY_PROMPT_QUIT_ENABLED=0
SMTTY_QUIT_REQUESTED=0
# SMTTY_GUIDED_QUIT_END
'''
if old_nav not in text:
    raise SystemExit("navigation globals anchor not found")
text = text.replace(old_nav, new_nav, 1)

text = replace_function(
    text,
    "backable_read",
    "read_one_key",
    r'''backable_read() {
  # backable_read <var_name> <prompt>
  # Returns 2 for back and 3 for guided-setup quit.
  local __var_name=$1
  local __prompt=$2
  local __value

  if (( ${SMTTY_PROMPT_QUIT_ENABLED:-0} )); then
    __prompt=${__prompt//b = back/b = back, q = quit}
  fi

  read -rp "$__prompt" __value || exit 1
  case "${__value,,}" in
    b)
      return 2
      ;;
    q)
      if (( ${SMTTY_PROMPT_QUIT_ENABLED:-0} )); then
        SMTTY_QUIT_REQUESTED=1
        return 3
      fi
      ;;
  esac

  printf -v "$__var_name" '%s' "$__value"
  return 0
}''',
)

text = replace_function(
    text,
    "read_one_key",
    "read_key_or_number",
    r'''read_one_key() {
  # read_one_key <var_name> <prompt>
  # Reads one key. Returns 1 for back and 3 for guided-setup quit.
  local __var_name=$1
  local __prompt=$2
  local __ch=""

  if (( ${SMTTY_PROMPT_QUIT_ENABLED:-0} )); then
    __prompt=${__prompt//b = back/b = back, q = quit}
  fi

  printf '%s' "$__prompt"
  IFS= read -rsn1 __ch || exit 1
  if [[ "${__ch}" == $'\r' || "${__ch}" == $'\n' ]]; then
    __ch=""
  fi

  case "$__ch" in
    B) __ch="b" ;;
    Q) __ch="q" ;;
  esac

  printf '\n'
  if [[ "$__ch" == "b" ]]; then
    return 1
  fi
  if [[ "$__ch" == "q" ]] && (( ${SMTTY_PROMPT_QUIT_ENABLED:-0} )); then
    SMTTY_QUIT_REQUESTED=1
    return 3
  fi

  printf -v "$__var_name" '%s' "$__ch"
  return 0
}''',
)

text = replace_function(
    text,
    "read_default",
    "print_help",
    r'''read_default() {
  local prompt=$1
  local def=$2
  local val
  if ! backable_read val "$prompt [$def] (b = back): "; then
    if (( ${SMTTY_QUIT_REQUESTED:-0} )); then
      printf '%s\n' "$QUIT_SENTINEL"
    else
      printf '%s\n' "$BACK_SENTINEL"
    fi
    return 0
  fi
  if [[ -z "$val" ]]; then
    printf '%s\n' "$def"
  else
    printf '%s\n' "$val"
  fi
}''',
)

# Command substitutions cannot propagate shell variables. Any chooser receiving
# QUIT_SENTINEL converts it back into the process-level quit request.
sentinel_pattern = re.compile(
    r'(?m)^(?P<indent>\s*)if \[\[ "\$(?P<var>[A-Za-z_][A-Za-z0-9_]*)" == "\$BACK_SENTINEL" \]\]; then$'
)


def add_quit_check(match: re.Match[str]) -> str:
    indent = match.group("indent")
    var = match.group("var")
    return (
        f'{indent}if [[ "${var}" == "$QUIT_SENTINEL" ]]; then\n'
        f'{indent}  SMTTY_QUIT_REQUESTED=1\n'
        f'{indent}  return 1\n'
        f'{indent}fi\n'
        f'{indent}if [[ "${var}" == "$BACK_SENTINEL" ]]; then'
    )

text, sentinel_count = sentinel_pattern.subn(add_quit_check, text)
if sentinel_count < 8:
    raise SystemExit(f"only updated {sentinel_count} BACK_SENTINEL checks")

old_width = '''      read -r -p "Width [${NATIVE_W}] (q = cancel): " w
      [[ $w == "q" || $w == "Q" ]] && return 1
'''
new_width = '''      read -r -p "Width [${NATIVE_W}] (b = back, q = quit): " w
      case "${w,,}" in
        b) return 1 ;;
        q) SMTTY_QUIT_REQUESTED=1; return 1 ;;
      esac
'''
old_height = '''      read -r -p "Height [${NATIVE_H}] (q = cancel): " h
      [[ $h == "q" || $h == "Q" ]] && return 1
'''
new_height = '''      read -r -p "Height [${NATIVE_H}] (b = back, q = quit): " h
      case "${h,,}" in
        b) return 1 ;;
        q) SMTTY_QUIT_REQUESTED=1; return 1 ;;
      esac
'''
if old_width not in text or old_height not in text:
    raise SystemExit("custom resolution prompts did not match")
text = text.replace(old_width, new_width, 1)
text = text.replace(old_height, new_height, 1)

text = replace_function(
    text,
    "interactive_new_config",
    "run_from_current_config",
    r'''interactive_new_config() {
  local from_menu=${1:-0}
  local previous_quit_mode=${SMTTY_PROMPT_QUIT_ENABLED:-0}

  CURRENT_PROFILE=""
  PRE_CMD=""
  POST_CMD=""
  LD_PRELOAD_MODE="inherit"
  detect_session_mode

  G_FPS=0
  G_FPS_BG=0
  SMTTY_PROMPT_QUIT_ENABLED=1
  SMTTY_QUIT_REQUESTED=0

  local step=1
  while :; do
    SMTTY_QUIT_REQUESTED=0

    case "$step" in
      1)
        if ! detect_steam_installations; then
          SMTTY_PROMPT_QUIT_ENABLED=$previous_quit_mode
          if (( SMTTY_QUIT_REQUESTED )); then
            SMTTY_QUIT_REQUESTED=0
            echo "Guided setup cancelled."
            return 1
          fi
          if (( from_menu )); then
            return 1
          fi
          echo "Aborting interactive setup."
          return 1
        fi
        if ! choose_steam_launch_mode; then
          SMTTY_PROMPT_QUIT_ENABLED=$previous_quit_mode
          if (( SMTTY_QUIT_REQUESTED )); then
            SMTTY_QUIT_REQUESTED=0
            echo "Guided setup cancelled."
            return 1
          fi
          return 1
        fi
        step=2
        ;;
      2)
        if choose_drm_output; then
          step=3
        elif (( SMTTY_QUIT_REQUESTED )); then
          SMTTY_PROMPT_QUIT_ENABLED=$previous_quit_mode
          SMTTY_QUIT_REQUESTED=0
          echo "Guided setup cancelled."
          return 1
        else
          step=1
        fi
        ;;
      3)
        if choose_resolution_profile; then
          step=4
        elif (( SMTTY_QUIT_REQUESTED )); then
          SMTTY_PROMPT_QUIT_ENABLED=$previous_quit_mode
          SMTTY_QUIT_REQUESTED=0
          echo "Guided setup cancelled."
          return 1
        else
          step=2
        fi
        ;;
      4)
        if choose_gamescope_rate; then
          step=5
        elif (( SMTTY_QUIT_REQUESTED )); then
          SMTTY_PROMPT_QUIT_ENABLED=$previous_quit_mode
          SMTTY_QUIT_REQUESTED=0
          echo "Guided setup cancelled."
          return 1
        else
          step=3
        fi
        ;;
      5)
        if choose_vrr_hdr_and_steamos; then
          step=6
        elif (( SMTTY_QUIT_REQUESTED )); then
          SMTTY_PROMPT_QUIT_ENABLED=$previous_quit_mode
          SMTTY_QUIT_REQUESTED=0
          echo "Guided setup cancelled."
          return 1
        else
          step=4
        fi
        ;;
      6)
        if choose_pipewire_debug; then
          step=7
        elif (( SMTTY_QUIT_REQUESTED )); then
          SMTTY_PROMPT_QUIT_ENABLED=$previous_quit_mode
          SMTTY_QUIT_REQUESTED=0
          echo "Guided setup cancelled."
          return 1
        else
          step=5
        fi
        ;;
      7)
        if choose_pipewire_latency; then
          step=8
        elif (( SMTTY_QUIT_REQUESTED )); then
          SMTTY_PROMPT_QUIT_ENABLED=$previous_quit_mode
          SMTTY_QUIT_REQUESTED=0
          echo "Guided setup cancelled."
          return 1
        else
          step=6
        fi
        ;;
      8)
        if choose_perf_env_preset; then
          step=9
        elif (( SMTTY_QUIT_REQUESTED )); then
          SMTTY_PROMPT_QUIT_ENABLED=$previous_quit_mode
          SMTTY_QUIT_REQUESTED=0
          echo "Guided setup cancelled."
          return 1
        else
          step=7
        fi
        ;;
      9)
        if choose_ld_preload_mode; then
          step=10
        elif (( SMTTY_QUIT_REQUESTED )); then
          SMTTY_PROMPT_QUIT_ENABLED=$previous_quit_mode
          SMTTY_QUIT_REQUESTED=0
          echo "Guided setup cancelled."
          return 1
        else
          step=8
        fi
        ;;
      10)
        if choose_audio_switch; then
          step=11
        elif (( SMTTY_QUIT_REQUESTED )); then
          SMTTY_PROMPT_QUIT_ENABLED=$previous_quit_mode
          SMTTY_QUIT_REQUESTED=0
          echo "Guided setup cancelled."
          return 1
        else
          step=9
        fi
        ;;
      11)
        if choose_pre_post_commands; then
          step=12
        elif (( SMTTY_QUIT_REQUESTED )); then
          SMTTY_PROMPT_QUIT_ENABLED=$previous_quit_mode
          SMTTY_QUIT_REQUESTED=0
          echo "Guided setup cancelled."
          return 1
        else
          step=10
        fi
        ;;
      12)
        if save_config; then
          SMTTY_PROMPT_QUIT_ENABLED=$previous_quit_mode
          SMTTY_QUIT_REQUESTED=0
          load_profile_by_name "$CURRENT_PROFILE" >/dev/null 2>&1 || HAVE_CONFIG=1
          return 0
        fi
        if (( SMTTY_QUIT_REQUESTED )); then
          SMTTY_PROMPT_QUIT_ENABLED=$previous_quit_mode
          SMTTY_QUIT_REQUESTED=0
          echo "Guided setup cancelled."
          return 1
        fi
        step=11
        ;;
      *)
        SMTTY_PROMPT_QUIT_ENABLED=$previous_quit_mode
        SMTTY_QUIT_REQUESTED=0
        return 1
        ;;
    esac
  done
}''',
)

path.write_text(text, encoding="utf-8")
print(f"added guided quit support; updated {sentinel_count} sentinel checks")
