#!/usr/bin/env python3
from pathlib import Path

smtty_path = Path("smtty")
test_path = Path("tests/test-compact-ui.sh")
smtty = smtty_path.read_text(encoding="utf-8")
tests = test_path.read_text(encoding="utf-8")

old_actions = '''smtty_print_compact_actions() {
  echo "Actions"
  printf '  %-19s %-21s %s\\n' "[P] Play" "[G] Select game" "[O] Launch options"
  printf '  %-19s %-21s %s\\n' "[S] Profiles" "[E] Edit profile" "[M] MangoHud"
  printf '  %-19s %-21s %s\\n' "[W] Wayland" "[T] Diagnostics" "[A] More"
  echo "  [Q] Quit"
}

smtty_more_actions_menu() {
  echo
  echo "More actions"
  printf '  %-20s %-20s %s\\n' "[L] Lock game" "[U] Unlock game" "[C] Clear game"
  printf '  %-20s %-20s %s\\n' "[N] New profile" "[D] Delete profile" "[V] Version"
  echo "  [B] Back"

  local selected
  if ! read_key_or_number selected "Choose [L,U,C,N,D,V,B]: "; then
    return 1
  fi
  selected="${selected//[[:space:]]/}"
  selected="${selected,,}"

  case "$selected" in
    l|u|c|n|d|v)
      REPLY=$selected
      return 0
      ;;
    b|q|"")
      return 1
      ;;
    *)
      echo "Choose L, U, C, N, D, V, or B."
      return 1
      ;;
  esac
}
'''

new_actions = '''smtty_print_compact_actions() {
  echo "Actions"
  printf '  %-19s %-21s %s\\n' "[P] Play" "[G] Select game" "[O] Launch options"
  printf '  %-19s %-21s %s\\n' "[S] Profiles" "[N] New profile" "[D] Delete profile"
  printf '  %-19s %-21s %s\\n' "[E] Edit profile" "[M] MangoHud" "[W] Wayland"
  printf '  %-19s %-21s %s\\n' "[L] Lock game" "[U] Unlock game" "[C] Clear game"
  printf '  %-19s %-21s %s\\n' "[T] Diagnostics" "[V] Version" "[Q] Quit"
}
'''

if old_actions not in smtty:
    raise SystemExit("compact action block did not match")
smtty = smtty.replace(old_actions, new_actions, 1)

old_header = '''    printf 'smtty %s\\n\\n' "$SMTTY_VERSION"
    smtty_print_compact_summary 1 "$mh_state"
'''
new_header = '''    echo "Steam Machine TTY Wrapper"
    echo
    smtty_print_compact_summary 1 "$mh_state"
'''
if old_header not in smtty:
    raise SystemExit("main header did not match")
smtty = smtty.replace(old_header, new_header, 1)

old_prompt = '''    if ! read_key_or_number choice "Choose [P,G,O,S,E,M,W,T,A,Q]: "; then
'''
new_prompt = '''    if ! read_key_or_number choice "Choose: "; then
'''
if old_prompt not in smtty:
    raise SystemExit("main prompt did not match")
smtty = smtty.replace(old_prompt, new_prompt, 1)

old_more_dispatch = '''
    if [[ "$choice" == "a" ]]; then
      if ! smtty_more_actions_menu; then
        continue
      fi
      choice=$REPLY
    fi

'''
if old_more_dispatch not in smtty:
    raise SystemExit("More-menu dispatch did not match")
smtty = smtty.replace(old_more_dispatch, "\n", 1)

smtty = smtty.replace(
    '          echo "Selection is temporary. Use More > Lock game to persist it."\n',
    '          echo "Selection is temporary. Use [L] to persist it."\n',
    1,
)
smtty = smtty.replace(
    '        echo "Choose P, G, O, S, E, M, W, T, A, or Q."\n',
    '        echo "Choose a listed action."\n',
    1,
)

old_test_stub = '''# The More menu depends on this function, but layout tests never call it.
read_key_or_number() { return 1; }

'''
tests = tests.replace(old_test_stub, "", 1)

tests = tests.replace(
    '(( action_lines <= 5 )) || fail "actions are too tall: $action_lines lines"',
    '(( action_lines <= 6 )) || fail "actions are too tall: $action_lines lines"',
    1,
)
tests = tests.replace(
    '[[ "$actions" == *"[A] More"* ]] || fail "more action missing"\n',
    '''[[ "$actions" == *"[S] Profiles"* ]] || fail "profiles action missing"
[[ "$actions" == *"[N] New profile"* ]] || fail "new-profile action missing"
[[ "$actions" == *"[D] Delete profile"* ]] || fail "delete-profile action missing"
[[ "$actions" == *"[E] Edit profile"* ]] || fail "edit action missing"
[[ "$actions" == *"[M] MangoHud"* ]] || fail "MangoHud action missing"
[[ "$actions" == *"[W] Wayland"* ]] || fail "Wayland action missing"
[[ "$actions" == *"[L] Lock game"* ]] || fail "lock action missing"
[[ "$actions" == *"[U] Unlock game"* ]] || fail "unlock action missing"
[[ "$actions" == *"[C] Clear game"* ]] || fail "clear action missing"
[[ "$actions" == *"[T] Diagnostics"* ]] || fail "diagnostics action missing"
[[ "$actions" == *"[V] Version"* ]] || fail "version action missing"
[[ "$actions" == *"[Q] Quit"* ]] || fail "quit action missing"
[[ "$actions" != *"[A] More"* ]] || fail "More submenu action remains"
''',
    1,
)

tests = tests.replace(
    '[[ "$menu_block" == *"smtty_print_compact_actions"* ]] || fail "main menu does not use compact actions"\n',
    '''[[ "$menu_block" == *"smtty_print_compact_actions"* ]] || fail "main menu does not use compact actions"
[[ "$menu_block" == *'echo "Steam Machine TTY Wrapper"'* ]] || fail "product title missing"
[[ "$menu_block" != *"smtty_more_actions_menu"* ]] || fail "More submenu dispatch remains"
[[ "$menu_block" != *"smtty %s"* ]] || fail "version banner remains at top"
''',
    1,
)

smtty_path.write_text(smtty, encoding="utf-8")
test_path.write_text(tests, encoding="utf-8")
print("revised compact main menu")
