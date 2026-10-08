CRIMSON GLASS 1.0.0
Black, ruby red, glass and smooth motion for KDE Plasma 6

QUICK INSTALL
  1. Extract Crimson-Glass-1.0.0.zip.
  2. Open a terminal inside the extracted Crimson-Glass-1.0.0 folder.
  3. Run as your NORMAL desktop user:
       sh ./install.sh --all
  4. Log out and back in. Login and boot themes appear on the next login/boot.

The --all option installs the desktop, SDDM login and Plymouth boot theme.
It downloads prerequisites from your distribution's enabled repositories,
using sudo only for packages and system startup files. Review the normal
package manager transaction before accepting it. The installer never
adds third-party repositories, changes display manager, or reboots.

Desktop only (no login/boot changes):
  sh ./install.sh
Keep your existing panels and widgets while adopting the visual theme:
  sh ./install.sh --no-layout
Inspect the file checks and installation plan without applying it:
  sh ./install.sh --all --dry-run
If all prerequisites are already installed:
  sh ./install.sh --all --skip-deps
Only add a startup component:
  The main installer accepts --with-login and/or --with-boot along with
  the desktop. startup.py also offers separately auditable system steps:
    python3 startup.py --help

WHAT IS INCLUDED
  * The current corrected CrimsonGlass-Icons pack: 25,987 distinct icon
    names, red generic/special folders, 28 original ruby app artworks,
    Papirus foundations plus Tela and Breeze coverage. No macOS icon pack.
  * Charcoal/red Plasma shell theme, Aurorae traffic-light decoration,
    exact current color palette, original 4K ribbon wallpaper and cursors.
  * Kvantum themes for Qt5 and Qt6; Dolphin gets its own glass stylesheet
    with about 80% opaque background and fully legible foreground content.
  * GTK2/GTK3/GTK4 theme files, GTK4 per-user CSS/assets, matching Konsole.
  * Andromeda application launcher, File/Edit global menu across the top,
    system tray, pager and clock; a floating bottom dock that dodges windows.
  * Primary-screen desktop clock and crimson CPU, RAM, network and storage
    monitors, scaled to the destination screen. Storage resolves the local
    root disk when available, otherwise uses the system's aggregate.
  * Blur, subtle translucency, Magic Lamp, Overview and Show Desktop corners.
  * Original matching SDDM login, KSplash and native Plymouth boot screens.
  * Complete source artwork, license notices, dependency recipes, SHA-256
    file manifest, install/restore tools and component credits.

The ZIP contains the theme assets in assets.tar.xz to preserve 145,000+
internal icon aliases and high-DPI directory links. The installer extracts
this archive safely; do not drag its contents individually into your home.
Compiled operating-system packages are downloaded at installation time;
they are distribution/architecture specific rather than embedded binaries.

COMPATIBILITY AND DEPENDENCIES
  Required: an existing KDE Plasma 6 desktop, Python 3.10+, about 2 GB free
  space for a fresh install (allow more for backups of an existing pack),
  network access, a package manager and administrator access for packages.
  Tested visual source: CachyOS, Plasma 6.7.5, Qt 6.11.2, Kvantum 1.1.8.
  The installer also has native dependency recipes for Arch derivatives,
  Debian 13/Ubuntu releases with Plasma 6, and Fedora KDE. These distro
  recipes are checked against enabled package repositories before settings
  change; full live installations on those other distributions are untested.
  Plasma 5, GNOME, immutable image-based OS installs and other desktops are
  not supported by automatic dependency installation. Do not run as root.

  dependencies.py records every explicit prerequisite and distro alias:
  Kvantum Qt5/Qt6, Plasma integration Qt5/Qt6, Aurorae, Breeze fallbacks,
  Kirigami Addons, Qt5Compat, Qt SVG/tools, KDE GTK integration, monitor and
  widget packages, Dolphin/KIO previews, Konsole, Ark, Noto fonts and GTK
  menu-export modules. Qt/KDE libraries arrive transitively through the
  native package manager. SDDM/Plasma QML modules and Plymouth/two-step
  integration are added for the optional startup components.

  On Arch, keep the system fully updated using your usual update process
  first. This installer uses pacman -S --needed and avoids partial upgrades.
  On Debian/Ubuntu, standard KDE/universe packages must be enabled. Fedora's
  GTK menu module may be unavailable; KDE/Qt global menus still work and
  GTK apps that do not export menus keep their own controls.

LOGIN AND BOOT DETAILS
  --all requires SDDM and supported distribution initramfs tooling.
  The startup module validates Qt6/Plasma QML and Plymouth's native two-step
  plugin before activating either theme. It does not enable a different
  login manager or restart your current login session.

  Plymouth is integrated using limine-mkinitcpio/mkinitcpio on Arch,
  update-initramfs on Debian/Ubuntu, or dracut on Fedora. On a simple Arch
  HOOKS array, --with-boot may add only the missing plymouth hook after udev
  or systemd. Existing driver, encryption and kernel settings are preserved.
  Complex overrides are reported for manual resolution before any changes.

  Your active kernel command line must contain splash and must not disable
  Plymouth. The installer reports when splash is missing. Add it using
  your distribution's existing bootloader configuration procedure, keeping
  all existing arguments. The installer deliberately does not guess a
  bootloader or overwrite authored boot entries. Initramfs rebuilds may
  refresh generated hashes for the current kernels.

BACKUPS AND RESTORE
  Every install saves existing assets/configuration before replacing them:
    ~/.local/state/crimson-glass/backups/<timestamp>/
  Respecting XDG_STATE_HOME when configured. The exact path is printed.
  Reinstallation saves another snapshot; it recreates two panels/five
  desktop widgets, so it does not accumulate duplicate widgets.

  Restore the last desktop snapshot:
    sh ./restore.sh
  Restore desktop AND the linked login/boot snapshot:
    sh ./restore.sh --restore-system
  Pick an older snapshot using the path printed by that installation:
    sh ./restore.sh --backup /absolute/path/to/snapshot
  Restoring panels briefly stops/restarts the user's Plasma shell; open
  applications and the session remain. Then log out and back in for all
  application themes. If your shell cannot be stopped, log out first and
  restore from a text console with:
    sh ./restore.sh --offline

  Distribution packages are retained after restore. Startup backups live
  under /var/lib/crimson-glass/startup-backups. System restoration checks
  whether files changed since install and regenerates current initramfs
  images; it never restores old kernel/boot image copies. Inspect any
  reported conflict before using startup.py's explicit --force-restore.

PERSONALIZATION AND LIMITS
  The normal layout installation replaces existing panels and current
  primary-screen widgets. Use --no-layout to keep them. Existing input,
  mouse/touchpad settings, monitor arrangement, accounts, private shortcuts,
  browser choice, file history and hardware identifiers are not distributed.
  The dock uses KDE apps actually installed on the destination computer.

  Qt Quick/Kirigami uses the Plasma palette; Kvantum styles Qt Widgets.
  Traditional GTK menus need an application that exports a menu; client-side
  menus and some Electron/browser apps cannot be moved into the top bar.
  Libadwaita, Snap and Flatpak apps may isolate/override their own styles;
  sandbox theme integration depends on the application's runtime. KWin
  compositing and a working GPU driver are required for blur/transparency.
  Blue hues in photos/thumbnails and application brand artwork are not
  recolored; default folder icons and theme accents are crimson.

  You can tune the themes in System Settings and Kvantum Manager. Restore
  snapshots contain your local preferences; keep them private when sharing
  this ZIP. No original desktop screenshots or personal account images
  are part of the release. License details are in CREDITS.txt and licenses/.

VERIFICATION
  The installer checks manifest.json's SHA-256 hashes before dependency or
  desktop changes. The separate ZIP .sha256 file checks the download itself. From the
  download directory:
    sha256sum -c Crimson-Glass-1.0.0.zip.sha256
  The hashes detect damage; they are not a publisher signature.

  Release testing: isolated home install, second install, restores, config
  preservation, symlink round trip, malformed archive rejection, startup
  install/restore simulations for all three initramfs families, and repeated
  layout application with mocked Plasma at different screen sizes. Testing
  does not perform another live desktop install or reboot this computer.
