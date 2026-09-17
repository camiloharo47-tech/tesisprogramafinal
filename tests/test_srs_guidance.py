import copy
import re
import unittest

from app.agents.srs_agent import SRSAgent
from app.services.srs_guidance_service import SRSGuidanceService
from app.services.document_service import DocumentService
from docx import Document


class SRSGuidanceTests(unittest.TestCase):
    def setUp(self):
        self.requirements = [{"code": "RF01", "description": "El sistema debe registrar préstamos de libros.",
                              "actor": "Bibliotecario", "source_excerpt": "Necesito registrar préstamos.",
                              "priority": "esencial", "verifiable": True, "ambiguity_detected": False}]
        self.project = {"name": "Biblioteca Central", "description": "Gestión de préstamos bibliotecarios"}
        self.agent = SRSAgent()

    def test_all_supplementary_sections_are_filled_and_labelled(self):
        content = self.agent._build_document(self.project, self.requirements, {})
        sections = dict(re.findall(r"^## ([0-9.]+) [^\n]+\n(.*?)(?=^## |\Z)", content, re.M | re.S))
        for number in ("1.1", "1.2", "1.3", "1.4", "1.5", "2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "3.1", "3.3", "3.4", "3.5", "3.6", "4.3"):
            with self.subTest(section=number):
                self.assertIn(SRSGuidanceService.MARKER, sections[number])
                self.assertGreater(len(sections[number].replace(SRSGuidanceService.MARKER, "").strip()), 50)
                self.assertNotIn("No especificado en la entrevista", sections[number])
        self.assertNotIn(SRSGuidanceService.MARKER, sections["3.2"])

    def test_project_specific_text_and_original_requirements_are_preserved(self):
        original = copy.deepcopy(self.requirements)
        content = self.agent._build_document(self.project, self.requirements, {})
        rf_section = content.split("## 3.2 Requisitos funcionales", 1)[1].split("## 3.3", 1)[0]
        self.assertIn(self.requirements[0]["description"], rf_section)
        self.assertIn("**Actor:** Bibliotecario", rf_section)
        self.assertIn("> Necesito registrar préstamos.", content)
        self.assertEqual(self.requirements, original)
        other = self.agent._build_document({"name": "Clínica", "description": "Gestión de citas"}, [], {})
        self.assertIn("Para Clínica", other)
        self.assertNotIn("Biblioteca Central", other)
        self.assertNotIn("Bibliotecario", other)

    def test_missing_model_fields_use_guidance(self):
        content = self.agent._build_document(self.project, self.requirements, {
            "scope": "No especificado en la entrevista.", "product_perspective": ""})
        self.assertNotIn("No especificado en la entrevista.", content)
        self.assertIn("2.6 Requisitos futuros", content)
        self.assertIn("pendiente de validación", content)

    def test_word_export_preserves_scope_markers_and_rf(self):
        content = self.agent._build_document(self.project, self.requirements, {})
        document = Document(DocumentService().create_docx(content))
        text = "\n".join(p.text for p in document.paragraphs)
        self.assertEqual(text.count(SRSGuidanceService.MARKER), content.count(SRSGuidanceService.MARKER))
        self.assertIn("2.6 Requisitos futuros", text)
        self.assertIn(self.requirements[0]["description"], text)


if __name__ == "__main__":
    unittest.main()
