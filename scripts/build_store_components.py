#!/usr/bin/env python3
"""Build native, source-complete KDE Store component packages without installing them.

The source asset archive and its adjacent sources/ directory come from the complete
Crimson Glass 1.1.0 release. Extracted sources are written to store/components/ so
Store listings can link directly to the corresponding editable source on GitHub.
No network, privilege, desktop configuration, or post-install hooks are used.
"""
# SPDX-License-Identifier: MIT
from __future__ import annotations
import argparse
import configparser
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import tarfile

VERSION = "1.1.0"
WEBSITE = "https://github.com/SirFork1988/Crimson-Glass"
EPOCH = 1791504000
PALETTE_HEADERS = """# SPDX-FileCopyrightText: Andrew Lake <jamboarder@gmail.com>
# SPDX-FileCopyrightText: Marco Martin <notmart@gmail.com>
# SPDX-FileCopyrightText: Nate Graham <nate@kde.org>
# SPDX-FileCopyrightText: Noah Davis <noahadvs@gmail.com>
# SPDX-FileCopyrightText: Neal Gompa <ngompa@kde.org>
# SPDX-FileCopyrightText: David Redondo <kde@david-redondo.de>
# SPDX-FileCopyrightText: Thomas Duckworth <tduck973564@gmail.com>
# SPDX-License-Identifier: LGPL-2.0-or-later
# Crimson Glass palette adaptation: SirFork1988, 2026.
# Source: https://invent.kde.org/plasma/breeze/-/blob/master/colors/BreezeDark.colors

"""
SPECS = [
    dict(key="icons", label="Icons", name="Crimson Glass Complete Icons", category="Full Icon Themes", roots=[("data/icons/CrimsonGlass-Icons", "CrimsonGlass-Icons")], license="GPL-3.0 AND LGPL-3.0-or-later", licenses=["Papirus-LICENSE", "Tela-COPYING", "Breeze-COPYING-ICONS"], install="Extract CrimsonGlass-Icons into ~/.local/share/icons, then select it in System Settings > Colors & Themes > Icons."),
    dict(key="plasma-style", label="Plasma-Style", name="Crimson Glass Plasma Style", category="Plasma Themes", roots=[("data/plasma/desktoptheme/CrimsonGlass", "CrimsonGlass")], license="GPL-3.0 AND LGPL-2.0-or-later", licenses=["GPL-3.0-WhiteSur-KDE.txt", "LGPL-2.0-or-later.txt"], install="Install with System Settings > Colors & Themes > Plasma Style > Get New, or kpackagetool6 --type Plasma/Theme --install ARCHIVE."),
    dict(key="aurorae", label="Aurorae", name="Crimson Glass Window Decorations", category="Aurorae Themes", roots=[("data/aurorae/themes/CrimsonGlass", "CrimsonGlass")], license="GPL-3.0", licenses=["GPL-3.0-WhiteSur-KDE.txt"], install="Extract CrimsonGlass into ~/.local/share/aurorae/themes and select it in System Settings > Colors & Themes > Window Decorations."),
    dict(key="kvantum", label="Kvantum", name="Crimson Glass Kvantum", category="Kvantum", roots=[("config/Kvantum/CrimsonGlass", "CrimsonGlass"), ("config/Kvantum/CrimsonGlassDolphin", "CrimsonGlassDolphin")], license="GPL-3.0", licenses=["GPL-3.0-WhiteSur-KDE.txt"], install="Install Kvantum and the Qt 5/6 style plugins from your distribution. Extract both directories. In Kvantum Manager install each theme directory, select CrimsonGlass, then assign CrimsonGlassDolphin to Dolphin if desired. Select Kvantum as the Qt application style."),
    dict(key="gtk", label="GTK", name="Crimson Glass GTK", category="GTK3/4 Themes", roots=[("data/themes/CrimsonGlass-Dark-red", "CrimsonGlass-Dark-red")], license="MIT", licenses=["MIT-WhiteSur-GTK.txt"], install="Extract CrimsonGlass-Dark-red into ~/.local/share/themes (or ~/.themes) and select it in GTK application style settings. GTK 2 requires the Murrine engine. Libadwaita applications may ignore GTK themes; this package does not overwrite your global GTK4 configuration."),
    dict(key="wallpaper", label="Wallpaper", name="Crimson Glass Wallpaper", category="Wallpapers KDE", roots=[("data/wallpapers/CrimsonGlass", "CrimsonGlass")], license="CC0-1.0", licenses=["CC0-1.0.txt"], install="Extract CrimsonGlass into ~/.local/share/wallpapers, then choose Crimson Glass in desktop wallpaper settings. Image is 3840x2160; editable SVG is included."),
    dict(key="sddm", label="SDDM", name="Crimson Glass Login", category="SDDM Login Themes", roots=[("system/sddm/CrimsonGlass", "CrimsonGlass")], license="LGPL-2.0-or-later AND CC0-1.0", licenses=["LGPL-2.0-or-later.txt", "CC0-1.0.txt"], install="Requires SDDM with Qt 6, Plasma 6 Breeze components, Kirigami, Plasma Components, and Qt5Compat GraphicalEffects. Install via System Settings > Login Screen (SDDM) > Install from File, then select Crimson Glass. Administrator authentication is required. This archive never changes the display manager automatically."),
    dict(key="plymouth", label="Plymouth", name="Crimson Glass Boot Splash", category="Plymouth Themes", roots=[("system/plymouth/crimson-glass", "crimson-glass")], license="GPL-2.0-or-later AND CC0-1.0", licenses=["GPL-2.0-or-later.txt", "CC0-1.0.txt", "OFL-1.1-Noto.txt"], install="Requires Plymouth's two-step renderer and Noto Sans/Noto Sans Light/Noto Sans Mono. Install crimson-glass into /usr/share/plymouth/themes using your distribution's theme manager, select it and rebuild the initramfs using your distribution's documented procedure. This archive contains no bootloader, initramfs, or privilege scripts."),
    dict(key="konsole", label="Konsole", name="Crimson Glass Konsole", category="Konsole Color Schemes", roots=[("data/konsole/CrimsonGlass.colorscheme", "CrimsonGlass.colorscheme"), ("data/konsole/CrimsonGlass.profile", "CrimsonGlass.profile")], license="MIT", licenses=["MIT-Crimson-Glass-Installer.txt"], install="Import CrimsonGlass.colorscheme in Konsole > Edit Profile > Appearance, or copy the .colorscheme and optional .profile to ~/.local/share/konsole. The profile uses Noto Sans Mono and does not set a shell command or working directory."),
    dict(key="color-scheme", label="Color-Scheme", name="Crimson Glass Colors", category="Plasma Color Schemes", roots=[("data/color-schemes/CrimsonGlass.colors", "CrimsonGlass.colors")], license="LGPL-2.0-or-later", licenses=["LGPL-2.0-or-later.txt"], install="Import CrimsonGlass.colors in System Settings > Colors & Themes > Colors, or copy it to ~/.local/share/color-schemes."),
]


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content.encode() if isinstance(content, str) else content)


def native_ini(path, updates):
    cfg = configparser.ConfigParser(interpolation=None, strict=False)
    cfg.optionxform = str
    cfg.read(path)
    for group, values in updates.items():
        if not cfg.has_section(group):
            cfg.add_section(group)
        for key, value in values.items():
            cfg[group][key] = value
    with path.open("w") as handle:
        cfg.write(handle, space_around_delimiters=False)


def json_metadata(path, name, description, structure=None):
    data = json.loads(path.read_text()) if path.exists() else {}
    plugin = data.setdefault("KPlugin", {})
    for key in list(plugin):
        if key.startswith(("Name[", "Description[")):
            del plugin[key]
    authors = plugin.setdefault("Authors", [])
    if not any(a.get("Name") == "SirFork1988" for a in authors):
        authors.insert(0, {"Name": "SirFork1988"})
    plugin.update(Name=name, Description=description, Version=VERSION, Website=WEBSITE)
    if structure:
        data["KPackageStructure"] = structure
    write(path, json.dumps(data, indent=2) + "\n")


def safe_relative(value):
    p = PurePosixPath(value)
    if p.is_absolute() or not p.parts or ".." in p.parts:
        raise ValueError(f"Unsafe archive path: {value}")
    return p


def extract_assets(archive, source_root):
    """Extract selected roots only; no symlink may escape its component tree."""
    count = 0
    with tarfile.open(archive, "r:xz") as source:
        for member in source:
            safe_relative(member.name)
            for spec in SPECS:
                for old, new in spec["roots"]:
                    if member.name != old and not member.name.startswith(old + "/"):
                        continue
                    relative = new + member.name[len(old):]
                    dest = source_root / spec["key"] / relative
                    base = source_root / spec["key"]
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    if member.isdir():
                        dest.mkdir(exist_ok=True)
                    elif member.isfile():
                        if dest.is_symlink():
                            raise ValueError(f"Refusing symlink destination: {dest}")
                        with source.extractfile(member) as reader, dest.open("wb") as writer:
                            shutil.copyfileobj(reader, writer)
                        dest.chmod(0o644)
                    elif member.issym():
                        if PurePosixPath(member.linkname).is_absolute():
                            raise ValueError(f"Absolute symlink: {member.name}")
                        target = (dest.parent / member.linkname).resolve()
                        if not target.is_relative_to(base.resolve()):
                            raise ValueError(f"Escaping symlink: {member.name}")
                        if dest.is_symlink():
                            dest.unlink()
                        dest.symlink_to(member.linkname)
                    else:
                        raise ValueError(f"Unsupported archive entry: {member.name}")
                    count += 1
    return count


def clean_svg_editor_paths(path):
    """Remove non-rendering upstream editor export paths, not artwork references."""
    data = path.read_bytes()
    data = re.sub(rb'\s+inkscape:export-filename="(?:/home/|file://)[^"]*"', b"", data)
    path.write_bytes(data)


def prepare(source_root, release, repo):
    for spec in SPECS:
        tree = source_root / spec["key"]
        roots = [new for _, new in spec["roots"]]
        # Single theme directory must remain the archive's only top-level entry.
        notice_dir = tree / roots[0] if (tree / roots[0]).is_dir() and len(roots) == 1 else tree
        for name in spec["licenses"]:
            shutil.copy2(repo / "licenses" / name, notice_dir / name)
        write(notice_dir / "INSTALL.txt", f"{spec['name']} {VERSION}\n\n{spec['install']}\n\nProject: {WEBSITE}\nFull installer and optional runtime: {WEBSITE}/releases/tag/v{VERSION}\nThis native component contains no automatic installer or post-install hooks.\n")
        credits = (repo / "CREDITS.txt").read_text()
        credits += "\nStore component packaging and Crimson Glass adaptations: SirFork1988.\n"
        if spec["key"] in ("color-scheme", "plasma-style"):
            credits += "\nPalette: adapted from KDE BreezeDark.colors; LGPL-2.0-or-later.\nAndrew Lake, Marco Martin, Nate Graham, Noah Davis, Neal Gompa, David Redondo, Thomas Duckworth.\nhttps://invent.kde.org/plasma/breeze/-/blob/master/colors/BreezeDark.colors\n"
        write(notice_dir / "CRIMSON-GLASS-NOTICES.txt", credits)
        write(notice_dir / "SOURCE.txt", f"Corresponding editable source and original notices are included in this package.\nBrowse this exact component: {WEBSITE}/tree/main/store/components/{spec['key']}\nVisual sources: SVG/SVGZ, QML, CSS, INI and PNG as applicable.\nArchive packaging script: {WEBSITE}/blob/main/scripts/build_store_components.py\nVersion: {VERSION}\n")

    plasma = source_root / "plasma-style/CrimsonGlass"
    json_metadata(plasma / "metadata.json", "Crimson Glass", "Charcoal and crimson glass; adapted from WhiteSur by Vince Liuice.", "Plasma/Theme")
    native_ini(plasma / "metadata.desktop", {"Desktop Entry": {"Name":"Crimson Glass", "Comment":"Charcoal and crimson glass; adapted from WhiteSur by Vince Liuice", "X-KDE-PluginInfo-Name":"CrimsonGlass", "X-KDE-PluginInfo-Author":"SirFork1988; Vince Liuice", "X-KDE-PluginInfo-Version":VERSION, "X-KDE-PluginInfo-Website":WEBSITE}, "Wallpaper":{"defaultWallpaperTheme":"CrimsonGlass"}})
    palette = source_root / "color-scheme/CrimsonGlass.colors"
    for path in (palette, plasma / "colors"):
        text = path.read_text()
        if not text.startswith("# SPDX-FileCopyrightText"):
            write(path, PALETTE_HEADERS + text)
    aurorae = source_root / "aurorae/CrimsonGlass"
    json_metadata(aurorae / "metadata.json", "Crimson Glass", "Crimson Glass window decorations; adapted from WhiteSur by Vince Liuice.", "aurorae")
    decoration_metadata = json.loads((aurorae / "metadata.json").read_text())
    decoration_metadata["KPlugin"]["License"] = "GPL-3.0"
    write(aurorae / "metadata.json", json.dumps(decoration_metadata, indent=2) + "\n")
    native_ini(aurorae / "metadata.desktop", {"Desktop Entry": {"Name":"Crimson Glass", "X-KDE-PluginInfo-Author":"SirFork1988; Vince Liuice", "X-KDE-PluginInfo-Version":VERSION, "X-KDE-PluginInfo-Website":WEBSITE}})
    native_ini(source_root / "gtk/CrimsonGlass-Dark-red/index.theme", {"Desktop Entry":{"Name":"Crimson Glass Dark Red", "Comment":"Charcoal and crimson GTK theme; adapted from WhiteSur GTK", "X-CrimsonGlass-Version":VERSION}})
    native_ini(source_root / "sddm/CrimsonGlass/metadata.desktop", {"SddmGreeterTheme":{"Author":"SirFork1988; KDE Visual Design Group and contributors", "Version":VERSION, "Website":WEBSITE, "License":"LGPL-2.0-or-later; CC0-1.0 (original Crimson Glass artwork)"}})
    for filename in ("CrimsonGlass.colorscheme", "CrimsonGlass.profile"):
        path = source_root / "konsole" / filename
        text = path.read_text()
        if not text.startswith("# SPDX-"):
            write(path, "# SPDX-FileCopyrightText: 2026 SirFork1988\n# SPDX-License-Identifier: MIT\n# Original Crimson Glass integration configuration.\n\n" + text)
    wallpaper = source_root / "wallpaper/CrimsonGlass"
    image_path = wallpaper / "CrimsonGlass.png"
    destination = wallpaper / "contents/images/3840x2160.png"
    destination.parent.mkdir(parents=True, exist_ok=True)
    if image_path.exists():
        image_path.replace(destination)
    write(wallpaper / "metadata.json", json.dumps({"KPlugin":{"Authors":[{"Name":"SirFork1988"}], "Id":"CrimsonGlass", "Name":"Crimson Glass", "Description":"Charcoal ribbon and crimson light", "License":"CC0-1.0", "Version":VERSION, "Website":WEBSITE}}, indent=2)+"\n")
    shutil.copy2(release / "sources/art/crimson-wallpaper.svg", wallpaper / "crimson-wallpaper.svg")
    for key, root in (("sddm", "CrimsonGlass"), ("plymouth", "crimson-glass")):
        sources = source_root / key / root / "sources"
        shutil.copytree(release / "sources/art", sources / "art", dirs_exist_ok=True)
        if key == "plymouth":
            shutil.copytree(release / "sources/plymouth", sources / "plymouth", dirs_exist_ok=True)
            builder = sources / "plymouth/build_theme.py"
            code = builder.read_text().replace("ROOT / 'assets/data/plasma/look-and-feel/org.crimsonglass.desktop/contents/splash/images/crimson-mark.svg'", "ROOT / 'sources/art/crimson-mark.svg'")
            write(builder, code)
    # No rendering changes: sanitize editor-only paths inherited from upstream SVGs.
    for path in source_root.rglob("*.svg"):
        if path.is_file() and not path.is_symlink():
            data = path.read_bytes()
            if b"/home/" in data or b"file://" in data:
                clean_svg_editor_paths(path)


def entries(tree):
    # Path.rglob does not descend directory symlinks, preserving aliases as aliases.
    return sorted(tree.rglob("*"), key=lambda p: p.relative_to(tree).as_posix())


def verify_tree(tree):
    counts = dict(files=0, symlinks=0, directories=0)
    for path in entries(tree):
        if path.is_symlink():
            if not path.resolve().is_relative_to(tree.resolve()) or not path.exists():
                raise ValueError(f"Broken or escaping symlink: {path}")
            counts["symlinks"] += 1
        elif path.is_file():
            counts["files"] += 1
        elif path.is_dir():
            counts["directories"] += 1
        else:
            raise ValueError(f"Special file: {path}")
    return counts


def archive_tree(tree, destination):
    with destination.open("wb") as output:
        with gzip.GzipFile(filename="", fileobj=output, mode="wb", mtime=EPOCH) as compressor:
            with tarfile.open(fileobj=compressor, mode="w|") as archive:
                for path in entries(tree):
                    info = archive.gettarinfo(path, arcname=path.relative_to(tree).as_posix())
                    info.uid = info.gid = 0
                    info.uname = info.gname = "root"
                    info.mtime = EPOCH
                    info.mode = 0o755 if info.isdir() else 0o777 if info.issym() else 0o644
                    with path.open("rb") if info.isfile() else io.BytesIO() as stream:
                        archive.addfile(info, stream if info.isfile() else None)
    with tarfile.open(destination, "r:gz") as archive:
        actual = 0
        for item in archive:
            safe_relative(item.name)
            if item.isfile():
                digest = hashlib.sha256(archive.extractfile(item).read()).digest()
                if digest != hashlib.sha256((tree / item.name).read_bytes()).digest():
                    raise ValueError(f"Archive content mismatch: {item.name}")
            elif item.issym() and item.linkname != os.readlink(tree / item.name):
                raise ValueError(f"Archive symlink mismatch: {item.name}")
            actual += 1
    if actual != len(entries(tree)):
        raise ValueError("Archive entry count mismatch")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", type=Path, required=True, help="Extracted complete release containing assets.tar.xz and sources/")
    parser.add_argument("--output", type=Path, default=Path("dist/kde-store"))
    parser.add_argument("--refresh-source", action="store_true", help="Re-extract selected source trees from the release (overwrites same-named generated files)")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    source_root = repo / "store/components"
    args.output.mkdir(parents=True, exist_ok=True)
    if args.refresh_source or not source_root.exists():
        print(f"Extracted {extract_assets(args.release / 'assets.tar.xz', source_root)} selected entries", flush=True)
        prepare(source_root, args.release, repo)
    catalog = {"version":VERSION, "project":WEBSITE, "source_layout":"Fully extracted editable corresponding source under store/components/", "components":[], "upstream_companions":[{"name":"Qogir Dark Cursors", "store_url":"https://store.kde.org/p/1366182", "source_url":"https://github.com/vinceliuice/Qogir-icon-theme", "upload":False, "reason":"Appearance unmodified; use upstream listing."}, {"name":"Andromeda Launcher", "store_url":"https://store.kde.org/p/2144212", "source_url":"https://github.com/EliverLara/AndromedaLauncher", "upload":False, "reason":"Unmodified upstream component; use author's Plasma 6 listing."}]}
    checksums = []
    for spec in SPECS:
        tree = source_root / spec["key"]
        counts = verify_tree(tree)
        name = f"Crimson-Glass-{spec['label']}-{VERSION}.tar.gz"
        archive = args.output / name
        archive_tree(tree, archive)
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        checksums.append(f"{digest}  {name}\n")
        item = {"key":spec["key"], "name":spec["name"], "category":spec["category"], "version":VERSION, "archive":name, "sha256":digest, "bytes":archive.stat().st_size, "license":spec["license"], "package_ids":[new for _, new in spec["roots"]], "source_url":f"{WEBSITE}/tree/main/store/components/{spec['key']}", "installation":spec["install"], "validation":counts, "store_id":None}
        catalog["components"].append(item)
        print(f"Verified {name}: {counts}", flush=True)
    for key, name in (("color-scheme", "CrimsonGlass.colors"), ("konsole", "CrimsonGlass.colorscheme")):
        destination = args.output / name
        shutil.copy2(source_root / key / name, destination)
        checksums.append(f"{hashlib.sha256(destination.read_bytes()).hexdigest()}  {name}\n")
    write(repo / "store/component-catalog.json", json.dumps(catalog, indent=2) + "\n")
    write(args.output / "component-catalog.json", json.dumps(catalog, indent=2) + "\n")
    write(args.output / "SHA256SUMS", "".join(checksums))
    print("All native component archives verified. No desktop settings changed.", flush=True)


if __name__ == "__main__":
    main()
