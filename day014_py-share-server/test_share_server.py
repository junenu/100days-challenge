import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from share_server import format_size, normalize_url_path, resolve_target


class ShareServerTest(unittest.TestCase):
    def test_normalize_url_path_collapses_parent_segments(self):
        self.assertEqual(normalize_url_path("/docs/../index.html?download=1"), "/index.html")

    def test_resolve_target_allows_files_under_root(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            file_path = root / "hello.txt"
            file_path.write_text("hello", encoding="utf-8")

            self.assertEqual(resolve_target(root, "/hello.txt"), file_path.resolve())

    def test_resolve_target_blocks_path_traversal(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()

            self.assertIsNone(resolve_target(root, "/../secret.txt"))

    def test_format_size_uses_human_readable_units(self):
        self.assertEqual(format_size(512), "512 B")
        self.assertEqual(format_size(1536), "1.5 KB")


if __name__ == "__main__":
    unittest.main()
