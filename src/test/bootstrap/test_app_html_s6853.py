"""Pruebas unitarias de accesibilidad HTML para Web:S6853 en app.html (Issue #183)."""

from html.parser import HTMLParser
from pathlib import Path
import unittest


APP_HTML_PATH = (
    Path(__file__).resolve().parents[2]
    / "main"
    / "bootstrap"
    / "templates"
    / "app.html"
)


class _LabelInputParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.labels = []
        self.input_ids = set()

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        if tag == "label":
            self.labels.append(attr_dict)
        elif tag in ("input", "select", "textarea") and "id" in attr_dict:
            self.input_ids.add(attr_dict["id"])


class TestAppHtmlLabelAssociationS6853(unittest.TestCase):
    """Verifica que la etiqueta label.search-field esté explícitamente asociada con for='opportunity-search'."""

    def test_search_field_label_tiene_atributo_for_asociado_al_input(self):
        parser = _LabelInputParser()
        parser.feed(APP_HTML_PATH.read_text(encoding="utf-8"))

        search_labels = [
            lbl for lbl in parser.labels if lbl.get("class") == "search-field"
        ]
        self.assertEqual(len(search_labels), 1)
        self.assertEqual(search_labels[0].get("for"), "opportunity-search")
        self.assertIn("opportunity-search", parser.input_ids)


if __name__ == "__main__":
    unittest.main()
