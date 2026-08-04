#!/usr/bin/env python3
from pathlib import Path

path = Path("smtty")
text = path.read_text(encoding="utf-8")
original = text

replacements = {
    '    audio="switch On"\n': '    audio="On"\n',
    "    printf 'smtty %s\\n\\n' \"${SMTTY_VERSION#v}\"\n": "    printf 'smtty %s\\n\\n' \"$SMTTY_VERSION\"\n",
    '        echo "Enter 1-9, 0, S, or b."\n': '        echo "Choose 1-9, 0, S, or B."\n',
}

for old, new in replacements.items():
    if new in text:
        continue
    if text.count(old) != 1:
        raise SystemExit(f"expected one compact UI refinement target, found {text.count(old)}")
    text = text.replace(old, new, 1)

if text != original:
    path.write_text(text, encoding="utf-8")
    print("refined compact terminal UI")
else:
    print("compact terminal UI already refined")
