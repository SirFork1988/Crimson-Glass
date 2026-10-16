"""Load the real SDDM theme without logging out or attempting authentication.

Requires the Qt 6 greeter, Plasma QML modules and a readable system journal.
Reintroducing a removed Breeze type must fail this test instead of silently
passing because SDDM fell back to its emergency theme.
"""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import unittest
import uuid


ROOT = Path(__file__).resolve().parents[1]
THEME = Path(os.environ.get("CRIMSON_SDDM_TEST_THEME", ROOT / "store/components/sddm/CrimsonGlass"))


@unittest.skipUnless(shutil.which("sddm-greeter-qt6") and shutil.which("journalctl"),
                     "requires Qt 6 SDDM and journalctl")
class GreeterLoad(unittest.TestCase):
    def test_theme_instantiates_without_falling_back(self):
        marker = "CRIMSON_THEME_READY_" + uuid.uuid4().hex
        with tempfile.TemporaryDirectory(prefix="crimson-sddm-test-") as temporary:
            theme = Path(temporary) / "CrimsonGlass"
            shutil.copytree(THEME, theme)
            main = theme / "Main.qml"
            source = main.read_text()
            # Test-only completion probe, inside the actual theme root. Seeing
            # the greeter process stay alive alone also passes on its fallback.
            main.write_text(source.replace("id: root", f'id: root\n    Component.onCompleted: console.log("{marker}")', 1))
            env = dict(os.environ, QT_QPA_PLATFORM="offscreen", QT_QUICK_BACKEND="software")
            process = subprocess.Popen(["sddm-greeter-qt6", "--test-mode", "--theme", str(theme)],
                                       env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logs = ""
            try:
                deadline = time.monotonic() + 12
                while time.monotonic() < deadline:
                    result = subprocess.run(["journalctl", "-b", f"_PID={process.pid}",
                                             "--no-pager", "-o", "cat"], capture_output=True, text=True, check=True)
                    logs = result.stdout
                    if marker in logs or "is not a type" in logs or process.poll() is not None:
                        break
                    time.sleep(0.2)
                self.assertIn(marker, logs, "Crimson theme never instantiated (SDDM may have used its fallback):\n" + logs)
                self.assertNotIn("is not a type", logs)
                self.assertNotIn("TypeError:", logs)
                self.assertNotIn("ReferenceError:", logs)
                self.assertIsNone(process.poll(), "greeter exited during theme loading:\n" + logs)
            finally:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()


if __name__ == "__main__":
    unittest.main()
