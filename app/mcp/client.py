import asyncio
import sys

from pathlib import Path

from mcp import (
    Client,
    StdioServerParameters
)


class MCPClient:

    def save_project_context(self, project_id, content):
        return self._run(self._call_tool(
            self.database_server, "save_project_context",
            {"project_id": project_id, "content": content}
        ))

    def search_academic(self, query, max_results=10):
        return self._run(self._call_tool(
            self.web_server, "search_academic",
            {"query": query, "max_results": max_results}
        ))

    def __init__(self):

        base = (
            Path(__file__)
            .resolve()
            .parent
            / "servers"
        )

        self.database_server = (
            base / "database_server.py"
        )

        self.web_server = (
            base / "web_server.py"
        )

        self.srs_server = (
            base / "srs_server.py"
        )

    # =====================================================
    # LLAMAR TOOL
    # =====================================================

    async def _call_tool(
        self,
        server_path,
        tool_name,
        arguments=None
    ):

        server = StdioServerParameters(
            command=sys.executable,
            args=[
                str(server_path)
            ]
        )

        async with Client(
            server
        ) as client:

            result = await client.call_tool(
                tool_name,
                arguments or {}
            )

            if result.is_error:

                messages = []

                for item in (
                    result.content
                    or []
                ):

                    text = getattr(
                        item,
                        "text",
                        None
                    )

                    if text:

                        messages.append(
                            text
                        )

                raise RuntimeError(
                    "\n".join(messages)
                    or
                    f"Error ejecutando MCP: "
                    f"{tool_name}"
                )

            return (
                result.structured_content
                or {}
            )

    # =====================================================
    # EJECUTAR ASYNC
    # =====================================================

    def _run(
        self,
        coroutine
    ):

        return asyncio.run(
            coroutine
        )

    # =====================================================
    # DATABASE
    # =====================================================

    def ping_database(self):

        return self._run(
            self._call_tool(
                self.database_server,
                "ping"
            )
        )

    def get_interview(
        self,
        interview_id
    ):

        return self._run(
            self._call_tool(
                self.database_server,
                "get_interview",
                {
                    "interview_id":
                        interview_id
                }
            )
        )

    def get_requirements(
        self,
        interview_id
    ):

        return self._run(
            self._call_tool(
                self.database_server,
                "get_requirements",
                {
                    "interview_id":
                        interview_id
                }
            )
        )

    def save_enriched_context(
        self,
        requirement_id,
        enriched_context
    ):

        return self._run(
            self._call_tool(
                self.database_server,
                "save_enriched_context",
                {
                    "requirement_id":
                        requirement_id,

                    "enriched_context":
                        enriched_context
                }
            )
        )

    def get_project_srs_data(
        self,
        project_id
    ):

        response = self._run(
            self._call_tool(
                self.database_server,
                "get_project_srs_data",
                {
                    "project_id":
                        project_id
                }
            )
        )

        return response.get(
            "project"
        )

    def save_srs_document(
        self,
        project_id,
        content
    ):

        return self._run(
            self._call_tool(
                self.database_server,
                "save_srs_document",
                {
                    "project_id":
                        project_id,

                    "content":
                        content
                }
            )
        )

    # =====================================================
    # WEB
    # =====================================================

    def ping_web(self):

        return self._run(
            self._call_tool(
                self.web_server,
                "ping"
            )
        )

    def search_web(
        self,
        query,
        max_results=5
    ):

        return self._run(
            self._call_tool(
                self.web_server,
                "search_web",
                {
                    "query":
                        query,

                    "max_results":
                        max_results
                }
            )
        )

    # =====================================================
    # SRS
    # =====================================================

    def generate_srs_general(
        self,
        project_name,
        project_description,
        requirements,
        rag_contexts
    ):

        return self._run(
            self._call_tool(
                self.srs_server,

                # IMPORTANTE:
                # Este nombre debe coincidir
                # exactamente con la herramienta
                # registrada en srs_server.py.
                "generar_informacion_srs",

                {
                    "project_name":
                        project_name,

                    "project_description":
                        project_description,

                    "requirements":
                        requirements,

                    "rag_contexts":
                        rag_contexts
                }
            )
        )

