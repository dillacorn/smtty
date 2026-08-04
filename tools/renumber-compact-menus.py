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
            '  smtty_print_action_row "[P] [8]"  "Play"         "[G] [1]"  "Select game" "[O] [12]" "Launch options"\n',
            '  smtty_print_action_row "[P] [1]"  "Play"         "[G] [2]"  "Select game" "[O] [3]"  "Launch options"\n',
            "main action row 1",
        ),
        (
            '  smtty_print_action_row "[S] [9]"  "Profiles"     "[N] [10]" "New profile" "[D] [11]" "Delete profile"\n',
            '  smtty_print_action_row "[S] [4]"  "Profiles"     "[N] [5]"  "New profile" "[D] [6]"  "Delete profile"\n',
            "main action row 2",
        ),
        (
            '  smtty_print_action_row "[E] [14]" "Edit profile" "[M] [4]"  "MangoHud"    "[W] [13]" "Wayland"\n',
            '  smtty_print_action_row "[E] [7]"  "Edit profile" "[M] [8]"  "MangoHud"    "[W] [9]"  "Wayland"\n',
            "main action row 3",
        ),
        (
            '  smtty_print_action_row "[L] [2]"  "Lock game"    "[U] [3]"  "Unlock game" "[C] [6]"  "Clear game"\n',
            '  smtty_print_action_row "[L] [10]" "Lock game"    "[U] [11]" "Unlock game" "[C] [12]" "Clear game"\n',
            "main action row 4",
        ),
        (
            '  smtty_print_action_row "[T] [5]"  "Diagnostics"  "[V] [7]"  "Version"     "[Q]"      "Quit"\n',
            '  smtty_print_action_row "[T] [13]" "Diagnostics"  "[V] [14]" "Version"     "[Q]"      "Quit"\n',
            "main action row 5",
        ),
    ],
)

smtty = replace_in_block(
    smtty,
    "interactive_profile_settings_editor() {",
    "interactive_profile_menu() {",
    [
        ('smtty_print_action_row "[H] [0]" "Hooks"', 'smtty_print_action_row "[H] [10]" "Hooks"', "new hooks label"),
        ('      h|0)\n', '      h|10)\n', "hooks numeric dispatch"),
    ],
)

smtty = replace_in_block(
    smtty,
    "interactive_profile_menu() {",
    "cleanup_old_session_artifacts() {",
    [
        ('      m|4)\n', '      m|8)\n', "MangoHud numeric dispatch"),
        ('      w|13)\n', '      w|9)\n', "Wayland numeric dispatch"),
        ('      e|14)\n', '      e|7)\n', "edit numeric dispatch"),
        ('      p|8)\n', '      p|1)\n', "play numeric dispatch"),
        ('      s|9)\n', '      s|4)\n', "profiles numeric dispatch"),
        ('      n|10)\n', '      n|5)\n', "new profile numeric dispatch"),
        ('      d|11)\n', '      d|6)\n', "delete profile numeric dispatch"),
        ('      g|1)\n', '      g|2)\n', "select game numeric dispatch"),
        ('Use [L] or [2] to persist it.', 'Use [L] or [10] to persist it.', "lock shortcut message"),
        ('      t|h|5)\n', '      t|h|13)\n', "diagnostics numeric dispatch"),
        ('      l|2)\n', '      l|10)\n', "lock numeric dispatch"),
        ('      u|3)\n', '      u|11)\n', "unlock numeric dispatch"),
        ('      c|6)\n', '      c|12)\n', "clear numeric dispatch"),
        ('      v|7)\n', '      v|14)\n', "version numeric dispatch"),
        ('      o|12)\n', '      o|3)\n', "launch options numeric dispatch"),
    ],
)

old_alias_checks = '''[[ "$actions" == *"[G] [1]"* ]] || fail "numeric alias 1 missing"
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
'''
new_alias_checks = '''[[ "$actions" == *"[P] [1]"* ]] || fail "numeric alias 1 missing"
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
compact_ui = replace_once(compact_ui, old_alias_checks, new_alias_checks, "compact UI alias assertions")

menu_assert_anchor = '[[ "$menu_block" != *\'echo "Options:"\'* ]] || fail "legacy tall Options list remains"\n'
menu_assertions = '''[[ "$menu_block" == *'p|1)'* ]] || fail "Play numeric dispatch is not 1"
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
if menu_assertions not in compact_ui:
    compact_ui = replace_once(compact_ui, menu_assert_anchor, menu_assert_anchor + menu_assertions, "menu dispatch assertion anchor")

compact_prompts = replace_once(
    compact_prompts,
    "expected_first='  [P] [8]   Play             [G] [1]   Select game       [O] [12]  Launch options'",
    "expected_first='  [P] [1]   Play             [G] [2]   Select game       [O] [3]   Launch options'",
    "compact prompt first row",
)
compact_prompts = replace_once(
    compact_prompts,
    "expected_edit='  [E] [14]  Edit profile     [M] [4]   MangoHud          [W] [13]  Wayland'",
    "expected_edit='  [E] [7]   Edit profile     [M] [8]   MangoHud          [W] [9]   Wayland'",
    "compact prompt edit row",
)
compact_prompts = replace_once(
    compact_prompts,
    "expected_quit='  [T] [5]   Diagnostics      [V] [7]   Version           [Q]       Quit'",
    "expected_quit='  [T] [13]  Diagnostics      [V] [14]  Version           [Q]       Quit'",
    "compact prompt final row",
)

profile_workflow = replace_once(
    profile_workflow,
    '[[ "$editor_block" == *\'smtty_print_action_row "[H] [0]" "Hooks" "[S]" "Save" "[Q]" "Cancel"\'* ]]',
    '[[ "$editor_block" == *\'smtty_print_action_row "[H] [10]" "Hooks" "[S]" "Save" "[Q]" "Cancel"\'* ]]',
    "profile workflow hooks label",
)
profile_workflow = replace_once(
    profile_workflow,
    '[[ "$editor_block" == *\'h|0)\'* ]]',
    '[[ "$editor_block" == *\'h|10)\'* ]]',
    "profile workflow hooks dispatch",
)

for forbidden in (
    '"[P] [8]"  "Play"',
    '"[H] [0]" "Hooks"',
    '      p|8)\n',
    '      h|0)\n',
):
    if forbidden in smtty:
        raise SystemExit(f"legacy numeric mapping remains: {forbidden!r}")

smtty_path.write_text(smtty, encoding="utf-8")
compact_ui_path.write_text(compact_ui, encoding="utf-8")
compact_prompts_path.write_text(compact_prompts, encoding="utf-8")
profile_workflow_path.write_text(profile_workflow, encoding="utf-8")
print("renumbered compact menus in visual order")
