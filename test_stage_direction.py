"""Test _clean_text() end-to-end using run_v7 module."""
import unittest
from pipeline.run_v7 import _clean_text

class TestStageDirection(unittest.TestCase):
    def test_clean_text_leading_paren(self):
        c, s = _clean_text("(quietly) We do, Sarah.", "en-US-BrianNeural")
        self.assertEqual(c, "We do, Sarah.")
        self.assertIn('volume="-6dB"', s)
        self.assertIn('rate="-5%"', s)
        self.assertIn("We do, Sarah.", s)

    def test_clean_text_trailing_paren(self):
        c, s = _clean_text("We do, Sarah. (whisper)", "en-US-BrianNeural")
        self.assertEqual(c, "We do, Sarah.")
        self.assertIn('volume="-12dB"', s)
        self.assertIn('rate="-10%"', s)

    def test_clean_text_mid_paren(self):
        c, s = _clean_text("We do (laughing) now, Sarah.", "en-US-BrianNeural")
        self.assertEqual(c, "We do now, Sarah.")
        self.assertIn('volume="0dB"', s)

if __name__ == "__main__":
    unittest.main()
