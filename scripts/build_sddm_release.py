#!/usr/bin/env python3
"""Build only the source-complete native SDDM archive and its checksum."""
# SPDX-License-Identifier: MIT
import argparse
import configparser
import hashlib
from pathlib import Path

from build_store_components import archive_tree, verify_tree

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    source = ROOT / "store/components/sddm"
    metadata = configparser.ConfigParser(interpolation=None)
    metadata.read(source / "CrimsonGlass/metadata.desktop")
    version = metadata["SddmGreeterTheme"]["Version"]
    counts = verify_tree(source)
    args.output.mkdir(parents=True, exist_ok=True)
    output = args.output / f"Crimson-Glass-SDDM-{version}.tar.gz"
    archive_tree(source, output)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_name(output.name + ".sha256").write_text(f"{digest}  {output.name}\n")
    print(f"{output}\nSHA256 {digest}\nVerified {counts['files']} files.")


if __name__ == "__main__":
    main()
