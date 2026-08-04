#!/usr/bin/env python3
from pathlib import Path

smtty_path = Path("smtty")
test_path = Path("tests/test-compact-ui.sh")
smtty = smtty_path.read_text(encoding="utf-8")
tests = test_path.read_text(encoding="utf-8")

old_actions = '''smtty_print_compact_actions() {
  echo "Actions"
  printf '  %-19s %-21s %s\\n' "[P] Play" "[G] Select game" "[O] Launch options"
  printf '  %-19s %-21s %s\\n' "[S] Profiles" "[N] New profile" "[D] Delete profile"
  printf '  %-19s %-21s %s\\n' "[E] Edit profile" "[M] MangoHud" "[W] Wayland"
  printf '  %-19s %-21s %s\\n' "[L] Lock game" "[U] Unlock game" "[C] Clear game"
  printf '  %-19s %-21s %s\\n' "[T] Diagnostics" "[V] Version" "[Q] Quit"
}
'''

new_actions = '''smtty_print_compact_actions() {
  echo "Actions"
  printf '  %-23s %-23s %s\\n' "[P/8] Play" "[G/1] Select game" "[O/12] Launch options"
  printf '  %-23s %-23s %s\\n' "[S/9] Profiles" "[N/10] New profile" "[D/11] Delete profile"
  printf '  %-23s %-23s %s\\n' "[E/14] Edit profile" "[M/4] MangoHud" "[W/13] Wayland"
  printf '  %-23s %-23s %s\\n' "[L/2] Lock game" "[U/3] Unlock game" "[C/6] Clear game"
  printf '  %-23s %-23s %s\\n' "[T/5] Diagnostics" "[V/7] Version" "[Q] Quit"
}
'''

if old_actions not in smtty:
    raise SystemExit("current compact action block did not match")
smtty = smtty.replace(old_actions, new_actions, 1)
smtty = smtty.replace(
    '          echo "Selection is temporary. Use [L] to persist it."\n',
    '          echo "Selection is temporary. Use [L/2] to persist it."\n',
    1,
)

label_replacements = {
    '"[P] Play"': '"[P/8] Play"',
    '"[G] Select game"': '"[G/1] Select game"',
    '"[O] Launch options"': '"[O/12] Launch options"',
    '"[S] Profiles"': '"[S/9] Profiles"',
    '"[N] New profile"': '"[N/10] New profile"',
    '"[D] Delete profile"': '"[D/11] Delete profile"',
    '"[E] Edit profile"': '"[E/14] Edit profile"',
    '"[M] MangoHud"': '"[M/4] MangoHud"',
    '"[W] Wayland"': '"[W/13] Wayland"',
    '"[L] Lock game"': '"[L/2] Lock game"',
    '"[U] Unlock game"': '"[U/3] Unlock game"',
    '"[C] Clear game"': '"[C/6] Clear game"',
    '"[T] Diagnostics"': '"[T/5] Diagnostics"',
    '"[V] Version"': '"[V/7] Version"',
}
for old, new in label_replacements.items():
    if old not in tests:
        raise SystemExit(f"test label did not match: {old}")
    tests = tests.replace(old, new, 1)

number_checks = '''
[[ "$actions" == *"[G/1]"* ]] || fail "numeric alias 1 missing"
[[ "$actions" == *"[L/2]"* ]] || fail "numeric alias 2 missing"
[[ "$actions" == *"[U/3]"* ]] || fail "numeric alias 3 missing"
[[ "$actions" == *"[M/4]"* ]] || fail "numeric alias 4 missing"
[[ "$actions" == *"[T/5]"* ]] || fail "numeric alias 5 missing"
[[ "$actions" == *"[C/6]"* ]] || fail "numeric alias 6 missing"
[[ "$actions" == *"[V/7]"* ]] || fail "numeric alias 7 missing"
[[ "$actions" == *"[P/8]"* ]] || fail "numeric alias 8 missing"
[[ "$actions" == *"[S/9]"* ]] || fail "numeric alias 9 missing"
[[ "$actions" == *"[N/10]"* ]] || fail "numeric alias 10 missing"
[[ "$actions" == *"[D/11]"* ]] || fail "numeric alias 11 missing"
[[ "$actions" == *"[O/12]"* ]] || fail "numeric alias 12 missing"
[[ "$actions" == *"[W/13]"* ]] || fail "numeric alias 13 missing"
[[ "$actions" == *"[E/14]"* ]] || fail "numeric alias 14 missing"
'''
anchor = '[[ "$actions" != *"[A] More"* ]] || fail "More submenu action remains"\n'
if number_checks.strip() not in tests:
    if anchor not in tests:
        raise SystemExit("number test insertion anchor missing")
    tests = tests.replace(anchor, anchor + number_checks, 1)

smtty_path.write_text(smtty, encoding="utf-8")
test_path.write_text(tests, encoding="utf-8")
print("added visible compact-menu number aliases")
