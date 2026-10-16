"""Packaging must ship the repaired login QML without changing other assets."""
import importlib.util
import io
from pathlib import Path
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("build_release", ROOT / "scripts/build_release.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class LoginPayload(unittest.TestCase):
    def test_replaces_login_theme_and_preserves_other_assets_and_aliases(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            asset = root / "assets.tar.xz"
            with tarfile.open(asset, "w:xz") as output:
                for name, data in [("system/sddm/CrimsonGlass/Main.qml", b"broken legacy theme"),
                                   ("data/icons/pack/icon.svg", b"unchanged icon")]:
                    info = tarfile.TarInfo(name)
                    info.size = len(data)
                    output.addfile(info, io.BytesIO(data))
                link = tarfile.TarInfo("data/icons/pack/alias.svg")
                link.type = tarfile.SYMTYPE
                link.linkname = "icon.svg"
                output.addfile(link)
            theme = root / "theme"
            theme.mkdir()
            (theme / "Main.qml").write_bytes(b"fixed login QML")
            (theme / "LICENSE.txt").write_bytes(b"license retained")
            builder.overlay_sddm(asset, theme)
            with tarfile.open(asset) as output:
                self.assertEqual(output.extractfile("system/sddm/CrimsonGlass/Main.qml").read(), b"fixed login QML")
                self.assertEqual(output.extractfile("system/sddm/CrimsonGlass/LICENSE.txt").read(), b"license retained")
                self.assertEqual(output.extractfile("data/icons/pack/icon.svg").read(), b"unchanged icon")
                self.assertEqual(output.getmember("data/icons/pack/alias.svg").linkname, "icon.svg")
                self.assertEqual(len(output.getnames()), 4)
