# smtty

A minimal TTY "Steam Machine" launcher that runs Steam Big Picture inside gamescope on a chosen monitor, with configurable internal resolution (including 4:3 / 16:10 stretch) and saved per-user settings.

# **IMPORTANT:**

- **Steam cannot be running in any other session or smtty will fail.**

- **Make sure “Enable GPU accelerated rendering in web views” is enabled in Steam, or Steam notifications can cover the entire screen with a black image when running under gamescope.**

#### Steam Big Picture overlay cursor quirk (gamescope)

- On my setup the game only consistently re-grabs **raw mouse input** if the mouse is **moving while I close the Steam Big Picture overlay**.  
- If I close the overlay with the mouse perfectly still, the game often fails to re-grab the cursor and the **camera or aim can feel stuck or pinned to an edge**.  
- In other words, the current **dumb workaround** is to **jiggle the mouse while opening and closing Steam Big Picture** so the game can re-grab the cursor.

# **Demonstration Video**

<img src="smtty_yt_image.png" alt="smtty demonstration thumbnail" width="420">

Watch the demonstration video:  
https://www.youtube.com/watch?v=r8dZZAY5GDE

## Hyprland:

#### Learn about what I did in [Hyprland](https://github.com/hyprwm/Hyprland) before using smtty+gamescope -> [Steam_Launch_Options_Wayland_Hyprland](https://github.com/dillacorn/awtarchy/blob/main/extra_notes/Steam_Launch_Options_Wayland_Hyprland.md)
