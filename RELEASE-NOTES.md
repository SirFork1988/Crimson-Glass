Crimson Glass 1.1.0 adds automatic widget realignment and opaque game windows.

- Monitoring widgets follow resolution, scaling, and monitor changes after the display settles. Only the five managed widgets move. A brief Plasma-shell restart applies positions; open applications stay running.
- Steam/Proton, detected non-Steam games, common emulators/launchers, and fullscreen windows remain opaque. Normal application windows retain subtle transparency.
- Alt+F3 → **Crimson Glass: keep this window opaque** remembers unusual windowed game classes. `CRIMSON_GLASS_GAME=1` is also supported.
- New native prerequisites: Python D-Bus and GObject bindings. The installer downloads these through distro repositories. Both features have opt-out flags and are included in backups/restoration.

Download **Crimson-Glass-1.1.0.zip** and its checksum, extract it, and run `sh ./install.sh --all` as your desktop user, or omit `--all` for desktop only. To preserve existing panels, use `--no-layout` (automatic alignment stays disabled).

Visual assets are unchanged from 1.0.0. Application-owned alpha and third-party effects can still render transparency. Cross-distro live installations remain untested; see VALIDATION.txt for test scope.
