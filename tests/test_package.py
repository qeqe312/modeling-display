from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import package_demo


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="geo3d-package-test-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        # Use a retained, non-inlined working page after the examples migration.
        self.source = (ROOT / "examples" / "外接球题建模示例" / "开发资料"
                       / "源码" / "外接球题建模示例.html")

    def test_offline_modes_and_licenses(self):
        for inline in (False, True):
            output = self.base / str(inline)
            page = package_demo.build(self.source, output, inline)
            html = page.read_text(encoding="utf-8")
            self.assertNotIn("cdn.jsdelivr.net", html)
            self.assertEqual((output / "three.min.js").exists(), not inline)
            self.assertTrue((output / "LICENSE").exists())
            self.assertTrue((output / "THREE-LICENSE.txt").exists())

    def test_mismatch_and_placeholders_refused(self):
        with patch.object(package_demo, "THREE_SHA256", "0" * 64):
            with self.assertRaises(ValueError):
                package_demo.build(self.source, self.base / "mismatch")
        with self.assertRaises(ValueError):
            package_demo.build(ROOT / "assets/template.html", self.base / "unfinished")

    def test_overwrite_and_source_overlap_refused(self):
        output = self.base / "output"
        page = package_demo.build(self.source, output)
        page.write_text("user file", encoding="utf-8")
        with self.assertRaises(ValueError):
            package_demo.build(self.source, output)
        self.assertEqual(page.read_text(), "user file")
        with self.assertRaises(ValueError):
            package_demo.build(self.source, self.source.parent)

    def test_active_markup_and_unexpected_scripts_refused(self):
        html = self.source.read_text(encoding='utf-8')
        for markup in ('<div onclick="alert(1)">x</div>', '<script>alert(1)</script>',
                       '<img src="https://example.invalid/tracker">', '<iframe srcdoc="x"></iframe>',
                       '<a href="java&#x73;cript:alert(1)">x</a>',
                       '<meta http-equiv="refresh" content="0; url=https://example.invalid">',
                       '<style>@import "https://example.invalid/style.css";</style>'):
            source = self.base / 'unsafe.html'
            source.write_text(html.replace('</body>', markup + '</body>'), encoding='utf-8')
            output = self.base / 'blocked'
            with self.assertRaises(ValueError):
                package_demo.build(source, output)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
