import json
import re
import unicodedata

from difflib import SequenceMatcher

from app.mcp.client import (
    MCPClient
)

from app.rag.retriever import (
    RAGRetriever
)

from app.rag.context_builder import (
    ContextBuilder
)

from app.services.ollama_service import (
    OllamaService
)


class EnrichmentAgent:

    # =====================================================
    # ESQUEMA
    # =====================================================

    ENRICHMENT_SCHEMA = {
        "type": "object",
        "properties": {
            "useful_context": {
                "type": "boolean"
            },
            "facts": {
                "type": "array",
                "maxItems": 5,
                "items": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string"
                        },
                        "source": {
                            "type": "integer"
                        },
                        "evidence": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "text",
                        "source",
                        "evidence"
                    ],
                    "additionalProperties": False
                }
            }
        },
        "required": [
            "useful_context",
            "facts"
        ],
        "additionalProperties": False
    }


    # =====================================================
    # INICIALIZACIÓN
    # =====================================================

    def __init__(self):

        self.mcp = MCPClient()

        self.retriever = (
            RAGRetriever()
        )

        self.context_builder = (
            ContextBuilder()
        )

        self.ollama = OllamaService(
            model_name="llama3.2:3b"
        )


    # =====================================================
    # PROCESAR ENTREVISTA
    # =====================================================

    def process_interview(self, interview_id):
        """Compatibility entry point: enrich the whole project once."""
        interview = self.mcp.get_interview(interview_id).get("interview")
        if not interview:
            raise ValueError("La entrevista no existe.")
        return [self.process_project(interview["project_id"])]

    def process_project(self, project_id):
        project = self.mcp.get_project_srs_data(project_id)
        if not project:
            raise ValueError("El proyecto no existe.")
        requirements = project.get("requirements") or []
        if not requirements:
            raise ValueError("El proyecto no tiene requisitos funcionales.")
        retrieved = self.retriever.retrieve_project(project, max_results=10)
        sources = retrieved.get("sources") or []
        context = {
            "scope": "project", "search_kind": "academic",
            "query": retrieved.get("query", ""),
            "providers": retrieved.get("providers", []),
            "warnings": retrieved.get("warnings", []),
            "scholar_url": retrieved.get("scholar_url", ""),
            "references": retrieved.get("references", []),
            "sources": self._prepare_sources(sources), "facts": [],
            "requirement_count": len(requirements),
            "summary": "No se encontraron fuentes académicas con resumen disponible relacionadas con el proyecto.",
        }
        if sources:
            prompt = self.context_builder.build_project_prompt(project, context["query"], sources)
            try:
                result = self.ollama.generate_json(prompt, self.ENRICHMENT_SCHEMA)
            except Exception:
                context["summary"] = "Se recuperaron artículos, pero no fue posible generar la síntesis del proyecto."
                context["warnings"].append("No se pudo generar la síntesis con el modelo local.")
            else:
                facts = result.get("facts", []) if result.get("useful_context") else []
                for fact in facts[:5]:
                    if not isinstance(fact, dict):
                        continue
                    # Do not present an existing RF as an academic fact.
                    if any(SequenceMatcher(None, self._normalize(fact.get("text", "")),
                                           self._normalize(r["description"])).ratio() >= 0.93
                           for r in requirements):
                        continue
                    validated = self._validate_fact(fact, "", sources, context["facts"])
                    if validated:
                        context["facts"].append(validated)
                context["summary"] = " ".join(f["text"] for f in context["facts"]) or (
                    "Se recuperaron artículos relacionados con el proyecto, pero no se obtuvo una síntesis suficientemente respaldada."
                )
        saved = self.mcp.save_project_context(project_id, json.dumps(context, ensure_ascii=False))
        if not saved.get("saved"):
            raise RuntimeError("No fue posible guardar el contexto del proyecto.")
        return {"project_id": project_id, "context": context}

    def _prepare_sources(
        self,
        sources
    ):

        fields = ("title", "url", "snippet", "authors", "year", "doi",
                  "venue", "provider", "document_type", "evidence_type")
        return [{key: source[key] for key in fields if key in source}
                for source in sources[:5]]


    # =====================================================
    # GUARDAR
    # =====================================================

    def _validate_fact(
        self,
        fact,
        requirement,
        sources,
        current
    ):

        if not isinstance(
            fact,
            dict
        ):

            return None


        text = str(
            fact.get(
                "text",
                ""
            )
            or ""
        ).strip()


        evidence = str(
            fact.get(
                "evidence",
                ""
            )
            or ""
        ).strip()


        try:

            source_index = int(
                fact.get(
                    "source"
                )
            )

        except (
            ValueError,
            TypeError
        ):

            return None


        if (
            not text
            or not evidence
        ):

            return None


        if (
            source_index < 1
            or source_index > len(
                sources
            )
        ):

            return None


        normalized_text = (
            self._normalize(
                text
            )
        )


        # =================================================
        # NO GENERAR NUEVOS RF
        # =================================================

        forbidden = (
            "el sistema debe",
            "el sistema debera",
            "debe permitir",
            "debera permitir",
            "el sistema deberia",
            "el sistema podria"
        )


        if any(
            phrase in normalized_text
            for phrase in forbidden
        ):

            print(
                "Agente 3 → hecho descartado: "
                "parece un requisito nuevo."
            )

            return None


        # =================================================
        # NO COPIAR RF
        # =================================================

        similarity = SequenceMatcher(

            None,

            normalized_text,

            self._normalize(
                requirement
            )

        ).ratio()


        if similarity >= 0.93:

            print(
                "Agente 3 → hecho descartado: "
                "es prácticamente una copia del RF."
            )

            return None


        # =================================================
        # EVIDENCIA
        # =================================================

        source = sources[
            source_index - 1
        ]


        snippet = str(
            source.get(
                "snippet",
                ""
            )
            or ""
        ).strip()


        if not self._evidence_matches(
            evidence,
            snippet
        ):

            print(
                "Agente 3 → hecho descartado: "
                "la evidencia no está suficientemente "
                "respaldada por la fuente."
            )

            return None


        # =================================================
        # DUPLICADOS
        # =================================================

        for current_fact in current:

            ratio = SequenceMatcher(

                None,

                normalized_text,

                self._normalize(
                    current_fact["text"]
                )

            ).ratio()


            if ratio >= 0.90:

                return None


        return {
            "text":
                text,

            "source":
                source_index,

            "evidence":
                evidence
        }


    # =====================================================
    # VALIDAR EVIDENCIA
    # =====================================================

    def _evidence_matches(
        self,
        evidence,
        snippet
    ):

        normalized_evidence = (
            self._normalize(
                evidence
            )
        )


        normalized_snippet = (
            self._normalize(
                snippet
            )
        )


        if (
            normalized_evidence
            in normalized_snippet
        ):

            return True


        evidence_words = set(
            self._keywords(
                evidence
            )
        )


        snippet_words = set(
            self._keywords(
                snippet
            )
        )


        if not evidence_words:

            return False


        common = (
            evidence_words
            & snippet_words
        )


        ratio = (
            len(common)
            /
            len(evidence_words)
        )


        minimum_words = min(
            3,
            len(evidence_words)
        )


        return (
            len(common) >= minimum_words
            and ratio >= 0.60
        )


    # =====================================================
    # KEYWORDS
    # =====================================================

    def _keywords(
        self,
        text
    ):

        normalized = (
            self._normalize(
                text
            )
        )


        return [
            word
            for word in re.findall(
                r"[a-z0-9]+",
                normalized
            )
            if len(word) >= 4
        ]


    # =====================================================
    # NORMALIZAR
    # =====================================================

    def _normalize(
        self,
        text
    ):

        text = str(
            text
            or ""
        ).lower()


        text = unicodedata.normalize(
            "NFD",
            text
        )


        text = "".join(
            character
            for character in text
            if unicodedata.category(
                character
            ) != "Mn"
        )


        text = re.sub(
            r"\s+",
            " ",
            text
        )


        return text.strip()
