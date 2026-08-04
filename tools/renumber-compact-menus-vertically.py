#!/usr/bin/env python3
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def replace_in_block(text: str, start: str, end: str, replacements: list[tuple[str, str, str]]) -> str:
    start_at = text.find(start)
    if start_at < 0:
        raise SystemExit(f"missing block start: {start}")
    end_at = text.find(end, start_at)
    if end_at < 0:
        raise SystemExit(f"missing block end: {end}")

    block = text[start_at:end_at]
    for old, new, label in replacements:
        block = replace_once(block, old, new, label)
    return text[:start_at] + block + text[end_at:]


smtty_path = Path("smtty")
compact_ui_path = Path("tests/test-compact-ui.sh")
compact_prompts_path = Path("tests/test-compact-prompts.sh")
profile_workflow_path = Path("tests/test-profile-workflow.sh")

smtty = smtty_path.read_text(encoding="utf-8")
compact_ui = compact_ui_path.read_text(encoding="utf-8")
compact_prompts = compact_prompts_path.read_text(encoding="utf-8")
profile_workflow = profile_workflow_path.read_text(encoding="utf-8")

smtty = replace_in_block(
    smtty,
    "smtty_print_compact_actions() {",
    "# SMTTY_COMPACT_UI_END",
    [
        (
            '  smtty_print_action_row "[P] [1]"  "Play"         "[G] [2]"  "Select game" "[O] [3]"  "Launch options"\n',
            '  smtty_print_action_row "[P] [1]"  "Play"         "[G] [6]"  "Select game" "[O] [11]" "Launch options"\n',
            "main action row 1",
        ),
        (
            '  smtty_print_action_row "[S] [4]"  "Profiles"     "[N] [5]"  "New profile" "[D] [6]"  "Delete profile"\n',
            '  smtty_print_action_row "[S] [2]"  "Profiles"     "[N] [7]"  "New profile" "[D] [12]" "Delete profile"\n',
            "main action row 2",
        ),
        (
            '  smtty_print_action_row "[E] [7]"  "Edit profile" "[M] [8]"  "MangoHud"    "[W] [9]"  "Wayland"\n',
            '  smtty_print_action_row "[E] [3]"  "Edit profile" "[M] [8]"  "MangoHud"    "[W] [13]" "Wayland"\n',
            "main action row 3",
        ),
        (
            '  smtty_print_action_row "[L] [10]" "Lock game"    "[U] [11]" "Unlock game" "[C] [12]" "Clear game"\n',
            '  smtty_print_action_row "[L] [4]"  "Lock game"    "[U] [9]"  "Unlock game" "[C] [14]" "Clear game"\n',
            "main action row 4",
        ),
        (
            '  smtty_print_action_row "[T] [13]" "Diagnostics"  "[V] [14]" "Version"     "[Q]"      "Quit"\n',
            '  smtty_print_action_row "[T] [5]"  "Diagnostics"  "[V] [10]" "Version"     "[Q]"      "Quit"\n',
            "main action row 5",
        ),
    ],
)

smtty = replace_in_block(
    smtty,
    "interactive_profile_settings_editor() {",
    "interactive_profile_menu() {",
    [
        ('smtty_print_action_row "[T] [1]" "Steam"        "[D] [2]" "Display"      "[R] [3]" "Resolution"',
         'smtty_print_action_row "[T] [1]" "Steam"        "[D] [5]" "Display"      "[R] [8]" "Resolution"',
         "profile row 1"),
        ('smtty_print_action_row "[F] [4]" "Refresh"      "[E] [5]" "Features"     "[P] [6]" "PipeWire"',
         'smtty_print_action_row "[F] [2]" "Refresh"      "[E] [6]" "Features"     "[P] [9]" "PipeWire"',
         "profile row 2"),
        ('smtty_print_action_row "[C] [7]" "Shader cache" "[L] [8]" "LD_PRELOAD"   "[A] [9]" "Audio"',
         'smtty_print_action_row "[C] [3]" "Shader cache" "[L] [7]" "LD_PRELOAD"   "[A] [10]" "Audio"',
         "profile row 3"),
        ('smtty_print_action_row "[H] [10]" "Hooks" "[S]" "Save" "[Q]" "Cancel"',
         'smtty_print_action_row "[H] [4]" "Hooks" "[S]" "Save" "[Q]" "Cancel"',
         "new-profile footer"),
        ('smtty_print_action_row "[H] [10]" "Hooks" "[S]" "Save" "[B]" "Back"',
         'smtty_print_action_row "[H] [4]" "Hooks" "[S]" "Save" "[B]" "Back"',
         "edit-profile footer"),
        ('      d|2)\n', '      d|5)\n', "Display dispatch"),
        ('      r|3)\n', '      r|8)\n', "Resolution dispatch"),
        ('      f|4)\n', '      f|2)\n', "Refresh dispatch"),
        ('      e|5)\n', '      e|6)\n', "Features dispatch"),
        ('      p|6)\n', '      p|9)\n', "PipeWire dispatch"),
        ('      c|7)\n', '      c|3)\n', "Shader-cache dispatch"),
        ('      l|8)\n', '      l|7)\n', "LD_PRELOAD dispatch"),
        ('      a|9)\n', '      a|10)\n', "Audio dispatch"),
        ('      h|10)\n', '      h|4)\n', "Hooks dispatch"),
    ],
)

smtty = replace_in_block(
    smtty,
    "interactive_profile_menu() {",
    "cleanup_old_session_artifacts() {",
    [
        ('      w|9)\n', '      w|13)\n', "Wayland dispatch"),
        ('      e|7)\n', '      e|3)\n', "Edit dispatch"),
        ('      s|4)\n', '      s|2)\n', "Profiles dispatch"),
        ('      n|5)\n', '      n|7)\n', "New-profile dispatch"),
        ('      d|6)\n', '      d|12)\n', "Delete-profile dispatch"),
        ('      g|2)\n', '      g|6)\n', "Select-game dispatch"),
        ('Use [L] or [10] to persist it.', 'Use [L] or [4] to persist it.', "lock shortcut message"),
        ('      t|h|13)\n', '      t|h|5)\n', "Diagnostics dispatch"),
        ('      l|10)\n', '      l|4)\n', "Lock-game dispatch"),
        ('      u|11)\n', '      u|9)\n', "Unlock-game dispatch"),
        ('      c|12)\n', '      c|14)\n', "Clear-game dispatch"),
        ('      v|14)\n', '      v|10)\n', "Version dispatch"),
        ('      o|3)\n', '      o|11)\n', "Launch-options dispatch"),
    ],
)

old_alias_checks = '''[[ "$actions" == *"[P] [1]"* ]] || fail "numeric alias 1 missing"
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
'''
new_alias_checks = '''[[ "$actions" == *"[P] [1]"* ]] || fail "numeric alias 1 missing"
[[ "$actions" == *"[S] [2]"* ]] || fail "numeric alias 2 missing"
[[ "$actions" == *"[E] [3]"* ]] || fail "numeric alias 3 missing"
[[ "$actions" == *"[L] [4]"* ]] || fail "numeric alias 4 missing"
[[ "$actions" == *"[T] [5]"* ]] || fail "numeric alias 5 missing"
[[ "$actions" == *"[G] [6]"* ]] || fail "numeric alias 6 missing"
[[ "$actions" == *"[N] [7]"* ]] || fail "numeric alias 7 missing"
[[ "$actions" == *"[M] [8]"* ]] || fail "numeric alias 8 missing"
[[ "$actions" == *"[U] [9]"* ]] || fail "numeric alias 9 missing"
[[ "$actions" == *"[V] [10]"* ]] || fail "numeric alias 10 missing"
[[ "$actions" == *"[O] [11]"* ]] || fail "numeric alias 11 missing"
[[ "$actions" == *"[D] [12]"* ]] || fail "numeric alias 12 missing"
[[ "$actions" == *"[W] [13]"* ]] || fail "numeric alias 13 missing"
[[ "$actions" == *"[C] [14]"* ]] || fail "numeric alias 14 missing"
'''
compact_ui = replace_once(compact_ui, old_alias_checks, new_alias_checks, "compact UI alias assertions")

old_dispatch_checks = '''[[ "$menu_block" == *'p|1)'* ]] || fail "Play numeric dispatch is not 1"
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
'''
new_dispatch_checks = '''[[ "$menu_block" == *'p|1)'* ]] || fail "Play numeric dispatch is not 1"
[[ "$menu_block" == *'s|2)'* ]] || fail "Profiles numeric dispatch is not 2"
[[ "$menu_block" == *'e|3)'* ]] || fail "Edit profile numeric dispatch is not 3"
[[ "$menu_block" == *'l|4)'* ]] || fail "Lock game numeric dispatch is not 4"
[[ "$menu_block" == *'t|h|5)'* ]] || fail "Diagnostics numeric dispatch is not 5"
[[ "$menu_block" == *'g|6)'* ]] || fail "Select game numeric dispatch is not 6"
[[ "$menu_block" == *'n|7)'* ]] || fail "New profile numeric dispatch is not 7"
[[ "$menu_block" == *'m|8)'* ]] || fail "MangoHud numeric dispatch is not 8"
[[ "$menu_block" == *'u|9)'* ]] || fail "Unlock game numeric dispatch is not 9"
[[ "$menu_block" == *'v|10)'* ]] || fail "Version numeric dispatch is not 10"
[[ "$menu_block" == *'o|11)'* ]] || fail "Launch options numeric dispatch is not 11"
[[ "$menu_block" == *'d|12)'* ]] || fail "Delete profile numeric dispatch is not 12"
[[ "$menu_block" == *'w|13)'* ]] || fail "Wayland numeric dispatch is not 13"
[[ "$menu_block" == *'c|14)'* ]] || fail "Clear game numeric dispatch is not 14"
'''
compact_ui = replace_once(compact_ui, old_dispatch_checks, new_dispatch_checks, "compact UI dispatch assertions")

compact_prompts = replace_once(
    compact_prompts,
    "expected_first='  [P] [1]   Play             [G] [2]   Select game       [O] [3]   Launch options'",
    "expected_first='  [P] [1]   Play             [G] [6]   Select game       [O] [11]  Launch options'",
    "compact prompt first row",
)
compact_prompts = replace_once(
    compact_prompts,
    "expected_edit='  [E] [7]   Edit profile     [M] [8]   MangoHud          [W] [9]   Wayland'",
    "expected_edit='  [E] [3]   Edit profile     [M] [8]   MangoHud          [W] [13]  Wayland'",
    "compact prompt edit row",
)
compact_prompts = replace_once(
    compact_prompts,
    "expected_quit='  [T] [13]  Diagnostics      [V] [14]  Version           [Q]       Quit'",
    "expected_quit='  [T] [5]   Diagnostics      [V] [10]  Version           [Q]       Quit'",
    "compact prompt final row",
)

profile_replacements = [
    ('smtty_print_action_row "[T] [1]" "Steam"', 'smtty_print_action_row "[T] [1]" "Steam"', "Steam label"),
    ('"[D] [2]" "Display"', '"[D] [5]" "Display"', "Display label"),
    ('"[R] [3]" "Resolution"', '"[R] [8]" "Resolution"', "Resolution label"),
    ('smtty_print_action_row "[F] [4]" "Refresh"', 'smtty_print_action_row "[F] [2]" "Refresh"', "Refresh label"),
    ('"[E] [5]" "Features"', '"[E] [6]" "Features"', "Features label"),
    ('"[P] [6]" "PipeWire"', '"[P] [9]" "PipeWire"', "PipeWire label"),
    ('smtty_print_action_row "[C] [7]" "Shader cache"', 'smtty_print_action_row "[C] [3]" "Shader cache"', "Shader label"),
    ('"[L] [8]" "LD_PRELOAD"', '"[L] [7]" "LD_PRELOAD"', "LD_PRELOAD label"),
    ('"[A] [9]" "Audio"', '"[A] [10]" "Audio"', "Audio label"),
    ('smtty_print_action_row "[H] [10]" "Hooks" "[S]" "Save" "[Q]" "Cancel"', 'smtty_print_action_row "[H] [4]" "Hooks" "[S]" "Save" "[Q]" "Cancel"', "Hooks label"),
    ("d|2)", "d|5)", "Display workflow dispatch"),
    ("r|3)", "r|8)", "Resolution workflow dispatch"),
    ("f|4)", "f|2)", "Refresh workflow dispatch"),
    ("e|5)", "e|6)", "Features workflow dispatch"),
    ("p|6)", "p|9)", "PipeWire workflow dispatch"),
    ("c|7)", "c|3)", "Shader workflow dispatch"),
    ("l|8)", "l|7)", "LD_PRELOAD workflow dispatch"),
    ("a|9)", "a|10)", "Audio workflow dispatch"),
    ("h|10)", "h|4)", "Hooks workflow dispatch"),
]
for old, new, label in profile_replacements:
    if old == new:
        if old not in profile_workflow:
            raise SystemExit(f"{label}: marker missing")
        continue
    profile_workflow = replace_once(profile_workflow, old, new, label)

for forbidden in (
    '"[G] [2]"  "Select game"',
    '"[H] [10]" "Hooks"',
    '      g|2)\n',
    '      h|10)\n',
):
    if forbidden in smtty:
        raise SystemExit(f"horizontal numeric mapping remains: {forbidden!r}")

smtty_path.write_text(smtty, encoding="utf-8")
compact_ui_path.write_text(compact_ui, encoding="utf-8")
compact_prompts_path.write_text(compact_prompts, encoding="utf-8")
profile_workflow_path.write_text(profile_workflow, encoding="utf-8")
print("renumbered compact menus vertically")
