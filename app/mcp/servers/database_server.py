import json
import sqlite3

from datetime import datetime
from pathlib import Path
from typing import Any

from mcp.server import MCPServer


mcp = MCPServer(
    "SRS Database Server"
)


PROJECT_ROOT = (
    Path(__file__).resolve().parents[3]
)

DATABASE_PATH = (
    PROJECT_ROOT
    / "instance"
    / "srs.db"
)


# =========================================================
# CONEXIÓN
# =========================================================

def get_connection():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = (
        sqlite3.Row
    )

    return connection


# =========================================================
# PING
# =========================================================

@mcp.tool()
def ping() -> dict[str, Any]:

    return {
        "status": "ok",
        "server": "database"
    }


# =========================================================
# ENTREVISTA
# =========================================================

@mcp.tool()
def get_interview(
    interview_id: int
) -> dict[str, Any]:

    connection = get_connection()

    try:

        row = connection.execute(
            """
            SELECT
                id,
                project_id,
                audio_path,
                transcription,
                created_at
            FROM interview
            WHERE id = ?
            """,
            (interview_id,)
        ).fetchone()

        if not row:

            return {
                "found": False,
                "interview": None
            }

        return {
            "found": True,
            "interview": dict(row)
        }

    finally:

        connection.close()


# =========================================================
# RF DE ENTREVISTA
# =========================================================

@mcp.tool()
def get_requirements(
    interview_id: int
) -> dict[str, Any]:

    connection = get_connection()

    try:

        rows = connection.execute(
            """
            SELECT
                id,
                project_id,
                interview_id,
                code,
                description,
                actor,
                priority,
                priority_reason,
                source_excerpt,
                ambiguity_detected,
                ambiguity_reason,
                verifiable,
                verification_reason,
                enriched_context,
                specification
            FROM requirement
            WHERE interview_id = ?
            ORDER BY id ASC
            """,
            (interview_id,)
        ).fetchall()


        requirements = []

        for row in rows:

            item = dict(row)

            item["ambiguity_detected"] = bool(
                item["ambiguity_detected"]
            )

            item["verifiable"] = bool(
                item["verifiable"]
            )

            requirements.append(item)


        return {
            "requirements": requirements
        }

    finally:

        connection.close()


# =========================================================
# GUARDAR RAG
# =========================================================

@mcp.tool()
def save_enriched_context(
    requirement_id: int,
    enriched_context: str
) -> dict[str, Any]:

    connection = get_connection()

    try:

        cursor = connection.execute(
            """
            UPDATE requirement
            SET enriched_context = ?
            WHERE id = ?
            """,
            (
                enriched_context,
                requirement_id
            )
        )

        connection.commit()

        return {
            "updated":
                cursor.rowcount > 0,

            "requirement_id":
                requirement_id
        }

    finally:

        connection.close()


# =========================================================
# DATOS DEL PROYECTO PARA SRS
# =========================================================

@mcp.tool()
def get_project_srs_data(
    project_id: int
) -> dict[str, Any]:

    connection = get_connection()

    try:

        project_row = connection.execute(
            """
            SELECT
                id,
                name,
                description,
                created_at
            FROM project
            WHERE id = ?
            """,
            (project_id,)
        ).fetchone()


        if not project_row:

            return {
                "found": False,
                "project": None
            }


        rows = connection.execute(
            """
            SELECT
                id,
                project_id,
                interview_id,
                code,
                description,
                actor,
                priority,
                priority_reason,
                source_excerpt,
                ambiguity_detected,
                ambiguity_reason,
                verifiable,
                verification_reason,
                enriched_context,
                specification
            FROM requirement
            WHERE project_id = ?
            ORDER BY id ASC
            """,
            (project_id,)
        ).fetchall()


        requirements = []

        for row in rows:

            item = dict(row)

            item["ambiguity_detected"] = bool(
                item["ambiguity_detected"]
            )

            item["verifiable"] = bool(
                item["verifiable"]
            )

            context = {}

            if item.get(
                "enriched_context"
            ):

                try:

                    context = json.loads(
                        item[
                            "enriched_context"
                        ]
                    )

                except (
                    json.JSONDecodeError,
                    TypeError
                ):

                    context = {}


            item["context"] = context

            requirements.append(
                item
            )


        project = dict(
            project_row
        )

        context_row = connection.execute(
            "SELECT content FROM project_context WHERE project_id = ?", (project_id,)
        ).fetchone()
        project["context"] = json.loads(context_row["content"]) if context_row else {}
        project["interviews"] = [dict(row) for row in connection.execute(
            "SELECT id, transcription FROM interview WHERE project_id = ? ORDER BY id", (project_id,)
        ).fetchall()]

        project["requirements"] = (
            requirements
        )


        return {
            "found": True,
            "project": project
        }

    finally:

        connection.close()


# =========================================================
# GUARDAR SRS
# =========================================================

@mcp.tool()
def save_srs_document(
    project_id: int,
    content: str
) -> dict[str, Any]:

    connection = get_connection()

    try:

        created_at = (
            datetime.utcnow().isoformat()
        )


        cursor = connection.execute(
            """
            INSERT INTO srs_document (
                project_id,
                content,
                created_at
            )
            VALUES (?, ?, ?)
            """,
            (
                project_id,
                content,
                created_at
            )
        )


        connection.commit()


        return {
            "saved": True,
            "id": cursor.lastrowid,
            "project_id": project_id,
            "created_at": created_at
        }

    finally:

        connection.close()


@mcp.tool()
def save_project_context(project_id: int, content: str) -> dict[str, Any]:
    context = json.loads(content)
    if not isinstance(context, dict) or context.get("scope") != "project":
        raise ValueError("El contexto debe pertenecer al proyecto.")
    connection = get_connection()
    try:
        if not connection.execute("SELECT id FROM project WHERE id = ?", (project_id,)).fetchone():
            raise ValueError("El proyecto no existe.")
        connection.execute(
            "INSERT INTO project_context (project_id, content, updated_at) VALUES (?, ?, ?) "
            "ON CONFLICT(project_id) DO UPDATE SET content=excluded.content, updated_at=excluded.updated_at",
            (project_id, content, datetime.utcnow().isoformat())
        )
        connection.commit()
        return {"saved": True, "project_id": project_id}
    finally:
        connection.close()


if __name__ == "__main__":
    mcp.run()
