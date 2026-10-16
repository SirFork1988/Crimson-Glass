Crimson Glass 1.1.1 repairs SDDM after upgrading to KDE Plasma 6.8.

- Fixes `Main.qml:366: VirtualKeyboardLoader is not a type`, caused by removal of the shared Breeze loader in Plasma 6.8.
- Uses `org.kde.plasma.workspace.keyboardlayout.KWinVirtualKeyboard`, retaining a compatibility path for the earlier API. The on-screen keyboard button appears only when a backend is available.
- The native SDDM archive and full installer both contain the repaired QML. All other bundled visual assets are preserved.
- Adds a real SDDM test-mode regression that detects fallback to the emergency theme, plus packaging coverage for the login overlay and preserved icon aliases.

**Existing installation: repair only login.** Extract `Crimson-Glass-1.1.1.zip`, open a terminal in its folder and run:

```sh
sudo python3 startup.py install --assets ./store/components --sddm
```

This creates a startup backup and installs/selects Crimson Glass without restarting SDDM or rebooting. You do not need to reapply your desktop or panels. The native `Crimson-Glass-SDDM-1.1.1.tar.gz` can also be installed through KDE's SDDM settings. Verify each download against its adjacent `.sha256` file.

Tested: theme instantiation on CachyOS with Plasma 6.8.0, Qt 6.12.0, SDDM 0.21.0; repository tests and release packaging checks. Older Plasma and other distributions are not live-tested for this patch. Test-mode loading does not exercise real PAM authentication or a reboot.

---

Crimson Glass 1.1.0 adds automatic widget realignment and opaque game windows.

- Monitoring widgets follow resolution, scaling, and monitor changes after the display settles. Only the five managed widgets move. A brief Plasma-shell restart applies positions; open applications stay running.
- Steam/Proton, detected non-Steam games, common emulators/launchers, and fullscreen windows remain opaque. Normal application windows retain subtle transparency.
- Alt+F3 → **Crimson Glass: keep this window opaque** remembers unusual windowed game classes. `CRIMSON_GLASS_GAME=1` is also supported.
- New native prerequisites: Python D-Bus and GObject bindings. The installer downloads these through distro repositories. Both features have opt-out flags and are included in backups/restoration.

Download **Crimson-Glass-1.1.0.zip** and its checksum, extract it, and run `sh ./install.sh --all` as your desktop user, or omit `--all` for desktop only. To preserve existing panels, use `--no-layout` (automatic alignment stays disabled).

Visual assets are unchanged from 1.0.0. Application-owned alpha and third-party effects can still render transparency. Cross-distro live installations remain untested; see VALIDATION.txt for test scope.
