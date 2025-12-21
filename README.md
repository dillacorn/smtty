# smtty

A minimal TTY "Steam Machine" launcher that runs Steam Big Picture inside gamescope on a chosen monitor, with configurable internal resolution (including 4:3 / 16:10 stretch) and saved per-user settings.

## Discussions and testers wanted
I’m actively looking for testers, especially on hardware different from mine.  
Use Discussions for hardware-specific quirks, tuning, and “is this a bug or my setup?” debugging.

Start here: [Welcome to "smtty" Discussions](https://github.com/dillacorn/smtty/discussions/7)

# **IMPORTANT:**

- **Steam cannot be running in any other session or smtty will fail.**

- **Make sure “Enable GPU accelerated rendering in web views” is enabled in Steam, or Steam notifications can cover the entire screen with a black image when running under gamescope.**

I made an issue on this https://github.com/ValveSoftware/gamescope/issues/2042

#### Overlay limitations

- When running gamescope, clipboard integration with the desktop session is one-way: you can copy from the gamescope session to the desktop, but you cannot copy from the desktop into the gamescope session (no desktop → gamescope paste).
- For Steam messaging, use a browser on your normal desktop session and open:  
  <https://steamcommunity.com/chat>
- For convenience, you can create a dedicated Steam Chat launcher. Example `.desktop` file (Firefox profile) in my awtarchy repo:  
  [`firefox-steam-chat.desktop`](https://github.com/dillacorn/awtarchy/blob/main/local/share/applications/firefox-steam-chat.desktop)

# **Demonstration Video**

<img src="smtty_yt_image.png" alt="smtty demonstration thumbnail" width="420">

Watch the demonstration video: (already outdated...lol)    
https://www.youtube.com/watch?v=r8dZZAY5GDE

## Hyprland:

#### Learn about what I did in [Hyprland](https://github.com/hyprwm/Hyprland) before using smtty+gamescope -> [Steam_Launch_Options_Wayland_Hyprland](https://github.com/dillacorn/awtarchy/blob/main/extra_notes/Steam_Launch_Options_Wayland_Hyprland.md)
