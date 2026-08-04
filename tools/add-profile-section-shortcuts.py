#!/usr/bin/env python3
from pathlib import Path

smtty_path = Path("smtty")
test_path = Path("tests/test-profile-workflow.sh")
smtty = smtty_path.read_text(encoding="utf-8")
tests = test_path.read_text(encoding="utf-8")

start = smtty.index("interactive_profile_settings_editor() {")
end = smtty.index("\ninteractive_profile_menu() {", start)
block = smtty[start:end]

old_heading = '''    if (( is_new )); then
      echo "New profile · unsaved"
    else
      echo "Edit profile: ${prof}"
    fi
    echo
    smtty_print_compact_summary 0 ""
    echo
'''
new_heading = '''    if (( is_new )); then
      echo "New profile · unsaved"
      echo
      echo "Review this draft. Change only what you need, then save."
    else
      echo "Edit profile: ${prof}"
      echo
      echo "Select a section to modify."
    fi
    echo
    smtty_print_compact_summary 0 ""
    echo
'''
if old_heading not in block:
    raise SystemExit("profile editor heading block did not match")
block = block.replace(old_heading, new_heading, 1)

old_sections = '''    echo "Sections"
    printf '  %-20s %-20s %s\\n' "[1] Steam" "[2] Display" "[3] Resolution"
    printf '  %-20s %-20s %s\\n' "[4] Refresh" "[5] Features" "[6] PipeWire"
    printf '  %-20s %-20s %s\\n' "[7] Performance" "[8] LD_PRELOAD" "[9] Audio"
    if (( is_new )); then
      printf '  %-20s %-20s %s\\n' "[0] Hooks" "[S] Save" "[Q] Cancel"
    else
      printf '  %-20s %-20s %s\\n' "[0] Hooks" "[S] Save" "[B] Back"
    fi
'''
new_sections = '''    echo "Sections"
    smtty_print_action_row "[T] [1]" "Steam"        "[D] [2]" "Display"      "[R] [3]" "Resolution"
    smtty_print_action_row "[F] [4]" "Refresh"      "[E] [5]" "Features"     "[P] [6]" "PipeWire"
    smtty_print_action_row "[C] [7]" "Shader cache" "[L] [8]" "LD_PRELOAD"   "[A] [9]" "Audio"
    if (( is_new )); then
      smtty_print_action_row "[H] [0]" "Hooks" "[S]" "Save" "[Q]" "Cancel"
    else
      smtty_print_action_row "[H] [0]" "Hooks" "[S]" "Save" "[B]" "Back"
    fi
'''
if old_sections not in block:
    raise SystemExit("profile editor section grid did not match")
block = block.replace(old_sections, new_sections, 1)

aliases = {
    "\n      1)\n": "\n      t|1)\n",
    "\n      2)\n": "\n      d|2)\n",
    "\n      3)\n": "\n      r|3)\n",
    "\n      4)\n": "\n      f|4)\n",
    "\n      5)\n": "\n      e|5)\n",
    "\n      6)\n": "\n      p|6)\n",
    "\n      7)\n": "\n      c|7)\n",
    "\n      8)\n": "\n      l|8)\n",
    "\n      9)\n": "\n      a|9)\n",
    "\n      0)\n": "\n      h|0)\n",
}
for old, new in aliases.items():
    if block.count(old) != 1:
        raise SystemExit(f"expected one editor case label: {old.strip()}")
    block = block.replace(old, new, 1)

block = block.replace(
    '''        if (( is_new )); then
          echo "Choose 1-9, 0, S, or Q."
        else
          echo "Choose 1-9, 0, S, or B."
        fi
''',
    '''        echo "Choose a listed letter or number."
''',
    1,
)

smtty = smtty[:start] + block + smtty[end:]

old_test = '''[[ "$editor_block" == *'New profile · unsaved'* ]]
[[ "$editor_block" == *'"[S] Save" "[Q] Cancel"'* ]]
[[ "$editor_block" == *'Discard unsaved profile?'* ]]
[[ "$editor_block" == *'return 2'* ]]
[[ "$editor_block" == *'if choose_gamescope_rate && (( ! is_new ))'* ]]
'''
new_test = '''[[ "$editor_block" == *'New profile · unsaved'* ]]
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
[[ "$editor_block" == *'smtty_print_action_row "[H] [0]" "Hooks" "[S]" "Save" "[Q]" "Cancel"'* ]]
[[ "$editor_block" == *'t|1)'* ]]
[[ "$editor_block" == *'d|2)'* ]]
[[ "$editor_block" == *'r|3)'* ]]
[[ "$editor_block" == *'f|4)'* ]]
[[ "$editor_block" == *'e|5)'* ]]
[[ "$editor_block" == *'p|6)'* ]]
[[ "$editor_block" == *'c|7)'* ]]
[[ "$editor_block" == *'l|8)'* ]]
[[ "$editor_block" == *'a|9)'* ]]
[[ "$editor_block" == *'h|0)'* ]]
[[ "$editor_block" == *'Discard unsaved profile?'* ]]
[[ "$editor_block" == *'return 2'* ]]
[[ "$editor_block" == *'if choose_gamescope_rate && (( ! is_new ))'* ]]
'''
if old_test not in tests:
    raise SystemExit("profile workflow assertions did not match")
tests = tests.replace(old_test, new_test, 1)

smtty_path.write_text(smtty, encoding="utf-8")
test_path.write_text(tests, encoding="utf-8")
print("added profile section mnemonics and editor guidance")
