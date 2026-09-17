from app import db
from app.models import Interview

from app.agents.transcription_agent import (
    TranscriptionAgent
)

from app.agents.requirements_agent import (
    RequirementsAgent
)

from app.agents.enrichment_agent import (
    EnrichmentAgent
)

from app.agents.srs_agent import (
    SRSAgent
)


class Orchestrator:

    def __init__(self):

        self.transcription_agent = (
            TranscriptionAgent()
        )

        self.requirements_agent = (
            RequirementsAgent()
        )

        self.enrichment_agent = (
            EnrichmentAgent()
        )

        self.srs_agent = (
            SRSAgent()
        )

    # =====================================================
    # PROCESAR ENTREVISTA COMPLETA
    # =====================================================

    def process_interview(
        self,
        interview_id
    ):

        interview = db.session.get(
            Interview,
            interview_id
        )

        if not interview:

            raise ValueError(
                "La entrevista no existe."
            )

        project_id = (
            interview.project_id
        )

        print()
        print("=" * 60)

        print(
            "ORQUESTADOR → INICIO"
        )

        print(
            f"Entrevista: {interview_id}"
        )

        print(
            f"Proyecto: {project_id}"
        )

        print("=" * 60)

        # =================================================
        # AGENTE 1
        # =================================================

        print()
        print(
            "ORQUESTADOR → "
            "Agente 1: Transcripción"
        )

        self.transcription_agent.process(
            interview_id
        )

        print(
            "ORQUESTADOR → "
            "Agente 1 completado."
        )

        # =================================================
        # AGENTE 2
        # =================================================

        print()
        print(
            "ORQUESTADOR → "
            "Agente 2: Requisitos"
        )

        requirements = (
            self.requirements_agent.process(
                interview_id
            )
        )

        print(
            "ORQUESTADOR → "
            "Agente 2 completado."
        )

        # =================================================
        # AGENTE 3
        # =================================================

        print()
        print(
            "ORQUESTADOR → "
            "Agente 3: RAG"
        )

        enrichment = (
            self.enrichment_agent
            .process_project(
                project_id
            )
        )

        print(
            "ORQUESTADOR → "
            "Agente 3 completado."
        )

        # =================================================
        # AGENTE 4
        # =================================================

        print()
        print(
            "ORQUESTADOR → "
            "Agente 4: SRS"
        )

        srs_result = (
            self.srs_agent.process(
                project_id
            )
        )

        print(
            "ORQUESTADOR → "
            "Agente 4 completado."
        )

        # =================================================
        # RECUPERAR ID DEL DOCUMENTO
        # =================================================
        #
        # Compatible con:
        #
        # 1. Agente 4 que devuelve diccionario:
        #
        # {
        #     "document_id": 1,
        #     ...
        # }
        #
        # 2. Agente 4 que devuelve directamente
        #    un objeto SRSDocument.
        # =================================================

        document_id = None

        if isinstance(
            srs_result,
            dict
        ):

            document_id = (
                srs_result.get(
                    "document_id"
                )
                or
                srs_result.get(
                    "id"
                )
            )

        else:

            document_id = getattr(
                srs_result,
                "id",
                None
            )

        if not document_id:

            raise ValueError(
                "El Agente 4 terminó, pero no "
                "fue posible obtener el ID "
                "del documento SRS."
            )

        # =================================================
        # RESULTADO
        # =================================================

        print()
        print("=" * 60)

        print(
            "ORQUESTADOR → "
            "PROCESO COMPLETADO"
        )

        print(
            f"Documento SRS ID: "
            f"{document_id}"
        )

        print("=" * 60)

        return {

            "success":
                True,

            "interview_id":
                interview_id,

            "project_id":
                project_id,

            "requirements_count":
                len(
                    requirements
                    or []
                ),

            "enrichment_count":
                (1 if enrichment else 0),

            "document_id":
                document_id
        }