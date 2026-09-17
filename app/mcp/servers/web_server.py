import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from app.services.academic_search_service import AcademicSearchService

from typing import List, Optional

from ddgs import DDGS

from mcp.server import MCPServer

from pydantic import BaseModel


# =====================================================
# MODELOS DE RESPUESTA
# =====================================================

class WebResult(BaseModel):

    title: str
    url: str
    snippet: str


class WebSearchResponse(BaseModel):

    query: str
    results: List[WebResult]
    error: Optional[str] = None


class PingResponse(BaseModel):

    status: str
    server: str


class AcademicSearchResponse(BaseModel):
    query: str
    results: List[dict]
    warnings: List[str]
    providers: List[str]


# =====================================================
# SERVIDOR MCP WEB
# =====================================================

mcp = MCPServer(
    "SRS Web Search Server"
)


# =====================================================
# LOG
# =====================================================

def log(message):

    # MCP por stdio utiliza stdout para
    # la comunicación del protocolo.
    #
    # Los mensajes propios van a stderr.

    print(
        message,
        file=sys.stderr,
        flush=True
    )


# =====================================================
# PING
# =====================================================

@mcp.tool()
def ping() -> PingResponse:

    return PingResponse(
        status="ok",
        server="web"
    )


# =====================================================
# BÚSQUEDA WEB
# =====================================================

@mcp.tool()
def search_web(
    query: str,
    max_results: int = 5
) -> WebSearchResponse:

    query = str(
        query
        or ""
    ).strip()


    # =================================================
    # CONSULTA VACÍA
    # =================================================

    if not query:

        return WebSearchResponse(
            query="",
            results=[],
            error=None
        )


    # =================================================
    # VALIDAR CANTIDAD
    # =================================================

    try:

        max_results = int(
            max_results
        )

    except (
        ValueError,
        TypeError
    ):

        max_results = 5


    max_results = max(
        1,
        min(
            max_results,
            10
        )
    )


    log(
        f"MCP Web → buscando: {query}"
    )


    # =================================================
    # BÚSQUEDA DDGS
    # =================================================

    try:

        raw_results = list(
            DDGS().text(
                query,
                max_results=max_results
            )
        )


    except Exception as error:

        message = (
            f"{type(error).__name__}: "
            f"{error}"
        )


        log(
            f"MCP Web → ERROR: "
            f"{message}"
        )


        return WebSearchResponse(

            query=query,

            results=[],

            error=message
        )


    # =================================================
    # CONVERTIR RESULTADOS
    # =================================================

    results = []


    for item in raw_results:

        if not isinstance(
            item,
            dict
        ):

            continue


        title = str(
            item.get(
                "title",
                ""
            )
            or ""
        ).strip()


        url = str(
            item.get(
                "href"
            )
            or item.get(
                "url"
            )
            or ""
        ).strip()


        snippet = str(
            item.get(
                "body"
            )
            or item.get(
                "snippet"
            )
            or ""
        ).strip()


        if not title:
            continue


        if not url:
            continue


        if not snippet:
            continue


        results.append(

            WebResult(

                title=title,

                url=url,

                snippet=snippet
            )
        )


    # =================================================
    # LOG
    # =================================================

    log(
        f"MCP Web → DDGS produjo "
        f"{len(raw_results)} "
        "resultado(s) originales."
    )


    log(
        f"MCP Web → "
        f"{len(results)} "
        "resultado(s) válidos."
    )


    # =================================================
    # RESPUESTA MCP ESTRUCTURADA
    # =================================================

    return WebSearchResponse(

        query=query,

        results=results,

        error=None
    )


# =====================================================
# EJECUTAR SERVIDOR
# =====================================================

@mcp.tool()
def search_academic(query: str, max_results: int = 10) -> AcademicSearchResponse:
    """Search scholarly article metadata in Crossref."""
    return AcademicSearchResponse(**AcademicSearchService().search(query, max_results))


if __name__ == "__main__":

    mcp.run()

