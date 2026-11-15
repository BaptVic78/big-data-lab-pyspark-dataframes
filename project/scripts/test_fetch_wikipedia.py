"""Offline checks for exact identifier matching and source extraction."""
import tempfile
import unittest
from pathlib import Path

from fetch_wikipedia import (fetch_one, has_imdb_id, plot_text, request_rows,
                             retry_delay)


class FakeClient:
    def __init__(self, imdb="tt1375666", extract=None):
        self.imdb = imdb
        self.extract = extract or "Introduction\n\n== Plot ==\nSource plot.\n\n== Cast ==\nNames"

    def get(self, endpoint, params):
        if params.get("list") == "search":
            return {"query": {"search": [{"pageid": 123}]}}
        if params.get("prop") == "pageprops":
            return {"query": {"pages": [{"pageid": 123,
                                         "pageprops": {"wikibase_item": "Q1"}}]}}
        if params.get("action") == "wbgetentities":
            return {"entities": {"Q1": {"claims": {"P345": [
                {"mainsnak": {"datavalue": {"value": self.imdb}}}]}}}}
        return {"query": {"pages": [{"pageid": 123, "extract": self.extract,
                                     "fullurl": "https://en.wikipedia.org/wiki/Example",
                                     "revisions": [{"revid": 456}]}]}}


class FetchTests(unittest.TestCase):
    def test_exact_match_and_plot(self):
        row = {"entity_id": "tt1375666", "kind": "film", "label": "Inception", "year": "2010"}
        result = fetch_one(row, FakeClient())
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["text"].strip(), "Source plot.")
        self.assertEqual(result["revision_id"], "456")
        self.assertIn("oldid=456", result["revision_url"])
        self.assertEqual(fetch_one(row, FakeClient(imdb="tt0000001"))["status"],
                         "no_verified_match")

    def test_missing_plot_is_not_a_synopsis(self):
        row = {"entity_id": "tt1375666", "kind": "film", "label": "Inception"}
        result = fetch_one(row, FakeClient(extract="Only an introduction."))
        self.assertEqual(result["status"], "missing_plot")
        self.assertIsNone(result["text"])

    def test_biography_introduction(self):
        row = {"entity_id": "nm0000138", "kind": "person", "label": "Example"}
        result = fetch_one(row, FakeClient(imdb="nm0000138"))
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["text"].strip(), "Introduction")

    def test_deprecated_identifier(self):
        entity = {"claims": {"P345": [{"rank": "deprecated",
                    "mainsnak": {"datavalue": {"value": "tt1"}}}]}}
        self.assertFalse(has_imdb_id(entity, "tt1"))
        self.assertFalse(has_imdb_id({}, "tt1"))

    def test_retry_delay(self):
        self.assertEqual(retry_delay("30", 1), 30)
        self.assertEqual(retry_delay("invalid", 2), 4)
        self.assertEqual(retry_delay("Sun, 06 Nov 1994 08:49:37 GMT", 2), 4)

    def test_sections_and_csv_deduplication(self):
        text, section = plot_text("Lead\n== Synopsis ==\nA\n=== Part 1 ===\nB\n== Reception ==\nC")
        self.assertEqual(section, "Synopsis")
        self.assertIn("Part 1", text)
        self.assertNotIn("Reception", text)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "requests.csv"
            path.write_text("entity_id,kind,label,year\ntt1,film,A,2000\ntt1,film,A,2000\n",
                            encoding="utf-8")
            self.assertEqual(len(list(request_rows(path))), 1)


if __name__ == "__main__":
    unittest.main()
