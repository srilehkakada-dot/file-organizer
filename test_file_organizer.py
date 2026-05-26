import shutil
import tempfile
import unittest
from pathlib import Path
from file_organizer import get_category, organize, file_hash


class TestGetCategory(unittest.TestCase):
    def test_image(self):
        self.assertEqual(get_category(Path("photo.jpg")), "Images")

    def test_document(self):
        self.assertEqual(get_category(Path("report.pdf")), "Documents")

    def test_video(self):
        self.assertEqual(get_category(Path("clip.mp4")), "Videos")

    def test_audio(self):
        self.assertEqual(get_category(Path("song.mp3")), "Audio")

    def test_archive(self):
        self.assertEqual(get_category(Path("backup.zip")), "Archives")

    def test_code(self):
        self.assertEqual(get_category(Path("script.py")), "Code")

    def test_unknown(self):
        self.assertEqual(get_category(Path("mystery.xyz")), "Others")

    def test_case_insensitive(self):
        self.assertEqual(get_category(Path("IMAGE.JPG")), "Images")


class TestOrganize(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def _make(self, name: str, content: str = "data") -> Path:
        p = self.tmp / name
        p.write_text(content)
        return p

    def test_moves_file_to_category_folder(self):
        self._make("photo.jpg")
        organize(str(self.tmp), preview=False)
        self.assertTrue((self.tmp / "Images" / "photo.jpg").exists())

    def test_preview_does_not_move(self):
        self._make("photo.jpg")
        organize(str(self.tmp), preview=True)
        self.assertTrue((self.tmp / "photo.jpg").exists())
        self.assertFalse((self.tmp / "Images").exists())

    def test_skips_duplicates(self):
        self._make("a.jpg", "same")
        self._make("b.jpg", "same")
        stats = organize(str(self.tmp), preview=False, skip_duplicates=True)
        self.assertEqual(stats["moved"], 1)
        self.assertEqual(stats["duplicates"], 1)

    def test_no_skip_duplicates(self):
        self._make("a.jpg", "same")
        self._make("b.jpg", "different")
        stats = organize(
            str(self.tmp), preview=False,
            skip_duplicates=False, auto_rename=True
        )
        self.assertEqual(stats["moved"], 2)

    def test_category_filter(self):
        self._make("photo.jpg")
        self._make("doc.pdf")
        stats = organize(
            str(self.tmp), preview=False, categories=["Images"]
        )
        self.assertTrue((self.tmp / "Images" / "photo.jpg").exists())
        self.assertFalse((self.tmp / "Documents").exists())
        self.assertEqual(stats["skipped"], 1)

    def test_invalid_directory(self):
        with self.assertRaises(ValueError):
            organize("/nonexistent/path/xyz")

    def test_unknown_extension_goes_to_others(self):
        self._make("weirdfile.xyz123")
        organize(str(self.tmp), preview=False)
        self.assertTrue((self.tmp / "Others" / "weirdfile.xyz123").exists())


class TestFileHash(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_same_content_same_hash(self):
        a = self.tmp / "a.txt"
        b = self.tmp / "b.txt"
        a.write_text("hello")
        b.write_text("hello")
        self.assertEqual(file_hash(a), file_hash(b))

    def test_different_content_different_hash(self):
        a = self.tmp / "a.txt"
        b = self.tmp / "b.txt"
        a.write_text("hello")
        b.write_text("world")
        self.assertNotEqual(file_hash(a), file_hash(b))


if __name__ == "__main__":
    unittest.main(verbosity=2)
