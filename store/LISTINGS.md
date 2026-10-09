# Crimson Glass — KDE Store listing copy

Prepared for the **SirFork1988** account, release **1.1.0**. These descriptions cover the native Store packages. The [complete installer](https://github.com/SirFork1988/Crimson-Glass/releases/tag/v1.1.0) remains a separate download.

## Publication fields and shared links

- Homepage: https://github.com/SirFork1988/Crimson-Glass
- Issues: https://github.com/SirFork1988/Crimson-Glass/issues
- Changelog: https://github.com/SirFork1988/Crimson-Glass/blob/main/RELEASE-NOTES.md
- Gallery: https://github.com/SirFork1988/Crimson-Glass/blob/main/screenshots/README.md
- Credits: https://github.com/SirFork1988/Crimson-Glass/blob/main/CREDITS.txt
- Extracted component source: https://github.com/SirFork1988/Crimson-Glass/tree/main/store/components
- Extracted global-theme source: https://github.com/SirFork1988/Crimson-Glass/tree/main/store/global-theme

Use the exact extracted component directory as each modified product's **Source** link after it has been pushed and checked publicly. A release ZIP or an upstream repository alone is not the extracted source for our modifications. Category names below are the intended Store categories; select the matching current form entry.

The Store's Original/Mod field is separate from the license. It describes how much of the submitted work was created or changed. Use **Original** only for independently created work. For derivatives, select **Mod** only where the actual changes satisfy the form's stated threshold; otherwise leave that field blank and still disclose the upstream base. Do not invent a percentage. In particular, the large icon collection includes many unchanged upstream assets, so its added artwork does not establish that a percentage threshold is met across the entire collection.

The single Store license selector cannot replace file-level notices. Choose the principal license shown below and state the included exceptions in the description. Preserve all copyrights, license texts, corresponding source, and modification notices. The repository's MIT installer license does **not** relicense the complete theme.

## Crimson Glass — Plasma 6 Global Theme

**Category:** Global Themes (Plasma 6)  
**Tags:** plasma6, global-theme, dark, red, crimson, glass  
**Preview order:** `desktop.png`, `dolphin.png`, `splash.png`, `global-menu.png`  
**Classification:** Original applies only to original preset/splash/artwork files; any bundled derived palette retains its own license. Do not classify the entire multi-component collection as original.  
**File:** `Crimson-Glass-Global-Theme-1.1.0.tar.gz` (build after publishing the required companion IDs)  
**License selector:** LGPLv2; palette LGPL-2.0-or-later, original splash/artwork CC0-1.0, layout integration MIT.

**Description:**

Crimson Glass brings charcoal surfaces, ruby accents, and a matching splash to KDE Plasma 6. Pair it with the Crimson Glass Plasma Style, Icons, Aurorae decoration, and Kvantum styles for the coordinated desktop shown in the gallery.

This is the native Global Theme package. Its component dependencies must be available before applying the complete appearance. Kvantum requires the Kvantum engine and selecting the CrimsonGlass style in Kvantum Manager. GTK, login, and boot themes are available separately. The Store package does not install system packages, run the Python desktop helper, or make privileged login/boot changes.

The optional native desktop layout provides the global-menu panel, floating dock, and monitoring widgets through KDE's layout selection workflow. Automatic display-change realignment, game opacity detection, and the full Kvantum/GTK configuration require the separately documented GitHub installer. Global menus work with applications that export menus; application-owned transparency and isolated application themes can differ.

Original Crimson Glass preset, splash, ribbon, and monogram by Crimson Glass contributors. Companion assets retain the licenses and credits on their respective pages. Designed for Plasma 6; the complete desktop was tested on CachyOS with Plasma 6.7.5. Other distributions' live installations remain untested.

## Crimson Glass Complete Icons

**Source:** https://github.com/SirFork1988/Crimson-Glass/tree/main/store/components/icons  
**File:** `Crimson-Glass-Icons-1.1.0.tar.gz`  
**Category:** Full Icon Themes  
**Tags:** icons, red, crimson, dark, papirus, plasma6  
**Preview order:** `icons.png`, `dolphin.png`  
**Classification:** Derivative; leave the Original/Mod field blank unless a documented comparison supports the Mod threshold.  
**License selector:** GPLv3; describe LGPL-3.0-or-later Breeze files and artwork clarification separately.

**Description:**

A complete crimson icon collection with red generic and special folders, ruby symbolic accents, and 28 original application artworks. The collection provides 25,987 distinct icon names, combining Papirus coverage with supplemental Tela and Breeze assets. The current package contains no macOS icon-pack sources.

Select **CrimsonGlass-Icons** in System Settings → Colors & Themes → Icons. The reference sheet is a rendered asset preview; the Dolphin image is an actual application capture.

Based on Papirus by the Papirus Development Team and Tela by Vince Liuice and contributors, both GPL-3.0. Supplemental Breeze artwork is by Uri Herrera, the KDE Visual Design Group, and contributors under LGPL-3.0-or-later with its included artwork clarification. Crimson modifications include folder gradients, symbolic accents, application art, and SVG repairs; original custom SVG artwork is GPL-3.0-or-later. Full editable SVGs, notices, and detailed custom-art credits accompany the download. Application names and logos remain their owners' trademarks.

## Crimson Glass Plasma Style

**Source:** https://github.com/SirFork1988/Crimson-Glass/tree/main/store/components/plasma-style  
**File:** `Crimson-Glass-Plasma-Style-1.1.0.tar.gz`  
**Category:** Plasma Themes  
**Tags:** plasma6, plasma-style, dark, red, translucent, glass  
**Preview order:** `desktop.png`, `widgets.png`, `global-menu.png`  
**Classification:** Derivative; use Mod only if the form's threshold is supported.  
**License selector:** GPLv3; bundled Breeze-derived color definitions are LGPL-2.0-or-later.

**Description:**

Charcoal and crimson Plasma surfaces for panels, menus, tooltips, and widgets. This companion to the Crimson Glass Global Theme keeps the shell dark with ruby accents and translucent glass styling. Blur requires working KWin compositing and the Blur effect.

Select **Crimson Glass** in System Settings → Colors & Themes → Plasma Style. Panel placement, widgets, application styles, and icons are configured separately. The gallery shows the complete setup.

Adapted from [WhiteSur KDE](https://github.com/vinceliuice/WhiteSur-kde) by Vince Liuice and contributors under GPL-3.0, with Crimson palette and styling changes. The bundled palette derives from KDE Breeze Dark under LGPL-2.0-or-later. Source SVG/SVGZ and configuration files, original notices, and modification details are included.

## Crimson Glass Window Decoration

**Source:** https://github.com/SirFork1988/Crimson-Glass/tree/main/store/components/aurorae  
**File:** `Crimson-Glass-Aurorae-1.1.0.tar.gz`  
**Category:** Aurorae Themes  
**Tags:** aurorae, window-decoration, plasma6, dark, red, glass  
**Preview order:** `dolphin.png`, `qt6-kvantum.png`  
**Classification:** Derivative; leave blank if changes are below the Mod threshold.  
**License selector:** GPLv3.

**Description:**

A dark Aurorae window frame for Crimson Glass, with compact traffic-light controls and matching glass styling. Use it with the Crimson palette and Kvantum styles for the application appearance shown in the screenshots.

Select **CrimsonGlass** in System Settings → Colors & Themes → Window Decorations. Button placement is configurable in KDE's titlebar-button settings. Icons and application interiors are separate components.

Adapted from [WhiteSur KDE](https://github.com/vinceliuice/WhiteSur-kde) by Vince Liuice and contributors, GPL-3.0. Editable SVG assets, configuration, and original license notices are included.

## Crimson Glass Kvantum

**Source:** https://github.com/SirFork1988/Crimson-Glass/tree/main/store/components/kvantum  
**File:** `Crimson-Glass-Kvantum-1.1.0.tar.gz`  
**Category:** Kvantum  
**Tags:** kvantum, qt5, qt6, dolphin, dark, red, glass  
**Preview order:** `qt6-kvantum.png`, `qt5-kvantum.png`, `dolphin.png`  
**Classification:** Derivative; use Mod only if the form's threshold is supported.  
**License selector:** GPLv3.

**Description:**

Charcoal and ruby Qt Widgets styles with translucent menus and windows. The download includes **CrimsonGlass** and **CrimsonGlassDolphin**, a separate glass preset for Dolphin.

Install the Kvantum engine for the Qt versions used by your applications. Import the styles in Kvantum Manager, select **CrimsonGlass**, and use Kvantum's application-theme assignment for Dolphin if desired. Select Kvantum as KDE's application style and use the Crimson Glass color scheme. Blur requires KWin compositing; Qt Quick/Kirigami, Electron, and applications with their own rendering may use other styling.

Adapted from [WhiteSur KDE](https://github.com/vinceliuice/WhiteSur-kde) by Vince Liuice and contributors, GPL-3.0. Crimson changes cover ruby accents, dark surfaces, translucency, and the Dolphin configuration. Editable SVG and kvconfig source is included.

## Crimson Glass GTK

**Source:** https://github.com/SirFork1988/Crimson-Glass/tree/main/store/components/gtk  
**File:** `Crimson-Glass-GTK-1.1.0.tar.gz`  
**Category:** GTK3/4 Themes  
**Tags:** gtk, gtk3, gtk4, dark, red, crimson  
**Preview order:** `gtk3.png`, `gtk4.png`  
**Classification:** Derivative; use Mod only if the form's threshold is supported.  
**License selector:** MIT.

**Description:**

A dark ruby GTK companion to the Crimson Glass KDE desktop. The named theme **CrimsonGlass-Dark-red** includes GTK2, GTK3, and GTK4 assets.

Select it in KDE's GTK application-style settings or your desktop's GTK theme selector. GTK2 engines can be required by older applications. Libadwaita applications and sandboxed Flatpak/Snap applications can keep their own appearance. This component does not silently replace global GTK4 configuration; the full installer documents that separate integration choice.

Adapted from [WhiteSur GTK](https://github.com/vinceliuice/WhiteSur-gtk-theme). Copyright (c) 2021 WhiteSur Developers, MIT. Crimson modifications add a ruby palette and matching configuration. Original notices and editable CSS/SVG source are included.

## Crimson Glass Ribbon Wallpaper

**Source:** https://github.com/SirFork1988/Crimson-Glass/tree/main/store/components/wallpaper  
**File:** `Crimson-Glass-Wallpaper-1.1.0.tar.gz`  
**Category:** Wallpapers KDE Plasma  
**Tags:** wallpaper, abstract, red, black, crimson, plasma6  
**Preview:** `desktop.png` as a contextual desktop image; use the packaged wallpaper itself as the primary preview.  
**Classification:** Original.  
**License selector:** CC0.

**Description:**

An original charcoal and crimson ribbon wallpaper created for the Crimson Glass desktop. The Plasma wallpaper package and editable vector artwork are included.

Install the wallpaper package and select it from the desktop wallpaper settings. Widgets and panels in the contextual screenshot are separate components.

Original Crimson Glass artwork by Crimson Glass contributors, dedicated under CC0-1.0. The source vector and license are included.

## Crimson Glass SDDM Login

**Source:** https://github.com/SirFork1988/Crimson-Glass/tree/main/store/components/sddm  
**File:** `Crimson-Glass-SDDM-1.1.0.tar.gz`  
**Category:** SDDM Login Themes  
**Tags:** sddm, login, plasma6, dark, red, glass  
**Preview:** `login.png` — caption: “SDDM test-mode preview; account label covered.”  
**Classification:** Mod where the documented visual/QML changes meet the form's threshold.  
**License selector:** LGPLv2; description must identify LGPL-2.0-or-later QML and CC0-1.0 original artwork.

**Description:**

A matching SDDM login screen with a dark glass panel, Crimson ribbon background, clock, and original monogram. This is a login theme for an existing SDDM setup; it does not switch your display manager.

Install through KDE's Login Screen (SDDM) settings with administrator authorization. The screenshot is a test-mode preview with the account label covered. Theme appearance depends on the SDDM/Qt environment and installed fonts.

Adapted from KDE Breeze SDDM QML by David Edmundson, Boudhayan Gupta, Aleix Pol Gonzalez, and KDE contributors. QML retains LGPL-2.0-or-later SPDX headers. The original Crimson ribbon and monogram are CC0-1.0. Complete QML/source artwork and notices are included; individual file licenses govern.

## Crimson Glass Plymouth Boot

**Source:** https://github.com/SirFork1988/Crimson-Glass/tree/main/store/components/plymouth  
**File:** `Crimson-Glass-Plymouth-1.1.0.tar.gz`  
**Category:** Plymouth Themes  
**Tags:** plymouth, boot, splash, dark, red, crimson  
**Preview order:** `boot.png`, `boot-password.png`, `boot-updates.png` — label every image “Rendered layout preview.”  
**Classification:** Derivative; use Mod only if the form's threshold is supported.  
**License selector:** GPLv2 or later; original Crimson artwork is CC0-1.0.

**Description:**

A native Plymouth boot theme with a Crimson ribbon background, red spinner/input assets, and matching password/update layouts. Designed to accompany the Crimson Glass login and Plasma splash themes.

The images are rendered layout previews, not photographs or captures from an actual reboot. Install using your distribution's Plymouth and initramfs procedure; Plymouth and its splash kernel configuration must already be supported. The native archive does not change your bootloader or regenerate initramfs automatically. The separate full installer supports documented optional startup integration.

Adapted from Plymouth spinner/input assets under GPL-2.0-or-later, with Crimson tinting and original CC0-1.0 ribbon/wordmark artwork. Asset origins, configuration, source artwork, and build sources accompany the download.

## Crimson Glass Color Scheme

**Source:** https://github.com/SirFork1988/Crimson-Glass/tree/main/store/components/color-scheme  
**Files:** `CrimsonGlass.colors` and `Crimson-Glass-Color-Scheme-1.1.0.tar.gz`  
**Category:** KDE Color Schemes  
**Tags:** color-scheme, plasma6, dark, red, crimson  
**Preview order:** `qt6-kvantum.png`, `dolphin.png` — note that application style/icons are separate.  
**Classification:** Mod: an extensively recolored Breeze Dark palette; retain source credit.  
**License selector:** LGPLv2; explicitly LGPL-2.0-or-later.

**Description:**

Charcoal backgrounds, light text, ruby selection/focus colors, and coordinated titlebar colors for KDE applications. The palette retains distinct semantic warning, error, and success colors.

Import **CrimsonGlass.colors** in System Settings → Colors & Themes → Colors. The screenshots also use the separately available Kvantum style, window decoration, and icon theme; a color scheme alone does not enable transparency.

Adapted from KDE Breeze Dark by Andrew Lake, Marco Martin, Nate Graham, Noah Davis, Neal Gompa, David Redondo, Thomas Duckworth, and KDE contributors, under LGPL-2.0-or-later. Crimson modifications recolor the palette and adjust selection/link contrast. Editable configuration, source credits, and the LGPL notice accompany the download.

## Crimson Glass Konsole

**Source:** https://github.com/SirFork1988/Crimson-Glass/tree/main/store/components/konsole  
**Files:** `CrimsonGlass.colorscheme` and `Crimson-Glass-Konsole-1.1.0.tar.gz`  
**Category:** Konsole Color Schemes  
**Tags:** konsole, terminal, dark, red, crimson, translucent  
**Preview:** capture a clean Konsole window before publishing; the existing gallery contains no dedicated terminal screenshot.  
**Classification:** Original configuration.  
**License selector:** MIT, as explicitly recorded for the original integration configuration in the native package.

**Description:**

A dark Konsole color scheme with ruby red, softly balanced terminal colors, an 88% background-opacity setting, and blur enabled. It complements the Crimson Glass KDE palette while preserving different ANSI colors for terminal output.

Import **CrimsonGlass.colorscheme** in your Konsole profile's Appearance settings. Working desktop compositing is needed for transparency and blur. This component changes the terminal palette; it does not install a shell configuration, prompt, or fonts.

Original Crimson Glass terminal configuration by Crimson Glass contributors, MIT. The editable colorscheme and its license notice are included.

## Reuse upstream entries; do not duplicate their products

- **Andromeda Launcher Plasma 6:** [KDE Store product 2144212](https://store.kde.org/p/2144212), by EliverLara and contributors. The [author's repository](https://github.com/EliverLara/AndromedaLauncher) links that product and is the preferred installation source. Product 2048016 is the older Plasma 5 entry. The unmodified launcher is not a new Crimson Glass product.
- **Qogir cursors:** [KDE Store product 1366182](https://store.kde.org/p/1366182), by Vince Liuice and contributors. Choose the dark variant. The [upstream repository](https://github.com/vinceliuice/Qogir-icon-theme) includes cursor sources. Product 1296407 is the broader icon-theme entry, not the standalone cursor entry. No cursor archive is republished as a Crimson Glass product.
- The five monitoring widgets are KDE's built-in clock/system-monitor applets. The full installer configures them; do not upload copies as original Crimson Glass applets.
- Noto fonts come from distribution packages. Credit the Noto Project and its SIL OFL-1.1 license when mentioning them; no separate Crimson font upload.

## Publication checks tied to these descriptions

1. Upload component packages before publishing a dependency-linked Global Theme. Use verified product IDs and download-file IDs in dependency metadata; do not publish placeholders.
2. Keep the full installer ZIP outside the native Global Theme install slot. The Store theme package cannot promise to install Python/D-Bus packages, autostart the game-opacity helper, update login/boot settings, or create the complete configured panel/widget layout unless those behaviors are implemented and tested separately.
3. Push fully extracted modified source and verify every product's Source URL before making it public. Include original notices, modification dates, and corresponding artwork/build sources. The standalone palette and Plasma Style's embedded palette must retain the Breeze Dark LGPL attribution.
4. Existing `desktop.png` does not show the top panel/dock. Existing launcher/dock captures have superseded icons and should not be used as current previews. Add fresh clean captures before claiming the screenshots show those components.
5. Preserve gallery captions: icon sheet and boot images are rendered previews; SDDM is test mode; screenshots do not demonstrate animation. Add a Konsole screenshot for its separate listing.
6. Avoid claiming a universal one-click install, official KDE endorsement, support for Plasma 5, or live testing on distributions that have not been exercised. Public app logos remain their owners' trademarks.

## Source verification notes

- The author's [Andromeda repository](https://github.com/EliverLara/AndromedaLauncher) identifies product 2144212. Qogir product 1366182 is also linked by Vince Liuice in [his upstream Store-profile comments](https://www.box-look.org/u/vinceliuice/morecomments/page/12/); direct Store fetches can block automated readers.
- The local build script `work/build_crimson.py` records that the Crimson palette was derived from Breeze Dark. The [official KDE source](https://raw.githubusercontent.com/KDE/breeze/master/colors/BreezeDark.colors) identifies the authors and LGPL-2.0-or-later license.
- [KDE's Plasma 6 porting documentation](https://develop.kde.org/docs/plasma/theme/theme-porting-to-plasma6/) describes the LookAndFeel KPackage structure and Plasma 6 packaging requirements.
