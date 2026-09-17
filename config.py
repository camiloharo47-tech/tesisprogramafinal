import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:

    SECRET_KEY = "tesis-srs"

    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///" + os.path.join(BASE_DIR, "instance", "srs.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    GENERATED_FOLDER = os.path.join(BASE_DIR, "generated")

    MAX_CONTENT_LENGTH = 200 * 1024 * 1024

    ALLOWED_AUDIO_EXTENSIONS = {
        "mp3",
        "wav",
        "m4a",
        "ogg",
        "webm",
        "mp4"
    }