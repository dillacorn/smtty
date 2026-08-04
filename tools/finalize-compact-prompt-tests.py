#!/usr/bin/env python3
from pathlib import Path

path = Path("tests/test-compact-ui.sh")
text = path.read_text(encoding="utf-8")
labels = {
    "[P] [8] Play": "Play",
    "[G] [1] Select game": "Select game",
    "[O] [12] Launch options": "Launch options",
    "[S] [9] Profiles": "Profiles",
    "[N] [10] New profile": "New profile",
    "[D] [11] Delete profile": "Delete profile",
    "[E] [14] Edit profile": "Edit profile",
    "[M] [4] MangoHud": "MangoHud",
    "[W] [13] Wayland": "Wayland",
    "[L] [2] Lock game": "Lock game",
    "[U] [3] Unlock game": "Unlock game",
    "[C] [6] Clear game": "Clear game",
    "[T] [5] Diagnostics": "Diagnostics",
    "[V] [7] Version": "Version",
    "[Q] Quit": "Quit",
}
for old, new in labels.items():
    old_assertion = f'[[ "$actions" == *"{old}"* ]]'
    new_assertion = f'[[ "$actions" == *"{new}"* ]]'
    if old_assertion in text:
        text = text.replace(old_assertion, new_assertion, 1)
    elif new_assertion not in text:
        raise SystemExit(f"assertion not found: {old}")

path.write_text(text, encoding="utf-8")
print("finalized compact UI assertions")
