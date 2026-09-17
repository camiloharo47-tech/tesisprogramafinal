import json
import os

from uuid import uuid4

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    current_app,
    send_file
)

from werkzeug.utils import secure_filename

from app import db

from app.models import (
    Project,
    ProjectContext,
    Interview,
    Requirement,
    SRSDocument
)

from app.agents.transcription_agent import (
    TranscriptionAgent
)

from app.agents.requirements_agent import (
    RequirementsAgent
)

from app.agents.enrichment_agent import (
    EnrichmentAgent
)

from app.orchestrator.orchestrator import (
    Orchestrator
)

from app.agents.srs_agent import (
    SRSAgent
)

from app.services.document_service import (
    DocumentService
)


main = Blueprint(
    "main",
    __name__
)


# =====================================================
# VALIDAR AUDIO
# =====================================================

def allowed_audio(filename):

    if "." not in filename:
        return False

    extension = filename.rsplit(
        ".",
        1
    )[1].lower()

    return extension in current_app.config[
        "ALLOWED_AUDIO_EXTENSIONS"
    ]


# =====================================================
# LEER CONTEXTO RAG
# =====================================================

def load_enriched_context(
    enriched_context
):

    if not enriched_context:
        return None

    try:

        context = json.loads(
            enriched_context
        )

        if isinstance(
            context,
            dict
        ):
            return context

    except (
        json.JSONDecodeError,
        TypeError
    ):
        pass

    return None


# =====================================================
# INICIO
# =====================================================

@main.route("/")
def index():

    projects = Project.query.order_by(
        Project.created_at.desc()
    ).all()

    return render_template(
        "index.html",
        projects=projects
    )


# =====================================================
# CREAR PROYECTO
# =====================================================

@main.route(
    "/projects",
    methods=["POST"]
)
def create_project():

    name = request.form.get(
        "name",
        ""
    ).strip()

    description = request.form.get(
        "description",
        ""
    ).strip()

    if not name:

        return redirect(
            url_for(
                "main.index"
            )
        )

    project = Project(
        name=name,
        description=description
    )

    db.session.add(
        project
    )

    db.session.commit()

    return redirect(
        url_for(
            "main.project_detail",
            project_id=project.id
        )
    )


# =====================================================
# VER PROYECTO
# =====================================================

@main.route(
    "/projects/<int:project_id>"
)
def project_detail(project_id):

    project = Project.query.get_or_404(
        project_id
    )

    interviews = (
        Interview.query
        .filter_by(
            project_id=project.id
        )
        .order_by(
            Interview.created_at.desc()
        )
        .all()
    )

    # =================================================
    # ÚLTIMO SRS GENERADO
    # =================================================

    latest_srs = (
        SRSDocument.query
        .filter_by(
            project_id=project.id
        )
        .order_by(
            SRSDocument.created_at.desc()
        )
        .first()
    )

    return render_template(
        "project.html",
        project=project,
        interviews=interviews,
        project_context=get_project_context(project.id),
        latest_srs=latest_srs
    )


# =====================================================
# SUBIR ENTREVISTA
# =====================================================

@main.route(
    "/projects/<int:project_id>/interviews",
    methods=["POST"]
)
def upload_interview(project_id):

    project = Project.query.get_or_404(
        project_id
    )

    audio = request.files.get(
        "audio"
    )

    if (
        not audio
        or not audio.filename
    ):

        return redirect(
            url_for(
                "main.project_detail",
                project_id=project.id
            )
        )

    if not allowed_audio(
        audio.filename
    ):

        return redirect(
            url_for(
                "main.project_detail",
                project_id=project.id
            )
        )

    original_name = secure_filename(
        audio.filename
    )

    extension = original_name.rsplit(
        ".",
        1
    )[1].lower()

    # Nombre único para evitar
    # sobrescribir audios anteriores.
    filename = (
        f"{uuid4().hex}.{extension}"
    )

    path = os.path.join(
        current_app.config[
            "UPLOAD_FOLDER"
        ],
        filename
    )

    audio.save(
        path
    )

    interview = Interview(
        project_id=project.id,
        audio_path=filename
    )

    db.session.add(
        interview
    )

    db.session.commit()

    return redirect(
        url_for(
            "main.interview_detail",
            interview_id=interview.id
        )
    )


# =====================================================
# VER ENTREVISTA
# =====================================================

@main.route(
    "/interviews/<int:interview_id>"
)
def interview_detail(interview_id):

    interview = Interview.query.get_or_404(
        interview_id
    )

    project = Project.query.get_or_404(
        interview.project_id
    )

    return render_template(
        "interview.html",
        interview=interview,
        project=project
    )


# =====================================================
# AGENTE 1 - TRANSCRIPCIÓN
# =====================================================

@main.route(
    "/interviews/<int:interview_id>/transcribe",
    methods=["POST"]
)
def transcribe_interview(interview_id):

    interview = Interview.query.get_or_404(
        interview_id
    )

    agent = TranscriptionAgent()

    try:

        agent.process(
            interview.id
        )

    except Exception as error:

        print(
            f"Error Agente 1: {error}"
        )

    return redirect(
        url_for(
            "main.interview_detail",
            interview_id=interview.id
        )
    )


# =====================================================
# AGENTE 2 - ANALIZAR REQUISITOS
# =====================================================

@main.route(
    "/interviews/<int:interview_id>/requirements",
    methods=["POST"]
)
def analyze_requirements(interview_id):

    interview = Interview.query.get_or_404(
        interview_id
    )

    agent = RequirementsAgent()

    try:

        agent.process(
            interview.id
        )

    except Exception as error:

        print(
            f"Error Agente 2: {error}"
        )

    return redirect(
        url_for(
            "main.view_requirements",
            interview_id=interview.id
        )
    )


# =====================================================
# VER REQUISITOS
# =====================================================

@main.route(
    "/interviews/<int:interview_id>/requirements"
)
def view_requirements(interview_id):

    interview = Interview.query.get_or_404(
        interview_id
    )

    project = Project.query.get_or_404(
        interview.project_id
    )

    requirements = (
        Requirement.query
        .filter_by(
            interview_id=interview.id
        )
        .order_by(
            Requirement.id.asc()
        )
        .all()
    )

    # =================================================
    # CONTEXTOS RAG
    # =================================================

    project_context = get_project_context(project.id)

    return render_template(
        "requirements.html",
        interview=interview,
        project=project,
        requirements=requirements,
        project_context=project_context,
        has_enrichment=bool(project_context)
    )


# =====================================================
# AGENTE 3 - ENRIQUECIMIENTO RAG
# =====================================================

@main.route(
    "/interviews/<int:interview_id>/enrich",
    methods=["POST"]
)
def enrich_requirements(interview_id):
    interview = Interview.query.get_or_404(interview_id)
    enrich_project(interview.project_id)
    return redirect(url_for("main.view_requirements", interview_id=interview.id, _anchor="project-context"))


def get_project_context(project_id):
    record = db.session.get(ProjectContext, project_id)
    return load_enriched_context(record.content) if record else None


@main.route("/projects/<int:project_id>/enrich", methods=["POST"])
def enrich_project(project_id):
    Project.query.get_or_404(project_id)
    try:
        EnrichmentAgent().process_project(project_id)
    except Exception as error:
        from flask import flash
        flash(f"No se pudo generar el contexto del proyecto: {error}", "warning")
    return redirect(url_for("main.project_detail", project_id=project_id))


# =====================================================
# AGENTE 4 - GENERAR SRS
# =====================================================

@main.route(
    "/projects/<int:project_id>/srs/generate",
    methods=["POST"]
)
def generate_srs(project_id):

    project = Project.query.get_or_404(
        project_id
    )

    # Verificar que existan RF
    # antes de generar el documento.
    requirements = (
        Requirement.query
        .filter_by(
            project_id=project.id
        )
        .all()
    )

    if not requirements:

        print(
            "Agente 4 → el proyecto "
            "no tiene requisitos funcionales."
        )

        return redirect(
            url_for(
                "main.project_detail",
                project_id=project.id
            )
        )

    agent = SRSAgent()

    try:

        result = agent.process(
            project.id
        )

        document_id = result.get(
            "document_id"
        )

        if document_id:

            return redirect(
                url_for(
                    "main.view_srs",
                    document_id=document_id
                )
            )

    except Exception as error:

        print(
            f"Error Agente 4: {error}"
        )

    return redirect(
        url_for(
            "main.project_detail",
            project_id=project.id
        )
    )


# =====================================================
# VER DOCUMENTO SRS
# =====================================================

@main.route(
    "/srs/<int:document_id>"
)
def view_srs(document_id):

    document = (
        SRSDocument.query
        .get_or_404(
            document_id
        )
    )

    project = (
        Project.query
        .get_or_404(
            document.project_id
        )
    )

    return render_template(
        "srs.html",
        document=document,
        project=project
    )


# =====================================================
# DESCARGAR DOCUMENTO WORD
# =====================================================

@main.route(
    "/srs/<int:document_id>/download"
)
def download_srs(document_id):

    document = (
        SRSDocument.query
        .get_or_404(
            document_id
        )
    )

    project = (
        Project.query
        .get_or_404(
            document.project_id
        )
    )

    service = DocumentService()

    buffer = service.create_docx(
        document.content
    )

    safe_project_name = secure_filename(
        project.name
    )

    if not safe_project_name:
        safe_project_name = (
            f"proyecto_{project.id}"
        )

    filename = (
        f"SRS_{safe_project_name}.docx"
    )

    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype=(
            "application/"
            "vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        )
    )
# =====================================================
# ELIMINAR PROYECTO
# =====================================================

@main.route(
    "/projects/<int:project_id>/delete",
    methods=["POST"]
)
def delete_project(project_id):

    project = Project.query.get_or_404(
        project_id
    )

    try:

        # =============================================
        # ELIMINAR AUDIOS DE LAS ENTREVISTAS
        # =============================================

        interviews = (
            Interview.query
            .filter_by(
                project_id=project.id
            )
            .all()
        )

        for interview in interviews:

            if interview.audio_path:

                audio_path = os.path.join(
                    current_app.config[
                        "UPLOAD_FOLDER"
                    ],
                    interview.audio_path
                )

                if os.path.exists(
                    audio_path
                ):

                    try:

                        os.remove(
                            audio_path
                        )

                    except Exception as error:

                        print(
                            "No se pudo eliminar "
                            f"el audio: {error}"
                        )

        # =============================================
        # ELIMINAR REQUISITOS
        # =============================================

        Requirement.query.filter_by(
            project_id=project.id
        ).delete(
            synchronize_session=False
        )

        # =============================================
        # ELIMINAR DOCUMENTOS SRS
        # =============================================

        SRSDocument.query.filter_by(
            project_id=project.id
        ).delete(
            synchronize_session=False
        )

        # =============================================
        # ELIMINAR ENTREVISTAS
        # =============================================

        Interview.query.filter_by(
            project_id=project.id
        ).delete(
            synchronize_session=False
        )

        # =============================================
        # ELIMINAR PROYECTO
        # =============================================

        ProjectContext.query.filter_by(project_id=project.id).delete(synchronize_session=False)

        db.session.delete(
            project
        )

        db.session.commit()

        print(
            f"Proyecto {project_id} eliminado."
        )

    except Exception as error:

        db.session.rollback()

        print(
            f"Error eliminando proyecto: {error}"
        )

        return redirect(
            url_for(
                "main.project_detail",
                project_id=project.id
            )
        )

    return redirect(
        url_for(
            "main.index"
        )
    )
# =====================================================
# ORQUESTADOR - PROCESAR ENTREVISTA COMPLETA
# =====================================================

@main.route(
    "/interviews/<int:interview_id>/process-all",
    methods=["POST"]
)
def process_interview_all(
    interview_id
):

    interview = (
        Interview.query
        .get_or_404(
            interview_id
        )
    )

    try:

        print()
        print("=" * 60)

        print(
            "FLASK → ejecutando "
            "orquestador..."
        )

        print("=" * 60)

        orchestrator = (
            Orchestrator()
        )

        result = (
            orchestrator
            .process_interview(
                interview.id
            )
        )

        document_id = (
            result.get(
                "document_id"
            )
        )

        if not document_id:

            raise ValueError(
                "El orquestador no devolvió "
                "el ID del documento SRS."
            )

        print(
            "FLASK → abriendo "
            f"documento {document_id}"
        )

        # =============================================
        # IR DIRECTAMENTE AL SRS
        # =============================================

        return redirect(
            url_for(
                "main.view_srs",
                document_id=document_id
            )
        )

    except Exception as error:

        print()
        print("=" * 60)

        print(
            "ERROR EN PROCESAMIENTO COMPLETO"
        )

        print(
            type(error).__name__
        )

        print(
            str(error)
        )

        print("=" * 60)

        return redirect(
            url_for(
                "main.project_detail",
                project_id=interview.project_id
            )
        )
