import os

from flask import current_app

from app import db
from app.models import Interview
from app.services.whisper_service import WhisperService


class TranscriptionAgent:

    def __init__(self):

        self.whisper = WhisperService(
            model_name="base"
        )

    def process(self, interview_id):

        interview = db.session.get(
            Interview,
            interview_id
        )

        if not interview:
            raise ValueError(
                "La entrevista no existe."
            )

        if not interview.audio_path:
            raise ValueError(
                "La entrevista no tiene audio."
            )

        audio_path = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            interview.audio_path
        )

        if not os.path.exists(audio_path):
            raise FileNotFoundError(
                "No se encontró el archivo de audio."
            )

        print(
            f"Agente 1 → transcribiendo entrevista "
            f"{interview_id}..."
        )

        transcription = self.whisper.transcribe(
            audio_path
        )

        if not transcription:
            raise ValueError(
                "Whisper no produjo una transcripción."
            )

        interview.transcription = transcription

        db.session.commit()

        print(
            "Agente 1 → transcripción completada."
        )

        return transcription