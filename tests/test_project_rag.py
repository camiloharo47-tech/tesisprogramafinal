import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from app import create_app, db
from app.models import Project, Interview, Requirement, ProjectContext
from app.agents.enrichment_agent import EnrichmentAgent
from app.agents.srs_agent import SRSAgent
from app.mcp.servers import database_server


class ProjectRAGTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.database = root / "test.db"
        self.app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///" + str(self.database),
                               "UPLOAD_FOLDER": str(root / "uploads"), "GENERATED_FOLDER": str(root / "generated")})
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.session.add_all([Project(id=1, name="Biblioteca", description="Sistema de biblioteca"),
                            Project(id=2, name="Otro proyecto")])
        db.session.add_all([Interview(id=1, project_id=1, transcription="Gestionar libros"),
                            Interview(id=2, project_id=1, transcription="Reservar libros"),
                            Interview(id=3, project_id=2, transcription="Datos ajenos")])
        db.session.add_all([Requirement(id=1, project_id=1, interview_id=1, code="RF01", description="Registrar libros", source_excerpt="Registrar libros", enriched_context='{"summary":"LEGACY"}'),
                            Requirement(id=2, project_id=1, interview_id=2, code="RF02", description="Reservar libros", source_excerpt="Reservar libros"),
                            Requirement(id=3, project_id=2, interview_id=3, code="RF01", description="Ajeno", source_excerpt="Ajeno")])
        db.session.commit()
        self.path_patch = patch.object(database_server, "DATABASE_PATH", self.database)
        self.path_patch.start()

    def tearDown(self):
        db.session.remove()
        db.engine.dispose()
        self.ctx.pop()
        self.path_patch.stop()
        self.temp.cleanup()

    def test_persistence_is_one_per_project_and_includes_all_interviews(self):
        payload = {"scope": "project", "summary": "FIRST", "sources": [], "facts": []}
        database_server.save_project_context(1, json.dumps(payload))
        payload["summary"] = "UPDATED"
        database_server.save_project_context(1, json.dumps(payload))
        project = database_server.get_project_srs_data(1)["project"]
        self.assertEqual(len(project["requirements"]), 2)
        self.assertEqual([i["id"] for i in project["interviews"]], [1, 2])
        self.assertEqual(project["context"]["summary"], "UPDATED")
        self.assertEqual(ProjectContext.query.count(), 1)
        self.assertEqual(database_server.get_project_srs_data(2)["project"]["context"], {})

    def test_one_retrieval_and_one_synthesis_for_two_interviews(self):
        project = database_server.get_project_srs_data(1)["project"]
        agent = EnrichmentAgent()
        agent.mcp = Mock()
        agent.mcp.get_project_srs_data.return_value = project
        agent.mcp.save_project_context.return_value = {"saved": True}
        agent.retriever = Mock()
        agent.retriever.retrieve_project.return_value = {"query": "library", "sources": [
            {"title": "Study", "url": "https://example.org/paper", "snippet": "Library systems support circulation."}]}
        agent.ollama = Mock()
        agent.ollama.generate_json.return_value = {"useful_context": True, "facts": [
            {"text": "Los sistemas bibliotecarios apoyan la circulación.", "source": 1, "evidence": "Library systems support circulation."}]}
        result = agent.process_project(1)
        agent.retriever.retrieve_project.assert_called_once_with(project, max_results=10)
        agent.ollama.generate_json.assert_called_once()
        prompt = agent.ollama.generate_json.call_args.args[0]
        self.assertIn("Registrar libros", prompt)
        self.assertIn("Reservar libros", prompt)
        self.assertNotIn("Ajeno", prompt)
        self.assertEqual(result["context"]["requirement_count"], 2)
        self.assertEqual(len(result["context"]["facts"]), 1)
        agent.mcp.save_project_context.assert_called_once()
        agent.mcp.save_enriched_context.assert_not_called()

    def test_srs_has_one_context_and_preserves_requirement_evidence(self):
        project = database_server.get_project_srs_data(1)["project"]
        project["context"] = {"scope": "project", "summary": "UNIQUE SYNTHESIS", "sources": [], "facts": []}
        content = SRSAgent()._build_document(project, project["requirements"], {})
        self.assertEqual(content.count("UNIQUE SYNTHESIS"), 1)
        self.assertEqual(content.count("## 4.2 Contexto académico del proyecto"), 1)
        self.assertNotIn("LEGACY", content)
        self.assertIn("> Registrar libros", content)
        self.assertIn("> Reservar libros", content)

    def test_pages_and_project_action(self):
        database_server.save_project_context(1, json.dumps({"scope": "project", "summary": "UNIQUE SYNTHESIS"}))
        client = self.app.test_client()
        page = client.get("/projects/1").get_data(as_text=True)
        self.assertNotIn("UNIQUE SYNTHESIS", page)
        page = client.get("/interviews/1/requirements").get_data(as_text=True)
        self.assertNotIn("LEGACY", page)
        self.assertEqual(page.count("UNIQUE SYNTHESIS"), 1)
        self.assertIn('href="#project-context"', page)
        self.assertIn('/interviews/1/enrich', page)
        with patch("app.routes.EnrichmentAgent") as agent:
            response = client.post("/projects/1/enrich")
            self.assertEqual(response.status_code, 302)
            agent.return_value.process_project.assert_called_once_with(1)
        with patch("app.routes.EnrichmentAgent") as agent:
            response = client.post("/interviews/1/enrich")
            self.assertEqual(response.location, "/interviews/1/requirements#project-context")
            agent.return_value.process_project.assert_called_once_with(1)
        response = client.post("/projects/1/delete")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ProjectContext.query.count(), 0)
        self.assertIsNotNone(db.session.get(Project, 2))

    def test_project_without_requirements_cannot_generate_context(self):
        agent = EnrichmentAgent()
        agent.mcp = Mock()
        agent.mcp.get_project_srs_data.return_value = {"requirements": []}
        with self.assertRaises(ValueError):
            agent.process_project(1)
        agent.mcp.save_project_context.assert_not_called()


if __name__ == "__main__":
    unittest.main()
