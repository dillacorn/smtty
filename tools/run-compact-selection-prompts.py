#!/usr/bin/env python3
from pathlib import Path
import runpy
import tempfile

source = Path("tools/compact-selection-prompts.py")
text = source.read_text(encoding="utf-8")
marker = '"LD_PRELOAD confirmation",\n)\n'
marker_end = text.find(marker)
if marker_end < 0:
    raise SystemExit("LD_PRELOAD confirmation marker not found")
block_start = text.rfind("replace_once(\n", 0, marker_end)
if block_start < 0:
    raise SystemExit("LD_PRELOAD confirmation block start not found")
block_end = marker_end + len(marker)
text = text[:block_start] + text[block_end:]

with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tmp:
    tmp.write(text)
    tmp_path = Path(tmp.name)

try:
    runpy.run_path(str(tmp_path), run_name="__main__")
finally:
    tmp_path.unlink(missing_ok=True)

smtty_path = Path("smtty")
smtty = smtty_path.read_text(encoding="utf-8")
old_lines = [
    '  echo "LD_PRELOAD mode set to: $LD_PRELOAD_MODE"\n',
    '  echo "  inherit = pass through existing LD_PRELOAD"\n',
    '  echo "  clear   = export LD_PRELOAD=\\"\\" before gamescope"\n',
]
for line in old_lines:
    if line not in smtty:
        raise SystemExit(f"LD_PRELOAD line not found: {line.strip()}")

smtty = smtty.replace(old_lines[0], '  echo "LD_PRELOAD: ${LD_PRELOAD_MODE^}"\n', 1)
smtty = smtty.replace(old_lines[1], "", 1)
smtty = smtty.replace(old_lines[2], "", 1)
smtty_path.write_text(smtty, encoding="utf-8")

ui_test_path = Path("tests/test-compact-ui.sh")
ui_test = ui_test_path.read_text(encoding="utf-8")
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
    needle = f'[[ "$actions" == *"{old}"* ]]'
    replacement = f'[[ "$actions" == *"{new}"* ]]'
    if needle not in ui_test:
        raise SystemExit(f"compact UI assertion not found: {old}")
    ui_test = ui_test.replace(needle, replacement, 1)
ui_test_path.write_text(ui_test, encoding="utf-8")

print("applied compact prompt pass with aligned-action test updates")
