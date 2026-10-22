import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(test_config=None):

    app = Flask(__name__)

    app.config.from_object("config.Config")
    if test_config:
        app.config.update(test_config)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["GENERATED_FOLDER"], exist_ok=True)

    db.init_app(app)

    from app.routes import main

    app.register_blueprint(main)

    with app.app_context():

        from app import models

        db.create_all()

        from app.schema_migrations import upgrade_requirement_specification
        upgrade_requirement_specification(db.engine)

    return app
