#!/usr/bin/env python3
from pathlib import Path

smtty_path = Path("smtty")
test_path = Path("tests/test-compact-ui.sh")
smtty = smtty_path.read_text(encoding="utf-8")
tests = test_path.read_text(encoding="utf-8")

old_code = '      game_name+=" · Locked"\n'
new_code = '      game_name+=" (locked)"\n'
if old_code not in smtty:
    raise SystemExit("locked game label did not match")
smtty = smtty.replace(old_code, new_code, 1)

tests = tests.replace(
    'Game:    Counter-Strike 2 · Locked',
    'Game:    Counter-Strike 2 (locked)',
    1,
)

unlocked_check = '''
rm -f "$lock_file"
unlocked_summary=$(smtty_print_compact_summary 1 "Off")
[[ "$unlocked_summary" == *"Game:    Counter-Strike 2"* ]] || fail "unlocked game name missing"
[[ "$unlocked_summary" != *"(locked)"* ]] || fail "unlocked game incorrectly marked locked"
'''
anchor = '[[ "$summary" == *"Hooks    None"* ]] || fail "hook summary missing"\n'
if unlocked_check.strip() not in tests:
    if anchor not in tests:
        raise SystemExit("unlocked test insertion anchor missing")
    tests = tests.replace(anchor, anchor + unlocked_check, 1)

smtty_path.write_text(smtty, encoding="utf-8")
test_path.write_text(tests, encoding="utf-8")
print("refined compact game lock label")
