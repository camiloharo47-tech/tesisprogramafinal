class SRSAgent:

    def __init__(self):

        from app.mcp.client import MCPClient

        self.mcp = MCPClient()

    # =====================================================
    # GENERAR SRS
    # =====================================================

    def process(
        self,
        project_id
    ):

        print()
        print("=" * 60)

        print(
            f"Agente 4 → generando SRS "
            f"del proyecto {project_id}..."
        )

        print("=" * 60)


        project = (
            self.mcp.get_project_srs_data(
                project_id
            )
        )


        if not project:

            raise ValueError(
                "El proyecto no existe."
            )


        requirements = project.get(
            "requirements",
            []
        ) or []


        if not requirements:

            raise ValueError(
                "El proyecto no tiene "
                "requisitos funcionales."
            )


        # =================================================
        # RF EXACTOS
        # =================================================

        requirement_texts = [

            (
                f"{item.get('code', '')}: "
                f"{item.get('description', '')}"
            )

            for item in requirements

            if item.get(
                "description"
            )
        ]


        # =================================================
        # CONTEXTO RAG
        # =================================================

        context = project.get("context") or {}
        summary = context.get("summary", "") if context.get("facts") else ""
        rag_contexts = [summary] if summary else []

        print(
            f"Agente 4 → "
            f"{len(requirements)} RF."
        )

        print(
            f"Agente 4 → "
            f"{len(rag_contexts)} "
            "contexto(s) RAG."
        )


        # =================================================
        # MCP SRS
        # =================================================

        general = (
            self.mcp.generate_srs_general(

                project_name=(
                    project.get(
                        "name",
                        ""
                    )
                ),

                project_description=(
                    project.get(
                        "description",
                        ""
                    )
                ),

                requirements=(
                    requirement_texts
                ),

                rag_contexts=(
                    []
                )
            )
        )


        # =================================================
        # CONSTRUIR DOCUMENTO
        # =================================================

        content = self._build_document(
            project,
            requirements,
            general
        )


        # =================================================
        # GUARDAR POR MCP
        # =================================================

        saved = (
            self.mcp.save_srs_document(
                project_id,
                content
            )
        )


        print(
            "Agente 4 → documento "
            f"SRS guardado con ID "
            f"{saved.get('id')}."
        )


        return {
            "document_id":
                saved.get("id"),

            "project_id":
                project_id,

            "content":
                content
        }

    # =====================================================
    # CONSTRUIR IEEE 830
    # =====================================================

    def _build_document(self, project, requirements, general):
        from app.services.srs_guidance_service import SRSGuidanceService
        from app.services.requirement_specification import specification_rows, requirement_name, PENDING

        guidance = SRSGuidanceService().build(project, requirements)
        marker = SRSGuidanceService.MARKER
        lines = [
            "# ESPECIFICACIÓN DE REQUISITOS DE SOFTWARE", "",
            f"## {project.get('name') or 'Proyecto'}", "",
            "Documento organizado según la estructura de IEEE 830-1998 presentada en la guía de referencia.", "",
            "El alcance de la tesis se centra en los requisitos funcionales de la sección 3.2. "
            "Las secciones complementarias contienen orientación general adaptada al proyecto, "
            "pendiente de validación; no constituyen compromisos aprobados ni requisitos extraídos de las entrevistas.", "",
        ]

        def section(title, body, level=2, supplementary=True):
            lines.extend(["#" * level + " " + title, ""])
            if supplementary:
                lines.extend([marker, ""])
            lines.extend([body, ""])

        def general_or_guidance(key):
            text = str(general.get(key) or "").strip()
            if not text or "no especificad" in text.lower():
                return guidance[key]
            # Add editorial guidance even when the model provides project facts.
            return text + " " + guidance[key]

        section("1. Introducción", "Presentación y organización de la especificación del proyecto.", 1)
        section("1.1 Propósito", guidance["purpose"])
        section("1.2 Ámbito del sistema", general_or_guidance("scope"))
        section("1.3 Definiciones, acrónimos y abreviaturas", "\n".join([
            "- ERS: Especificación de Requisitos de Software.",
            "- SRS: Software Requirements Specification, equivalente a ERS.",
            "- RF: Requisito funcional identificado a partir de una entrevista.",
            "- Actor: usuario o sistema que interviene en una función identificada.",
            "- RAG: recuperación de información académica para apoyar el contexto del proyecto.",
            "- MCP: protocolo utilizado por el prototipo para acceder a sus herramientas.",
            "- API: interfaz de programación para el intercambio entre aplicaciones, si se acuerda una integración.",
        ]))
        references = [
            "- IEEE Std. 830-1998: referencia de organización del documento.",
            "- Especificación de Requisitos según el estándar de IEEE 830, guía en castellano del 22 de octubre de 2008 proporcionada como referencia.",
            "- Entrevistas del proyecto: evidencia de los RF reproducida en la sección 4.1.",
        ]
        references += [f"- {source['title']}: {source['url']}" for source in self._sources(project)]
        section("1.4 Referencias", "\n".join(references))
        section("1.5 Visión general del documento", "La sección 2 presenta el contexto del producto; la sección 3.2 detalla los RF. "
                "Las otras subsecciones ofrecen orientación complementaria. Los apéndices conservan la trazabilidad y el contexto académico del proyecto.")
        section("2. Descripción general", "Contexto del sistema y consideraciones orientativas para su desarrollo.", 1)
        section("2.1 Perspectiva del producto", general_or_guidance("product_perspective"))
        section("2.2 Funciones del producto", "Resumen de las funciones identificadas, sin añadir funciones nuevas:\n\n" + "\n".join(
            f"- {item.get('code', 'RF')}: {item.get('description', '')}" for item in requirements))
        section("2.3 Características de los usuarios", guidance["users"])
        section("2.4 Restricciones", guidance["constraints"])
        section("2.5 Suposiciones y dependencias", guidance["assumptions"])
        section("2.6 Requisitos futuros", guidance["future"])
        section("3. Requisitos específicos", "Los RF se documentan en la sección 3.2. Las demás subsecciones son propuestas orientativas pendientes de validación.", 1, False)
        section("3.1 Interfaces externas", guidance["interfaces"])
        for title, key in [
            ("3.1.1 Interfaz de usuario", "user_interface"),
            ("3.1.2 Interfaces de hardware", "hardware_interface"),
            ("3.1.3 Interfaces de software", "software_interface"),
            ("3.1.4 Interfaces de comunicaciones", "communications"),
        ]:
            section(title, guidance[key], 3)
        section("3.2 Requisitos funcionales", "Los RF se organizan mediante una ficha adaptada de identificación, comportamiento y criterios de aceptación. "
                "La estructura del documento permanece basada en IEEE 830-1998; la ficha no es una plantilla literal ni una declaración de cumplimiento de ISO/IEC/IEEE 29148. "
                "Los campos sin evidencia quedan pendientes de aclaración y los detalles se reproducen literalmente de la entrevista.", supplementary=False)
        interviews = {item.get("id"): item.get("transcription") or "" for item in project.get("interviews", [])}
        for item in requirements:
            lines += [
                f"### {item.get('code', 'RF')}", "",
                "**Nombre:** " + requirement_name(item.get("description")), "",
                "**Origen:** Entrevista " + str(item.get("interview_id", PENDING)), "",
                "**Enunciado:** " + item.get("description", PENDING), "",
                "**Actor:** " + (item.get("actor") or PENDING), "",
                "**Prioridad:** " + self._priority(item.get("priority")), "",
            ]
            rows = specification_rows(item.get("specification"), interviews.get(item.get("interview_id")) or item.get("source_excerpt") or "", item)
            for row in rows:
                if row["key"] == "acceptance_criteria":
                    continue
                lines += [f"**{row['label']}:**", ""]
                lines += ["- " + quote for quote in row["values"]] or [PENDING]
                lines.append("")
            criteria = next(row["values"] for row in rows if row["key"] == "acceptance_criteria")
            lines += ["**Criterios de aceptación:**", ""]
            lines += [f"- {item.get('code', 'RF')}-CA-{i:02d}: {quote}" for i, quote in enumerate(criteria, 1)] or [PENDING]
            lines += ["", "---", ""]
        section("3.3 Requisitos de rendimiento", guidance["performance"])
        section("3.4 Restricciones de diseño", guidance["design"])
        section("3.5 Atributos del sistema", guidance["quality"] + "\n\n" + "\n".join(
            "- " + guidance[key] for key in ("reliability", "availability", "security", "maintainability", "portability")))
        section("3.6 Otros requisitos", guidance["other"])
        section("4. Apéndices", "Material de apoyo: trazabilidad de los RF, antecedentes académicos y orientación para documentación adicional.", 1, False)
        section("4.1 Trazabilidad de requisitos", "Los siguientes fragmentos conservan la evidencia original de las entrevistas.", supplementary=False)
        for item in requirements:
            lines += [f"### {item.get('code', 'RF')}", "", "> " + (item.get("source_excerpt") or "No especificada."), ""]
            lines += ["**Razón de la prioridad:** " + (item.get("priority_reason") or PENDING), "",
                      "**Ambigüedad (análisis automático):** " + ("Detectada" if item.get("ambiguity_detected") else "No detectada"), "",
                      "**Verificabilidad (análisis automático):** " + ("Verificable" if item.get("verifiable") else "Requiere aclaración"), ""]
        context = project.get("context") or {}
        section("4.2 Contexto académico del proyecto", "Antecedentes académicos; no representan requisitos del cliente.\n\n" + (
            context.get("summary") or "El contexto académico todavía no se ha generado. Puede obtenerse desde la pantalla de requisitos funcionales."
        ), supplementary=False)
        for fact in context.get("facts", []):
            lines += [f"- Evidencia [fuente {fact.get('source')}]: {fact.get('evidence', '')}", ""]
        for index, source in enumerate(context.get("sources", []), 1):
            lines += [f"- Fuente {index}: {source.get('title', '')}. {source.get('url', '')}", ""]
        section("4.3 Documentación complementaria sugerida", guidance["appendices"])
        return "\n".join(lines)

    def _sources(self, project):
        result, seen = [], set()
        for source in (project.get("context") or {}).get("sources", []):
            url = source.get("url", "")
            if url and url not in seen:
                seen.add(url)
                result.append({"title": source.get("title", "Fuente académica"), "url": url})
        return result

    def _priority(
        self,
        priority
    ):

        labels = {
            "esencial": "Esencial",
            "condicional": "Condicional",
            "opcional": "Opcional",
            "no_especificada": "No especificada"
        }


        return labels.get(
            str(
                priority
                or
                "no_especificada"
            ).lower(),
            "No especificada"
        )
