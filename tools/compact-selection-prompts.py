#!/usr/bin/env python3
from pathlib import Path

path = Path("smtty")
test_path = Path("tests/test-compact-prompts.sh")
text = path.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 match, found {count}")
    text = text.replace(old, new, 1)


def replace_all(old: str, new: str, label: str, minimum: int = 1) -> None:
    global text
    count = text.count(old)
    if count < minimum:
        raise SystemExit(f"{label}: expected at least {minimum} matches, found {count}")
    text = text.replace(old, new)


replace_once(
'''smtty_print_compact_actions() {
  echo "Actions"
  printf '  %-23s %-23s %s\\n' "[P] [8] Play" "[G] [1] Select game" "[O] [12] Launch options"
  printf '  %-23s %-23s %s\\n' "[S] [9] Profiles" "[N] [10] New profile" "[D] [11] Delete profile"
  printf '  %-23s %-23s %s\\n' "[E] [14] Edit profile" "[M] [4] MangoHud" "[W] [13] Wayland"
  printf '  %-23s %-23s %s\\n' "[L] [2] Lock game" "[U] [3] Unlock game" "[C] [6] Clear game"
  printf '  %-23s %-23s %s\\n' "[T] [5] Diagnostics" "[V] [7] Version" "[Q] Quit"
}
''',
'''smtty_print_action_row() {
  printf '  %-9s %-15s  %-9s %-16s  %-9s %s\\n' \\
    "$1" "$2" "$3" "$4" "$5" "$6"
}

smtty_print_compact_actions() {
  echo "Actions"
  smtty_print_action_row "[P] [8]"  "Play"         "[G] [1]"  "Select game" "[O] [12]" "Launch options"
  smtty_print_action_row "[S] [9]"  "Profiles"     "[N] [10]" "New profile" "[D] [11]" "Delete profile"
  smtty_print_action_row "[E] [14]" "Edit profile" "[M] [4]"  "MangoHud"    "[W] [13]" "Wayland"
  smtty_print_action_row "[L] [2]"  "Lock game"    "[U] [3]"  "Unlock game" "[C] [6]"  "Clear game"
  smtty_print_action_row "[T] [5]"  "Diagnostics"  "[V] [7]"  "Version"     "[Q]"      "Quit"
}
''',
"action grid",
)

replace_once('    print_info "Auto-detected max refresh for $DRM_SHORT at ${NATIVE_W}x${NATIVE_H}: ${G_FPS} Hz"\n    echo\n', '', "silent refresh detection")
replace_once('  echo "Detected *connected* outputs:"\n', '  echo "Displays"\n', "display heading")
replace_once("    printf '  [%d] %s (native: %s)\\n' \"$idx\" \"$short\" \"$native_line\"\n", "    printf '  [%d] %s · %s\\n' \"$idx\" \"$short\" \"$native_line\"\n", "display rows")
replace_all('Select output [1-${#entries[@]}, b = back]: ', 'Choose display [1-${#entries[@]}, b = back]: ', "display prompt", 2)
replace_once(
'''  echo
  echo "Using output: $DRM_SHORT (native ${NATIVE_W}x${NATIVE_H})"
  echo "Session mode: $SESSION_MODE (kms = bare VT, nested = under compositor)"
  echo
  if [[ "$SESSION_MODE" == "nested" ]]; then
    echo "Note: running under a compositor. gamescope will be nested as a window"
    echo "      or fullscreen surface. Physical monitor resolution is not changed,"
    echo "      but gamescope still controls internal and outer resolutions/scaling."
    echo
  fi
''',
'''  echo
  printf 'Display: %s · %sx%s · %s\\n\\n' \\
    "$DRM_SHORT" "$NATIVE_W" "$NATIVE_H" "${SESSION_MODE^}"
''',
"selected display summary",
)

replace_all("Custom width in px [${NATIVE_W}] (or 'q' to cancel): ", "Width [${NATIVE_W}] (q = cancel): ", "custom width")
replace_all("Custom height in px [${NATIVE_H}] (or 'q' to cancel): ", "Height [${NATIVE_H}] (q = cancel): ", "custom height")
replace_once('    if ! prompt_select_default "Stretch mode" 1 \\\n      "Stretch to fill ${NATIVE_W}x${NATIVE_H} (distorts)" \\\n      "Keep aspect (black bars)"; then\n', '    if ! prompt_select_default "Scaling" 1 \\\n      "Fill screen (stretch)" \\\n      "Keep aspect (black bars)"; then\n', "scaling prompt")
replace_all('    echo "Resolution profile for 1080p 16:9:"\n', '    echo "Render resolution"\n', "1080 heading")
replace_all('    echo "Resolution profile for 1440p 16:9:"\n', '    echo "Render resolution"\n', "1440 heading")
replace_all('    echo "Resolution profile for 4K 16:9:"\n', '    echo "Render resolution"\n', "4k heading")
replace_all('prompt_select_default "Choose profile"', 'prompt_select_default "Choose"', "resolution choice", 3)
replace_all('(4:3 base, downscale)', '· 4:3 downscale', "4:3 downscale")
replace_all('(4:3 base)', '· 4:3', "4:3 label")
replace_all('(16:10 base, downscale)', '· 16:10 downscale', "16:10 downscale")
replace_all('(16:10 base)', '· 16:10', "16:10 label")
replace_all('(downscale base)', '· downscale', "downscale label")

replace_once('  val=$(read_default "Target display refresh for gamescope (-r, Hz; 0 = auto-detect max via modetest, else unlimited)" "$G_FPS")\n', '  val=$(read_default "Display refresh (Hz, 0 = auto)" "$G_FPS")\n', "display refresh prompt")
replace_once('  if ! backable_read raw "Nested unfocused refresh (-o, Hz, empty = disabled, b = back): "; then\n', '  if ! backable_read raw "Unfocused refresh (Hz, empty = off, b = back): "; then\n', "unfocused prompt")
replace_once('    echo "Invalid value; disabling -o."\n', '    echo "Invalid value; using off."\n', "unfocused error")

replace_once('  echo "Optional gamescope features:"\n', '  echo "Features"\n', "features heading")
replace_once('    vrr=$(read_default "Enable gamescope adaptive sync / VRR? (0 = no, 1 = yes)" "$ADAPTIVE_SYNC")\n', '    vrr=$(read_default "VRR (0 = off, 1 = on)" "$ADAPTIVE_SYNC")\n', "VRR prompt")
replace_once('    hdr=$(read_default "Enable gamescope HDR output? (0 = no, 1 = yes)" "$ENABLE_GAMESCOPE_HDR")\n', '    hdr=$(read_default "HDR (0 = off, 1 = on)" "$ENABLE_GAMESCOPE_HDR")\n', "HDR prompt")
replace_once('    nits=$(read_default "HDR ITM target nits (gamescope --hdr-itm-target-nits)" "$default_nits")\n', '    nits=$(read_default "HDR target nits" "$default_nits")\n', "HDR nits prompt")
replace_once(
'''  echo
  echo "Cursor grab:"
  echo "  Mostly useful on bare TTY (KMS). In nested sessions it can make"
  echo "  mouse input worse if games and overlays already manage grabs."
''',
'''  echo
  echo "Cursor grab is mainly useful in KMS sessions."
''',
"cursor explanation",
)
replace_once('    fg=$(read_default "Force gamescope cursor grab? (0 = no, 1 = yes)" "$FORCE_GRAB_CURSOR")\n', '    fg=$(read_default "Cursor grab (0 = off, 1 = on)" "$FORCE_GRAB_CURSOR")\n', "cursor prompt")
replace_once(
'''  echo
  echo "Wayland exposure:"
  echo "  Enables native Wayland clients inside gamescope (--expose-wayland)."
  echo "  Usually not needed for Proton/X11 games; can cause odd behavior on some setups."
''',
'''  echo
  echo "Wayland exposure is only needed by native Wayland clients."
''',
"Wayland explanation",
)
replace_once('    ew=$(read_default "Expose Wayland to clients inside gamescope? (0 = no, 1 = yes)" "$EXPOSE_WAYLAND")\n', '    ew=$(read_default "Expose Wayland (0 = off, 1 = on)" "$EXPOSE_WAYLAND")\n', "Wayland prompt")
replace_once(
'''    echo "Low-latency / tearing (advanced, KMS sessions only):"
    echo "  Enables SteamOS-style tearing capability flags for Steam running inside gamescope."
    echo "  Can reduce latency, but may cause visible tearing, break capture, or regress smoothness."
''',
'''    echo "Low-latency tearing (KMS only; may break capture)."
''',
"tearing explanation",
)
replace_once('      lt=$(read_default "Enable low-latency / tearing mode? (0 = no, 1 = yes)" "$LOW_LATENCY_TEARING")\n', '      lt=$(read_default "Low-latency tearing (0 = off, 1 = on)" "$LOW_LATENCY_TEARING")\n', "tearing prompt")

replace_once(
'''  echo "PipeWire / gamescope log verbosity:"
  echo "  This controls PIPEWIRE_DEBUG for the gamescope process only."
  echo "  Lower values reduce spam like 'pipewire: warning: out of buffers'."
  echo
  echo "  [1] Inherit system default (do not set PIPEWIRE_DEBUG)"
  echo "  [2] Disabled [PIPEWIRE_DEBUG=0]"
  echo "  [3] Errors [PIPEWIRE_DEBUG=1]"
  echo "  [4] Warnings [PIPEWIRE_DEBUG=2]"
  echo "  [5] Informational messages [PIPEWIRE_DEBUG=3]"
''',
'''  echo "PipeWire logging"
  echo "  [1] Inherit   [2] Off   [3] Errors   [4] Warnings   [5] Info"
''',
"PipeWire logging menu",
)
replace_once('  sel=$(read_default "Choose PipeWire debug level (1-5)" "$default_choice")\n', '  sel=$(read_default "Choose (1-5)" "$default_choice")\n', "PipeWire prompt")
replace_once(
'''  echo
  echo "PipeWire debug mode set to: $PIPEWIRE_DEBUG_MODE"
  echo "  inherit  = smtty leaves PIPEWIRE_DEBUG alone"
  echo "  0        = logging disabled"
  echo "  1        = errors"
  echo "  2        = warnings"
  echo "  3        = informational messages"
  echo
''',
'''  echo
  echo "PipeWire debug: $PIPEWIRE_DEBUG_MODE"
  echo
''',
"PipeWire confirmation",
)
replace_once(
'''  echo
  echo "PipeWire latency hint (optional)."
  echo "  This sets PIPEWIRE_LATENCY for gamescope only."
  echo "  Use 'inherit' unless you know you need this."
  echo "  Examples: 128/48000  64/48000"
  echo
''',
'''  echo
  echo "PipeWire latency"
  echo "  inherit or frames/rate, e.g. 128/48000"
''',
"PipeWire latency text",
)
replace_once('    val="$(read_default "PIPEWIRE_LATENCY" "$cur")"\n', '    val="$(read_default "Latency" "$cur")"\n', "latency prompt")
replace_all('PipeWire latency env set to:', 'PipeWire latency:', "latency confirmation", 2)

replace_once(
'''  echo
  echo "Perf/shader cache preset (optional)."
  echo "  Goal: reduce shader-compilation stutter on some titles across launches."
  echo "  0 = off (default)"
  echo "  1 = on  (enables extra caching; uses more disk space)"
  echo "  Notes:"
  echo "    - Applies only to this smtty session/profile (not global)."
  echo "    - Not an FPS boost. May do nothing depending on game/renderer."
  echo "    - What it sets (vendor-aware):"
  echo "      * DXVK_STATE_CACHE=1"
  echo "      * AMD/Intel (Mesa): MESA_SHADER_CACHE_MAX_SIZE=4G"
  echo "      * NVIDIA (OpenGL): __GL_SHADER_DISK_CACHE=1"
  echo
''',
'''  echo
  echo "Shader-cache preset"
  echo "  [0] Off"
  echo "  [1] On · vendor-aware caching; may use more disk"
''',
"shader cache menu",
)
replace_once('    val="$(read_default "PERF_ENV_PRESET (0/1)" "$cur")"\n', '    val="$(read_default "Choose (0/1)" "$cur")"\n', "shader cache prompt")
replace_once('      echo "Perf env preset set to: $PERF_ENV_PRESET"\n', '      [[ "$val" == "1" ]] && echo "Shader cache: On" || echo "Shader cache: Off"\n', "shader cache confirmation")

replace_once(
'''  echo "LD_PRELOAD handling for gamescope / Steam:"
  echo "  Clearing LD_PRELOAD avoids inherited overlays/shims (MangoHud, vkBasalt,"
  echo "  etc.) from injecting into gamescope or the game."
  echo
  echo "  [1] Inherit current LD_PRELOAD (do nothing)"
  echo "  [2] Clear LD_PRELOAD for gamescope and Steam"
''',
'''  echo "LD_PRELOAD"
  echo "  [1] Inherit"
  echo "  [2] Clear · avoids inherited overlays and shims"
''',
"LD_PRELOAD menu",
)
replace_once('  sel=$(read_default "Choose LD_PRELOAD mode (1-2)" "$default_choice")\n', '  sel=$(read_default "Choose (1-2)" "$default_choice")\n', "LD_PRELOAD prompt")
replace_once(
'''  echo
  echo "LD_PRELOAD mode set to: $LD_PRELOAD_MODE"
  echo "  inherit = pass through existing LD_PRELOAD"
  echo "  clear   = export LD_PRELOAD=\"\" before gamescope"
  echo
''',
'''  echo
  echo "LD_PRELOAD: ${LD_PRELOAD_MODE^}"
  echo
''',
"LD_PRELOAD confirmation",
)

replace_once('  echo "Temporary audio output switching (PulseAudio / PipeWire via pactl):"\n', '  echo "Audio switching"\n', "audio heading")
replace_once('    echo "  pactl not found; audio device switching will be disabled."\n', '    echo "  pactl not found; disabled."\n', "audio missing dependency")
replace_once('  en=$(read_default "Enable automatic audio output switch while gamescope is running? (0 = no, 1 = yes)" 0)\n', '  en=$(read_default "Switch output while running (0 = off, 1 = on)" 0)\n', "audio prompt")
replace_once('  echo "Available audio outputs (PulseAudio / PipeWire sinks):"\n', '  echo "Audio outputs"\n', "audio outputs heading")
replace_all('Choose sink to use while gamescope is running [1-${#sink_names[@]}, b = back]: ', 'Choose output [1-${#sink_names[@]}, b = back]: ', "audio selection prompt", 2)
replace_once(
'''  echo
  echo "Audio switcher will use:"
  echo "  Description: ${sink_descs[choice-1]}"
  echo "  Name:        ${AUDIO_SINK_NAME}"
  echo
''',
'''  echo
  echo "Audio output: ${sink_descs[choice-1]}"
  echo
''',
"audio confirmation",
)

replace_once(
'''  echo "Optional pre / post shell commands for this profile:"
  echo "  Pre-command runs asynchronously before gamescope starts."
  echo "  Post-command runs when the gamescope session ends."
  echo "  Leave empty to skip."
  echo
''',
'''  echo "Hooks (optional)"
  echo "  Pre runs before launch; post runs on exit. Empty disables."
''',
"hooks text",
)
replace_once('  pre=$(read_default "Pre-command (empty = none)" "${PRE_CMD:-}")\n', '  pre=$(read_default "Pre command" "${PRE_CMD:-}")\n', "pre hook prompt")
replace_once('  post=$(read_default "Post-command (empty = none)" "${POST_CMD:-}")\n', '  post=$(read_default "Post command" "${POST_CMD:-}")\n', "post hook prompt")

replace_once('  echo "Save this configuration as a named profile."\n  echo "Examples: gaming, 4k-monitor, stretched-43, desktop-session"\n', '  echo "Save profile"\n  echo "  Examples: gaming, stretched-43, desktop-session"\n', "profile name heading")
replace_once('    if ! backable_read profile_name "Profile name [$default_name] (b = back): "; then\n', '    if ! backable_read profile_name "Name [$default_name] (b = back): "; then\n', "profile name prompt")

replace_once('    echo "Installed Steam games (page $((page + 1))/$pages, showing $((start + 1))-$end of $total, page size $page_size):"\n', '    echo "Steam games · page $((page + 1))/$pages · $((start + 1))-$end of $total"\n', "game picker heading")
replace_once('    echo "  [N] Next page   [P] Previous page   [G] Set page size   [B] Back   [F] Find"\n', '    echo "  [N] Next   [P] Previous   [G] Page size   [F] Find   [B] Back"\n', "game picker controls")
replace_once('    printf "Select game (1-%d) or n/p/g/b/f: " "$on_page"\n', '    printf "Choose [1-%d/N/P/G/F/B]: " "$on_page"\n', "game picker prompt")
replace_once('      read -r -p "Find game name (empty clears): " __smtty_find\n', '      read -r -p "Find (empty = clear): " __smtty_find\n', "game finder prompt")
replace_once('        if ! backable_read newps "Games per page [$page_size] (5-$max, b = back): "; then\n', '        if ! backable_read newps "Page size [$page_size] (5-$max, b = back): "; then\n', "page size prompt")

path.write_text(text, encoding="utf-8")

test_path.write_text(r'''#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
source_file="$repo_root/smtty"
helper_file=$(mktemp)
trap 'rm -f "$helper_file"' EXIT

sed -n '/^# SMTTY_COMPACT_UI_BEGIN$/,/^# SMTTY_COMPACT_UI_END$/p' "$source_file" >"$helper_file"
# shellcheck disable=SC1090
source "$helper_file"

actions=$(smtty_print_compact_actions)
expected_first='  [P] [8]   Play             [G] [1]   Select game       [O] [12]  Launch options'
expected_edit='  [E] [14]  Edit profile     [M] [4]   MangoHud          [W] [13]  Wayland'
expected_quit='  [T] [5]   Diagnostics      [V] [7]   Version           [Q]       Quit'

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
''', encoding="utf-8")

print("compacted action alignment and selection prompts")
