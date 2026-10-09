# KDE Store publication status

Account: SirFork1988. Upload terms accepted with the owner's explicit authorization.

All ten native component listings are published with source, credits, preview, and downloads.

- **wallpaper**: https://www.opendesktop.org/p/2377905/
- **plasma-style**: https://www.opendesktop.org/p/2377906/
- **aurorae**: https://www.opendesktop.org/p/2377909/
- **icons**: https://www.opendesktop.org/p/2377908/
- **kvantum**: https://www.opendesktop.org/p/2377910/
- **gtk**: https://www.opendesktop.org/p/2377911/
- **sddm**: https://www.opendesktop.org/p/2377913/
- **plymouth**: https://www.opendesktop.org/p/2377914/
- **color-scheme**: https://www.opendesktop.org/p/2377915/
- **konsole**: https://www.opendesktop.org/p/2377916/

The final native global-theme archive is built with the published IDs in `store-ids.json`; its upload is in progress.

Validation: component archives and icon aliases verified against extracted source. Native global KPackage install/show/remove passed in an isolated HOME; final source metadata passes KPackage AppStream generation and matches the final archive. No live theme was changed. End-to-end online KNS dependency installation has not been verified: the Store front end currently blocks some automated connections.

Color schemes use directly importable .colors/.colorscheme Store downloads; complete credited source and supplementary files remain in the repository. Full automatic widget realignment and game-opacity helpers are in the separate GitHub installer.
