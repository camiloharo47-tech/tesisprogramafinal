from datetime import datetime

from app import db


# =====================================================
# PROYECTO
# =====================================================

class Project(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(150),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# =====================================================
# ENTREVISTA
# =====================================================

class ProjectContext(db.Model):
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), primary_key=True)
    content = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Interview(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    project_id = db.Column(
        db.Integer,
        db.ForeignKey("project.id"),
        nullable=False
    )

    audio_path = db.Column(
        db.String(300),
        nullable=True
    )

    transcription = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# =====================================================
# REQUISITO FUNCIONAL
# =====================================================

class Requirement(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    project_id = db.Column(
        db.Integer,
        db.ForeignKey("project.id"),
        nullable=False
    )

    interview_id = db.Column(
        db.Integer,
        db.ForeignKey("interview.id"),
        nullable=False
    )

    code = db.Column(
        db.String(20),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    actor = db.Column(
        db.String(100),
        nullable=True
    )

    priority = db.Column(
        db.String(30),
        default="no_especificada"
    )

    priority_reason = db.Column(
        db.Text,
        nullable=True
    )

    source_excerpt = db.Column(
        db.Text,
        nullable=False
    )

    ambiguity_detected = db.Column(
        db.Boolean,
        default=False
    )

    ambiguity_reason = db.Column(
        db.Text,
        nullable=True
    )

    verifiable = db.Column(
        db.Boolean,
        default=True
    )

    verification_reason = db.Column(
        db.Text,
        nullable=True
    )

    # Será utilizado posteriormente
    # por el Agente 3 + RAG
    enriched_context = db.Column(
        db.Text,
        nullable=True
    )


# =====================================================
# DOCUMENTO SRS
# =====================================================

class SRSDocument(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    project_id = db.Column(
        db.Integer,
        db.ForeignKey("project.id"),
        nullable=False
    )

    content = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
