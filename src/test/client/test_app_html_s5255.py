"""HTML accessibility unit tests for Web:S5255 in app.html (Issue #184)."""

from html.parser import HTMLParser
from pathlib import Path
import unittest


APP_HTML_PATH = (
    Path(__file__).resolve().parents[2]
    / "main"
    / "client"
    / "templates"
    / "app.html"
)


class _AsideAriaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.asides = {}

    def handle_starttag(self, tag, attrs):
        if tag == "aside":
            attr_dict = dict(attrs)
            self.asides[attr_dict.get("id")] = attr_dict


class TestAppHtmlAsideAriaLabelsS5255(unittest.TestCase):
    """Checks that the 4 <aside> containers in app.html have descriptive aria-label attributes."""

    def test_every_aside_element_has_an_aria_label(self):
        parser = _AsideAriaParser()
        parser.feed(APP_HTML_PATH.read_text(encoding="utf-8"))

        expected_ids = (
            "sidebar",
            "dashboard-progress",
            "profile-summary",
            "opportunity-detail",
        )
        for aside_id in expected_ids:
            with self.subTest(aside_id=aside_id):
                self.assertIn(aside_id, parser.asides)
                aria_label = (parser.asides[aside_id].get("aria-label") or "").strip()
                self.assertTrue(
                    bool(aria_label),
                    f"El elemento <aside id='{aside_id}'> debe poseer un aria-label no vacío",
                )


if __name__ == "__main__":
    unittest.main()
