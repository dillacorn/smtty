#!/usr/bin/env python3
from pathlib import Path

smtty_path = Path("smtty")
test_path = Path("tests/test-compact-ui.sh")
smtty = smtty_path.read_text(encoding="utf-8")
tests = test_path.read_text(encoding="utf-8")

replacements = {
    "[P/8] Play": "[P] [8] Play",
    "[G/1] Select game": "[G] [1] Select game",
    "[O/12] Launch options": "[O] [12] Launch options",
    "[S/9] Profiles": "[S] [9] Profiles",
    "[N/10] New profile": "[N] [10] New profile",
    "[D/11] Delete profile": "[D] [11] Delete profile",
    "[E/14] Edit profile": "[E] [14] Edit profile",
    "[M/4] MangoHud": "[M] [4] MangoHud",
    "[W/13] Wayland": "[W] [13] Wayland",
    "[L/2] Lock game": "[L] [2] Lock game",
    "[U/3] Unlock game": "[U] [3] Unlock game",
    "[C/6] Clear game": "[C] [6] Clear game",
    "[T/5] Diagnostics": "[T] [5] Diagnostics",
    "[V/7] Version": "[V] [7] Version",
    "Use [L/2] to persist it.": "Use [L] or [2] to persist it.",
}

for old, new in replacements.items():
    if old in smtty:
        smtty = smtty.replace(old, new)
    if old in tests:
        tests = tests.replace(old, new)

number_aliases = {
    '[G/1]': '[G] [1]',
    '[L/2]': '[L] [2]',
    '[U/3]': '[U] [3]',
    '[M/4]': '[M] [4]',
    '[T/5]': '[T] [5]',
    '[C/6]': '[C] [6]',
    '[V/7]': '[V] [7]',
    '[P/8]': '[P] [8]',
    '[S/9]': '[S] [9]',
    '[N/10]': '[N] [10]',
    '[D/11]': '[D] [11]',
    '[O/12]': '[O] [12]',
    '[W/13]': '[W] [13]',
    '[E/14]': '[E] [14]',
}
for old, new in number_aliases.items():
    tests = tests.replace(old, new)

if "[P/8]" in smtty or "[P/8]" in tests:
    raise SystemExit("slash-style menu aliases remain")
if "[P] [8] Play" not in smtty:
    raise SystemExit("dual-bracket Play label was not applied")

smtty_path.write_text(smtty, encoding="utf-8")
test_path.write_text(tests, encoding="utf-8")
print("converted compact menu aliases to dual brackets")
