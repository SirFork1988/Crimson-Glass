Rebuild the theme assets with Python3 and PyQt6:
  QT_QPA_PLATFORM=offscreen python3 sources/plymouth/build_theme.py
Run from the package root. Output stays in build/plymouth; it does not install system files.
Native spinner PNG source assets are GPL-2.0-or-later, with provenance in ASSET-ORIGINS.txt.
Original ribbon/monogram SVGs are in sources/art under CC0-1.0.
