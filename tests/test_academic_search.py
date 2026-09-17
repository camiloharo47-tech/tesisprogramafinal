import os
import unittest
from unittest.mock import Mock, patch

import requests

from app.services.academic_search_service import AcademicSearchService
from app.rag.retriever import RAGRetriever
from app.agents.enrichment_agent import EnrichmentAgent
from jinja2 import Environment, FileSystemLoader


def paper(**changes):
    item = {"title": "Library management system", "url": "https://doi.org/10.1/example",
            "doi": "10.1/example", "snippet": "The library management system supports circulation.",
            "provider": "Crossref", "evidence_type": "abstract", "authors": ["Author"], "year": "2024"}
    return dict(item, **changes)


class AcademicSearchTests(unittest.TestCase):
    def setUp(self):
        self.retriever = RAGRetriever()

    def test_system_domain_is_enough_and_general_web_is_rejected(self):
        results = self.retriever._filter_sources(
            [paper(), paper(provider="Web", doi="other"),
             paper(title="Hospital management system", snippet="Patient software", doi="hospital")],
            ["biblioteca"], ["reservar", "libros"])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["doi"], "10.1/example")

    def test_metadata_is_reference_but_never_evidence(self):
        data = [paper(snippet="", evidence_type="metadata_only")]
        self.assertEqual(self.retriever._filter_sources(data, ["biblioteca"], []), [])
        self.assertEqual(len(self.retriever._filter_sources(data, ["biblioteca"], [], False)), 1)

    def test_queries_cover_requirement_and_system_without_web_fallback(self):
        self.retriever.mcp = Mock()
        self.retriever.mcp.search_academic.return_value = {"results": [paper()], "providers": ["Crossref"]}
        result = self.retriever.retrieve("El sistema debe reservar libros", interview_context="Necesitamos un sistema de biblioteca.")
        self.assertIn("library management system", result["queries"])
        self.assertTrue(any("reservar" in q for q in result["queries"]))
        self.assertEqual(len(result["sources"]), 1)
        self.retriever.mcp.search_web.assert_not_called()

    @patch.dict(os.environ, {}, clear=True)
    def test_crossref_metadata_and_document_types(self):
        session = Mock()
        session.get.return_value.json.return_value = {"message": {"items": [
            {"type": "journal-article", "title": ["Library system"], "DOI": "10.1/a",
             "abstract": "<jats:p>Library &amp; books.</jats:p>", "author": [{"family": "Doe"}],
             "published": {"date-parts": [[2024]]}},
            {"type": "book", "title": ["Book"], "DOI": "10.1/b"}]}}
        result = AcademicSearchService(session).search("library system")
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["snippet"], "Library & books.")
        self.assertEqual(result["results"][0]["year"], "2024")
        self.assertEqual(result["providers"], ["Crossref"])
        self.assertEqual(result["warnings"], [])

    @patch.dict(os.environ, {}, clear=True)
    def test_network_failure_is_visible(self):
        session = Mock()
        session.get.side_effect = requests.Timeout("secret details")
        result = AcademicSearchService(session).search("library")
        self.assertEqual(result["results"], [])
        self.assertEqual(result["providers"], [])
        self.assertIn("Crossref", " ".join(result["warnings"]))
        self.assertNotIn("secret", str(result))

    def test_agent_preserves_metadata_when_no_abstract_is_available(self):
        agent = EnrichmentAgent()
        agent.retriever = Mock()
        agent.mcp = Mock()
        agent.ollama = Mock()
        agent.retriever.retrieve_project.return_value = {
            "query": "library", "sources": [], "references": [paper(snippet="")],
            "providers": ["Crossref"], "warnings": [],
            "scholar_url": "https://scholar.google.com/scholar?q=library"}
        agent.mcp.get_project_srs_data.return_value = {"requirements": [{"id": 1, "description": "Reservar libros"}]}
        agent.mcp.save_project_context.return_value = {"saved": True}
        result = agent.process_project(1)
        self.assertEqual(result["context"]["search_kind"], "academic")
        self.assertEqual(result["context"]["facts"], [])
        self.assertTrue(result["context"]["references"])
        agent.ollama.generate_json.assert_not_called()
        agent.mcp.save_project_context.assert_called_once()

    def test_template_compiles(self):
        Environment(loader=FileSystemLoader("app/templates")).get_template("requirements.html")

    def test_successful_enrichment_keeps_citation_metadata(self):
        agent = EnrichmentAgent()
        agent.retriever = Mock()
        agent.mcp = Mock()
        agent.ollama = Mock()
        agent.retriever.retrieve_project.return_value = {"query": "library", "sources": [paper()], "providers": ["Crossref"]}
        agent.ollama.generate_json.return_value = {"useful_context": False, "facts": []}
        agent.mcp.get_project_srs_data.return_value = {"requirements": [{"id": 1, "description": "Reservar libros"}]}
        agent.mcp.save_project_context.return_value = {"saved": True}
        result = agent.process_project(1)
        source = result["context"]["sources"][0]
        self.assertEqual(source["authors"], ["Author"])
        self.assertEqual(source["doi"], "10.1/example")
        self.assertEqual(result["context"]["providers"], ["Crossref"])


if __name__ == "__main__":
    unittest.main()


