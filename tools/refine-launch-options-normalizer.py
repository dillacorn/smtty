#!/usr/bin/env python3
from pathlib import Path

path = Path("smtty")
text = path.read_text(encoding="utf-8")
original = text

replacements = [('  local ch next quote token\n', '  local ch next quote token\n  local after_command=0\n'), ('          \';\'|\'&\'|\'|\'|\'<\'|\'>\'|\'(\'|\')\'|\'`\')\n            SMTTY_LAUNCH_NORMALIZE_ERROR="Unquoted shell control character \'$ch\' is too ambiguous to normalize safely."\n            return 1\n            ;;\n', '          \';\'|\'&\'|\'|\'|\'<\'|\'>\'|\'(\'|\')\'|\'`\')\n            if (( after_command )); then\n              token+="$ch"\n              i=$((i + 1))\n            else\n              SMTTY_LAUNCH_NORMALIZE_ERROR="Unquoted shell control character \'$ch\' is too ambiguous to normalize safely."\n              return 1\n            fi\n            ;;\n'), ('    SMTTY_LAUNCH_TOKENS+=("$token")\n  done\n', '    SMTTY_LAUNCH_TOKENS+=("$token")\n    if [[ "$token" == "%command%" ]]; then\n      after_command=1\n    fi\n  done\n'), ('  local extracted=0\n', '  local extracted=0\n  local preserve_env_tail=0\n'), ('      if [[ "$token" == "gamescope" ]]; then\n        SMTTY_LAUNCH_NORMALIZE_ERROR="The pasted options already contain gamescope. Paste the original game options instead."\n        return 1\n      fi\n\n      if [[ "$token" == "env" ]] && (( i + 1 < count )); then\n', '      if [[ "$token" == "gamescope" || "$token" == */gamescope ]]; then\n        SMTTY_LAUNCH_NORMALIZE_ERROR="The pasted options already contain gamescope. Paste the original game options instead."\n        return 1\n      fi\n\n      if (( preserve_env_tail )); then\n        command_tokens+=("$token")\n        i=$((i + 1))\n        continue\n      fi\n\n      if [[ "$token" == "env" ]] && (( i + 1 < count )); then\n'), ('        if (( env_found )); then\n          if (( j < count )) && [[ "${SMTTY_LAUNCH_TOKENS[j]}" == "--" ]]; then\n            j=$((j + 1))\n          fi\n          i=$j\n          continue\n        fi\n      fi\n\n      if [[ "$token" =~ ^[A-Za-z_][A-Za-z0-9_]*= ]]; then\n', '        if (( env_found )); then\n          if (( j < count )) && [[ "${SMTTY_LAUNCH_TOKENS[j]}" == "--" ]]; then\n            j=$((j + 1))\n          fi\n          i=$j\n          continue\n        fi\n\n        preserve_env_tail=1\n        command_tokens+=("$token")\n        i=$((i + 1))\n        continue\n      fi\n\n      if [[ "$token" =~ ^[A-Za-z_][A-Za-z0-9_]*= ]]; then\n')]

for old, new in replacements:
    if new in text:
        continue
    if text.count(old) != 1:
        raise SystemExit(f"expected one refinement target, found {text.count(old)}")
    text = text.replace(old, new, 1)

if text != original:
    path.write_text(text, encoding="utf-8")
    print("refined launch-option normalizer")
else:
    print("launch-option normalizer already refined")
