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

    original_transcription = db.Column(db.Text, nullable=True)

    @property
    def clarifications(self):
        return RequirementClarification.query.filter_by(interview_id=self.id).order_by(RequirementClarification.id).all()

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

    specification = db.Column(db.Text, nullable=True)

    @property
    def actor_pending(self):
        from app.services.requirement_specification import folded
        return folded((self.actor or '').strip()) in (
            '', 'pendiente de aclaracion', 'por aclarar', 'no especificado', 'no especificada', 'desconocido')

    @property
    def quality_attributes(self):
        from app.services.requirement_specification import read_specification
        from app.services.requirement_quality import quality_values
        return quality_values(read_specification(self.specification).get('quality'),
                              {r['key']: r['values'] for r in self.specification_rows})

    @property
    def interview_guidance(self):
        from app.services.requirement_quality import interview_guidance
        return interview_guidance(self)

    @property
    def has_applied_clarification(self):
        from app.services.requirement_specification import read_specification
        return read_specification(self.specification).get('extraction_status') == 'clarified'

    @property
    def pending_fields(self):
        result = []
        if self.actor_pending:
            result.append('Actor')
        if self.priority not in ('esencial', 'opcional', 'condicional'):
            result.append('Prioridad')
        result.extend(row['label'] for row in self.specification_rows if not row['values'])
        for key, label in [('clarity', 'Claridad (sin ambigüedad)'), ('verifiability', 'Verificabilidad')]:
            if not self.quality_attributes[key]['sufficient']:
                result.append(label)
        return result

    @property
    def clarifications(self):
        return RequirementClarification.query.filter_by(requirement_id=self.id).order_by(RequirementClarification.id).all()

    @property
    def specification_rows(self):
        from app.services.requirement_specification import specification_rows
        interview = db.session.get(Interview, self.interview_id)
        source = interview.transcription if interview else self.source_excerpt
        return specification_rows(self.specification, source or "", {
            "description": self.description, "source_excerpt": self.source_excerpt})

    @property
    def name(self):
        from app.services.requirement_specification import requirement_name
        return requirement_name(self.description)

    @property
    def specification_unavailable(self):
        from app.services.requirement_specification import read_specification
        return read_specification(self.specification).get("extraction_status") == "unavailable"

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


class RequirementClarification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    requirement_id = db.Column(db.Integer, db.ForeignKey('requirement.id'), nullable=False)
    interview_id = db.Column(db.Integer, db.ForeignKey('interview.id'), nullable=False)
    code = db.Column(db.String(20), nullable=False)
    audio_path = db.Column(db.String(300), nullable=False)
    transcription = db.Column(db.Text, nullable=False)
    fields = db.Column(db.Text, nullable=False)
    previous_specification = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), default='pending', nullable=False)
    error = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
