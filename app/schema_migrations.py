"""Additive, idempotent migration for existing SQLite installations."""
from sqlalchemy import inspect

def upgrade_requirement_specification(engine):
    if engine.dialect.name != "sqlite":
        return
    with engine.begin() as connection:
        columns = {column["name"] for column in inspect(connection).get_columns("requirement")}
        if "specification" not in columns:
            connection.exec_driver_sql("ALTER TABLE requirement ADD COLUMN specification TEXT")
        if inspect(connection).has_table('interview'):
            columns = {column['name'] for column in inspect(connection).get_columns('interview')}
            if 'original_transcription' not in columns:
                connection.exec_driver_sql('ALTER TABLE interview ADD COLUMN original_transcription TEXT')
