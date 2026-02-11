import tempfile
import unittest
from pathlib import Path

from appcc_yeva.cli import build_parser
from appcc_yeva.plan import load_default_plan
from appcc_yeva.preview import export_plan_preview


class PreviewTests(unittest.TestCase):
    def test_export_preview_generates_html(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "preview.html"
            export_plan_preview(load_default_plan(), output)

            self.assertTrue(output.exists())
            html = output.read_text(encoding="utf-8")
            self.assertIn("<!doctype html>", html.lower())
            self.assertIn("Plan APPCC de Yeva", html)
            self.assertIn("Recepción de materias primas", html)

    def test_cli_supports_serve_preview_command(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["servir-preview", "--host", "127.0.0.1", "--puerto", "8765"])
        self.assertEqual("servir-preview", args.command)
        self.assertEqual("127.0.0.1", args.host)
        self.assertEqual(8765, args.puerto)

    def test_cli_supports_preview_open_flag(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["previsualizar", "--abrir"])
        self.assertEqual("previsualizar", args.command)
        self.assertTrue(args.abrir)


if __name__ == "__main__":
    unittest.main()
