# Crimson Glass

A black and ruby-red glass theme for **KDE Plasma 6**: translucent windows, smooth animations, a complete crimson icon pack, and a matching desktop, login, splash, and boot experience.

[Browse the screenshot gallery](screenshots/README.md) — 14 desktop/component captures and previews, with captions.

![Crimson Glass desktop and monitoring widgets](screenshots/desktop.png)

*Desktop capture from the theme build. See the gallery for the corrected icon pack and component details.*

**[Download the complete installer ZIP](https://github.com/SirFork1988/Crimson-Glass/releases/latest)**

The release ZIP contains all theme assets, source artwork, licenses, and installation files. Download `Crimson-Glass-1.1.0.zip` from the release assets. GitHub’s automatic **Source code** archives contain this repository’s reference code and documentation, without the theme asset bundle.

## Install

Extract the installer ZIP, open a terminal inside its `Crimson-Glass-1.1.0` folder, and run as your **normal desktop user**:

```sh
sh ./install.sh --all
```

The installer downloads native prerequisites from your distro’s enabled repositories, backs up existing theme files and preferences, and applies the desktop plus the optional SDDM login and Plymouth boot themes. Log out and back in afterward. Login and boot changes take effect on the next login/boot.

For the desktop alone:

```sh
sh ./install.sh
```

To retain your existing panels and widgets:

```sh
sh ./install.sh --no-layout
```

To check the plan before making changes:

```sh
sh ./install.sh --all --dry-run
```

## Screen changes and game transparency (1.1.0)

The user-session helper automatically realigns the five Crimson Glass monitoring widgets after a resolution, display scaling, or monitor change has settled for about 9 seconds. It uses logical desktop dimensions, tracks the managed widgets, preserves other widgets and panel settings, and saves five layout backups. Plasma currently ignores live geometry assignments on some versions, so the helper briefly restarts the desktop shell when it needs to apply a new layout; open applications keep running. It does not reset manual widget placement on ordinary logins. Displays below 800 × 816 logical pixels are left alone.

The game opacity policy replaces the theme's broad KWin translucency effect. Fullscreen windows, Steam game classes, Windows `.exe`/Proton windows, common launcher/emulator classes, and processes carrying Steam, Lutris, Heroic, or an explicit game flag remain fully opaque even when inactive or moving. Standard application windows keep subtle inactive/move transparency. Application-rendered alpha, overlays, and unrelated third-party effects are outside this policy.

For an unusual native windowed game, open its window menu with **Alt+F3** and choose **Crimson Glass: keep this window opaque**. This remembers the window class for future sessions. Alternatively, launch it with `CRIMSON_GLASS_GAME=1 your-game`. The helper reads only local same-user process information for classification; it does not transmit or log environment values.

Use `--no-auto-align` or `--no-game-opacity` to opt out during installation. `--no-layout` keeps your current panels/widgets and leaves automatic alignment disabled. Runtime preferences and remembered game classes live in `~/.config/crimson-glass-runtime.json`; restart the helper after editing this file. To clear a remembered class, remove it from `opaque_classes`. Runtime logs and the five most recent alignment backups live in `~/.local/state/crimson-glass/`.

An existing theme-owned `CrimsonGlass-Transparency` catch-all KWin rule is migrated away so it cannot force games transparent. Other window rules are retained. Restoration stops the helper, unloads the game policy, and restores the backed-up runtime files and preferences. Choose the upgrade's original backup to revert both features.

## What you get

- **CrimsonGlass-Icons:** 25,987 distinct icon names, corrected red generic and special folders, and 28 original ruby application artworks. Papirus foundations with Tela and Breeze coverage; no macOS icon pack.
- **Plasma:** charcoal/red shell, original ribbon wallpaper, traffic-light window controls, Andromeda application launcher, top-bar File/Edit global menus, floating dock, and matching cursors.
- **Application themes:** Kvantum styles for Qt5/Qt6, a separate glass style for Dolphin, GTK2/GTK3/GTK4 assets, and matching Konsole colors.
- **System monitoring:** clock, CPU, memory, network, and storage widgets that adapt to the destination screen and computer.
- **Motion and glass:** blur, subtle translucency, Magic Lamp, Overview, and Show Desktop corners.
- **Startup screens:** matching SDDM login, KSplash, and native Plymouth boot themes.
- **Recovery:** backups, restore tools, SHA-256 integrity checks, editable artwork, and upstream license notices.

The package removes private paths, account images, hardware identifiers, and device-specific settings. It preserves existing mouse/touchpad preferences and monitor arrangement. The normal layout option replaces panels and primary-screen widgets; use `--no-layout` to keep them.

## Compatibility

An existing **KDE Plasma 6** desktop and Python 3.10+ are required. Allow approximately 2 GB free space for a fresh install, and more when backing up existing theme assets.

The visual source is CachyOS with Plasma 6.7.5, Qt 6.11.2, and Kvantum 1.1.8. Dependency recipes cover Arch/CachyOS derivatives, Debian 13/Ubuntu releases with Plasma 6, and Fedora KDE. They check enabled repositories before changing desktop settings. **Live installations on those other distributions remain untested.** Plasma 5, GNOME, and immutable image-based systems are outside automatic installation support.

`--all` requires SDDM and supported initramfs tooling. The installer does not switch display managers or reboot. Plymouth needs `splash` in the active kernel command line; the installer reports when it is missing. Follow your distro’s existing bootloader procedure while retaining existing arguments. Complex or UKI-only boot configurations may require manual integration. See [the full guide](README.txt).

Qt Quick/Kirigami follows the Plasma palette; Kvantum styles Qt Widgets. Global menus require applications that export a menu. Libadwaita, Electron, Flatpak, and Snap applications can retain or isolate their own styles. Blur requires working KWin compositing and graphics drivers.

## Restore

From the extracted release folder:

```sh
sh ./restore.sh
```

To also restore the startup themes linked to that installation:

```sh
sh ./restore.sh --restore-system
```

Backups live under `~/.local/state/crimson-glass/backups/` (respecting `XDG_STATE_HOME`); the installer prints the exact path. System startup snapshots live under `/var/lib/crimson-glass/startup-backups/`. Restoration keeps distro packages and regenerates current initramfs images rather than copying old kernel/boot images. Keep your local backups private.

## Verify your download

Download the release’s ZIP and `.sha256` file into the same directory, then run:

```sh
sha256sum -c Crimson-Glass-1.1.0.zip.sha256
```

The installer also verifies the package’s internal file manifest. Checksums detect corruption; they are not a publisher signature.

## Validation and source

Fresh installation, reinstallation, and restoration passed in an isolated home, including all 145,098 icon links, preserved file permissions, and unrelated preferences. Additional tests cover hostile archives and links, startup recovery, multiple screen sizes, launcher registration, and sensor discovery. See [VALIDATION.txt](VALIDATION.txt) for the test scope.

This repository provides the installer reference code, dependency recipes, documentation, and notices. The complete editable theme assets and cursor/boot artwork rebuild sources are included in the release ZIP, including its `assets.tar.xz` bundle. Source rebuild tools can require Pillow; the installer uses Python’s standard library and the session helper uses distro-provided D-Bus/GObject bindings.

## Credits and licenses

Crimson Glass combines original artwork with work from Papirus, Tela, KDE Breeze, WhiteSur KDE/GTK, Qogir, and Andromeda Launcher. Each component retains its own license. The portable installer is MIT; the package as a whole has multiple licenses. See [CREDITS.txt](CREDITS.txt) and [licenses/](licenses/). Public application names and logos remain their owners’ trademarks.

## Feedback

Please include your distribution, Plasma version, installation options, and a redacted error message when reporting an issue. Do not upload personal backups, credentials, account screenshots, or private system configuration.

## KDE Store packages

Native companion packages and their fully extracted, credited source are in [store/](store/). [Store listing copy](store/LISTINGS.md) documents licenses and compatibility. The native Global Theme uses KDE appearance defaults and an optional desktop layout; automatic widget realignment and game opacity still require the full installer.

### KDE Store components

Native component downloads are now published under [SirFork1988](https://www.opendesktop.org/u/sirfork1988/products). See the [component list](store/PUBLISHING.md) for direct links. The native global theme complements the full installer; the installer provides automatic widget realignment and game-opacity helpers.
