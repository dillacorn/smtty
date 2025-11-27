# smtty

A minimal TTY "Steam Machine" launcher that runs Steam Big Picture inside gamescope on a chosen monitor, with configurable internal resolution (including 4:3 / 16:10 stretch) and saved per-user settings.

# **IMPORTANT:**

- **Steam cannot be running in any other session or smtty will fail.**

- **Make sure “Enable GPU accelerated rendering in web views” is enabled in Steam, or Steam notifications can cover the entire screen with a black image when running under gamescope.**

- **Some games do not like `--force-grab-cursor`; test it per game and per session (DE/WM vs TTY) if you hit cursor or input issues.**

- **If your camera or cursor gets stuck at the screen edge, briefly open then close Steam Big Picture over the game or pause/unpause; if it keeps happening, try `--force-grab-cursor` as a last resort.**

#### Learn about what I did in [Hyprland](https://github.com/hyprwm/Hyprland) before using smtty+gamescope -> [Steam_Launch_Options_Wayland_Hyprland](https://github.com/dillacorn/awtarchy/blob/main/extra_notes/Steam_Launch_Options_Wayland_Hyprland.md)
