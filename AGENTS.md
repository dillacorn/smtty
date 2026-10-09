# Repository instructions for smtty

Applies to this repository and its scripts.

## Project and behavior

- `smtty` is a Bash Steam Big Picture/Gamescope TTY launcher with configurable display, resolution/stretch, and persistent user profiles in `~/.config/smtty`.
- Preserve its single-file launcher structure, its input/menu workflow, profiles, Steam/Gamescope selection, and safe handling of native versus stretched resolution. Check the current implementation before editing options or Gamescope arguments.
- `smtty-installer` provides per-user manual installation/uninstallation (normally `~/.local/bin`); `smtty-update` updates a manual installation from the repository's current `main`. Do not assume manual install, GitHub Release, and AUR users receive changes identically.
- The AUR `smtty` package is a separate distribution channel. Do not publish/update the AUR package simply because a GitHub release was approved.

## Merge and release authorization

Operate autonomously within the user's approved scope; do not add needless approval checkpoints.

- Implementation, investigation, fixes, tests, branches, and ordinary review PRs are not implicit authorization to merge, tag, or publish.
- A clear request to merge, commit/apply directly to `main`, tag, or publish authorizes the named operation for the specified work. An approved release includes its necessary scoped merge unless the user specifies a different target or restriction; do not ask for the same approval twice.
- An authorized but **unfinished** merge/release remains authorized through related small fixes, adjustments, tests, and interruptions. If the user pauses the release to correct a defect, an unambiguous "good to go", "working, continue", "looks good", or equivalent can resume the **same previously approved** operation. A pause ("wait"/"hold off") must be respected until the user signals continuation.
- The approval is **consumed when that operation finishes**. After a release has been published, fixing another issue or hearing "perfect"/"that works" does not authorize a follow-up merge or release. A new release requires a new authorization, even for a fix to the previous one.
- Stop and clarify when authorization is genuinely unclear, explicitly withdrawn, or when the scope, release target, or version materially changes. Do not invent an approval merely because CI passed, a prior release happened, or publishing would be convenient.
- A user can expressly approve releasing without manual runtime testing. Run reasonable available static/CI checks and report what was actually validated; do not misrepresent missing runtime testing or ignore significant failing checks.
- Preparing release notes, identifying a proposed version, writing code, and opening a feature PR are not themselves publication. Creating or triggering release-publishing workflows, one-use GitHub Actions release bridges, Git tags, Releases, uploads, or other publication requires an active approval for that specific release.
- Preserve any stricter project-specific permissions for deployments, package publication, destructive changes, and external infrastructure. A GitHub Release authorization does not inherently approve deployment, package publication, or replacing production data.

## Validation and delivery

- For Bash changes, run `bash -n smtty smtty-installer smtty-update` and relevant `tests/test-*.sh` checks when available; run ShellCheck when available. Do not imply CI covers a real DRM/Gamescope/Steam launch.
- Confirm the current latest release, its existing tag format, `main` HEAD, and the exact intended release contents before publishing. Do not assume a new semantic version scheme from other repositories.
- Preserve per-user settings and avoid deleting user profiles or changing persistent state outside the explicit task.
