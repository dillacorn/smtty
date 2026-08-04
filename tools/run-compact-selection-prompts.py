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
print("applied compact prompt pass with LD_PRELOAD fix")
