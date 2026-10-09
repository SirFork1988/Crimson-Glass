# Native Plasma 6 Global Theme packaging

The editable package lives in `store/global-theme/org.crimsonglass.desktop`.
It uses `KPackageStructure: Plasma/LookAndFeel`, package ID
`org.crimsonglass.desktop`, and version 1.1.0. The splash, preview, defaults,
Breeze-derived crimson palette and optional layout are bundled. License notices
are included; palette attribution is LGPL-2.0-or-later, splash/original artwork
CC0-1.0, and layout integration MIT.

## Native appearance and complete installer

The native theme selects the CrimsonGlass Plasma style, CrimsonGlass-Icons,
CrimsonGlass Aurorae decoration, CrimsonGlass wallpaper, Qogir-Dark cursor and
included splash. It uses Breeze Qt widgets with the crimson palette, which
works without an external Qt style plugin. Kvantum and GTK are separate
components selected by the user after installing their distro prerequisites.
Kvantum Manager must select the CrimsonGlass style; the separate Dolphin
variant needs the configuration described in the Kvantum component.

The optional native desktop layout is offered only through KDE's desktop
layout selection/reset workflow. It supplies a global-menu bar, Andromeda
launcher (KDE Application Launcher fallback), floating centered dock, clock,
and CPU/memory/network/storage monitors. It uses current logical dimensions
and portable aggregate sensor names. Existing applications populate dock
launchers. A workspace too small for the monitors receives the panels only.
The layout does not delete objects or run shell commands; KDE owns any reset
explicitly requested through its dialog. Applying appearance alone preserves
the current panel/widget layout.

The native package sets monitor positions once. Automatic display-change
realignment and game opacity detection require the full 1.1.0 installer and
its Python D-Bus helper. SDDM/Plymouth, fonts and native distro packages also
remain separate. Store descriptions must say screenshots depict the complete
installer plus companions, not claim native Global Theme installation alone
sets up every feature. System-monitor widgets require Plasma System Monitor.

## Dependency publication order

Publish native companion listings first, then put their real numeric Store
content IDs in a local JSON object using these keys:

| Key | Native KNS route | Package name selected by defaults |
| --- | --- | --- |
| `plasma-style` | `plasma-themes.knsrc` | `CrimsonGlass` |
| `icons` | `icons.knsrc` | `CrimsonGlass-Icons` |
| `window-decoration` | `aurorae.knsrc` | `__aurorae__svg__CrimsonGlass` |
| `wallpaper` | `wallpaper.knsrc` | `CrimsonGlass` |
| `cursors` | `xcursor.knsrc` | `Qogir-Dark` |
| `launcher` | `plasmoids.knsrc` | `com.github.SnoutBug.mmckLauncher` |
| `color-scheme` (optional) | `colorschemes.knsrc` | `CrimsonGlass` |

The example JSON deliberately uses `null` for unpublished products. It is not
loaded as package metadata. The builder rejects missing, malformed or unknown
entries for a release build and inserts dependency URLs into the archive.
Color-scheme dependency is optional because `contents/colors` supplies the
complete palette. Native package archives must not contain fabricated content
IDs. Existing upstream listing candidates are Qogir cursors 1366182 and
Andromeda 2144212; verify their current compatible files before final build.
Kvantum, GTK, login and boot companions are linked in the listing rather than
forced through this native global theme dependency resolver.

```bash
python3 scripts/build_store_global.py --store-ids /path/to/published-ids.json
```

This creates `dist/store/Crimson-Glass-Global-Theme-1.1.0.tar.gz` and its SHA256
file. It does not install or apply the theme. Keep the verified ID mapping
alongside the publication records after creation.

For package validation before the listings exist:

```bash
python3 scripts/build_store_global.py --draft
```

The output has `-DRAFT` in its name and omits KNS dependencies. It is only for
local validation and must not be uploaded as the finished global theme.

## Verification

Validated on Plasma 6.7.5 / KPackage 6 using an isolated temporary `HOME`,
`XDG_DATA_HOME`, `XDG_CONFIG_HOME`, and `XDG_CACHE_HOME`, with the normal
`plasma/look-and-feel` location below that temporary data home. Native
`kpackagetool6 --type Plasma/LookAndFeel --install`, `--show`, and `--remove`
recognized the correct package ID/name/path and succeeded. The test did not
apply any desktop appearance or layout to the running session. Avoid testing
lookup with an arbitrary `--packageroot`: the LookAndFeel package's fallback
lookup can resolve Breeze when the custom root is outside its standard path.

Qt 6 QJSEngine layout checks cover nine logical desktop sizes from 640x480 to
3840x2160, including the user's 1707x960 HiDPI TV workspace. At supported sizes,
five monitors are in bounds with no overlap; undersized displays receive
panels. A missing Andromeda launcher uses native Kickoff. Mock removal hooks
would fail if the layout tried to delete panels/widgets. Final remote KNS
download resolution requires the real published listing IDs.

## References checked

- [KDE Global Theme package guide](https://userbase.kde.org/Plasma/Create_a_Global_Theme_Package)
- [Plasma 6 theme packaging](https://develop.kde.org/docs/plasma/theme/theme-porting-to-plasma6/)
- [KDE Global Theme user documentation](https://docs.kde.org/stable_kf6/en/plasma-workspace/kcontrol/lookandfeel/)
- [Native LookAndFeel package structure](https://github.com/KDE/plasma-workspace/blob/master/shell/packageplugins/lookandfeel/lookandfeel.cpp)
- [KDE palette/style application implementation](https://github.com/KDE/plasma-workspace/blob/master/libklookandfeel/klookandfeelmanager.cpp)

Store source link:
`https://github.com/SirFork1988/Crimson-Glass/tree/main/store/global-theme`
