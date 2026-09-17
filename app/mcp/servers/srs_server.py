import os
import sys
from typing import Optional


# =========================================================
# AGREGAR RAÍZ DEL PROYECTO AL PYTHON PATH
# =========================================================
#
# srs_server.py está en:
#
# app/mcp/servers/srs_server.py
#
# Al ejecutarse como proceso MCP independiente,
# Python necesita conocer la raíz tesis_srs/
# para poder importar app.services.
# =========================================================

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        ".."
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(
        0,
        PROJECT_ROOT
    )


from mcp.server import MCPServer
from pydantic import BaseModel

from app.services.ollama_service import OllamaService


# =========================================================
# ESQUEMA JSON
# =========================================================

SRS_SCHEMA = {

    "type": "object",

    "properties": {

        "purpose": {
            "type": "string"
        },

        "scope": {
            "type": "string"
        },

        "product_perspective": {
            "type": "string"
        },

        "product_functions": {
            "type": "string"
        }
    },

    "required": [
        "purpose",
        "scope",
        "product_perspective",
        "product_functions"
    ],

    "additionalProperties": False
}


# =========================================================
# RESPUESTA MCP
# =========================================================

class SRSGeneralResponse(BaseModel):

    purpose: str
    scope: str
    product_perspective: str
    product_functions: str


# =========================================================
# SERVIDOR MCP
# =========================================================

mcp = MCPServer(

    "SRS Generation",

    instructions=(
        "Servidor MCP encargado de generar "
        "información general para documentos SRS "
        "IEEE 830-1998 utilizando un modelo LLM local."
    )
)


# =========================================================
# OLLAMA
# =========================================================

ollama = OllamaService(
    model_name="llama3.2:3b"
)


# =========================================================
# GENERAR INFORMACIÓN GENERAL DEL SRS
# =========================================================

@mcp.tool(
    title="Generar información general SRS"
)
def generar_informacion_srs(

    project_name: str,

    project_description: str,

    requirements: list[str],

    rag_contexts: Optional[list[str]] = None

) -> SRSGeneralResponse:

    # =====================================================
    # NORMALIZAR
    # =====================================================

    project_name = str(
        project_name or ""
    ).strip()

    project_description = str(
        project_description or ""
    ).strip()

    requirements = [

        str(requirement).strip()

        for requirement in requirements

        if str(requirement).strip()
    ]

    rag_contexts = [

        str(context).strip()

        for context in (
            rag_contexts or []
        )

        if str(context).strip()
    ]


    # =====================================================
    # VALIDACIONES
    # =====================================================

    if not project_name:

        raise ValueError(
            "El proyecto no tiene nombre."
        )

    if not requirements:

        raise ValueError(
            "El proyecto no tiene "
            "requisitos funcionales."
        )


    # =====================================================
    # REQUISITOS
    # =====================================================

    requirement_text = "\n".join(

        f"- {requirement}"

        for requirement in requirements
    )


    # =====================================================
    # CONTEXTO RAG
    # =====================================================

    if rag_contexts:

        rag_text = "\n".join(

            f"- {context}"

            for context in rag_contexts
        )

    else:

        rag_text = (
            "No existe contexto externo disponible."
        )


    # =====================================================
    # PROMPT
    # =====================================================

    prompt = f"""
Eres un analista especializado en Ingeniería
de Requisitos de Software.

Debes redactar únicamente información general
para un documento de Especificación de Requisitos
de Software estructurado con base en IEEE 830-1998.

PROYECTO

Nombre:

{project_name}

Descripción:

{project_description or "No especificada"}

REQUISITOS FUNCIONALES IDENTIFICADOS
EN LAS ENTREVISTAS

{requirement_text}

CONTEXTO EXTERNO RECUPERADO MEDIANTE RAG

{rag_text}


JERARQUÍA DE INFORMACIÓN

La información del proyecto y los requisitos
funcionales obtenidos de las entrevistas son
la fuente principal y autorizada para describir
el sistema.

El contexto RAG es únicamente información
externa complementaria.

El contexto RAG NO representa decisiones
tomadas por el Product Owner.


REGLAS OBLIGATORIAS

1. Los requisitos funcionales proporcionados
   son definitivos para esta etapa.

2. NO modifiques los requisitos funcionales.

3. NO agregues requisitos funcionales.

4. NO elimines requisitos funcionales.

5. NO combines requisitos funcionales.

6. NO inventes actores.

7. NO inventes tecnologías.

8. NO inventes frameworks.

9. NO inventes lenguajes de programación.

10. NO inventes bases de datos.

11. NO inventes arquitecturas.

12. NO inventes herramientas.

13. NO inventes plataformas.

14. NO inventes metodologías.

15. NO inventes requisitos no funcionales.

16. NO agregues seguridad, rendimiento,
    disponibilidad, interfaces o restricciones
    si no aparecen explícitamente en la
    información autorizada.

17. El contexto RAG NO debe convertirse
    en requisitos.

18. El contexto RAG NO debe modificar
    el alcance funcional obtenido de las
    entrevistas.

19. El contexto RAG NO debe convertirse
    en una característica del proyecto.

20. El contexto RAG NO debe convertirse
    en una decisión técnica del proyecto.

21. Una tecnología encontrada mediante RAG
    NO significa que el proyecto utilizará
    esa tecnología.

22. Un framework encontrado mediante RAG
    NO significa que el proyecto utilizará
    ese framework.

23. Una arquitectura encontrada mediante RAG
    NO significa que el proyecto utilizará
    esa arquitectura.

24. NO presentes información encontrada
    en Internet como si hubiera sido
    solicitada por el Product Owner.

25. NO inventes objetivos empresariales.

26. NO inventes beneficios empresariales.

27. Si una información aparece solamente
    dentro del contexto RAG y no aparece
    en el proyecto ni en los requisitos,
    no la presentes como característica
    del sistema.

28. Si no existe información suficiente,
    utiliza exactamente:

    "No especificado en la entrevista."

29. Redacta de forma formal,
    académica y concisa.


CAMPOS


purpose:

Describe el propósito DEL DOCUMENTO SRS.

Indica que el documento especifica los
requisitos funcionales identificados para
el proyecto.

No inventes objetivos del negocio.


scope:

Describe el alcance únicamente utilizando:

- nombre del proyecto
- descripción del proyecto
- requisitos funcionales proporcionados

No amplíes el alcance utilizando RAG.


product_perspective:

Describe brevemente el producto únicamente
utilizando:

- nombre del proyecto
- descripción del proyecto
- requisitos funcionales

Ignora tecnologías, frameworks, lenguajes,
arquitecturas, bases de datos y herramientas
que aparezcan únicamente dentro del RAG.


product_functions:

Resume exclusivamente las funciones que
ya aparecen en los requisitos funcionales.

No agregues funciones nuevas.

Devuelve exclusivamente JSON válido.
"""


    # =====================================================
    # OLLAMA
    # =====================================================

    result = ollama.generate_json(
        prompt,
        SRS_SCHEMA
    )


    # =====================================================
    # TEXTO POR DEFECTO
    # =====================================================

    default_text = (
        "No especificado en la entrevista."
    )


    # =====================================================
    # RESPUESTA
    # =====================================================

    return SRSGeneralResponse(

        purpose=(

            str(
                result.get(
                    "purpose",
                    default_text
                )
            ).strip()

            or default_text
        ),

        scope=(

            str(
                result.get(
                    "scope",
                    default_text
                )
            ).strip()

            or default_text
        ),

        product_perspective=(

            str(
                result.get(
                    "product_perspective",
                    default_text
                )
            ).strip()

            or default_text
        ),

        product_functions=(

            str(
                result.get(
                    "product_functions",
                    default_text
                )
            ).strip()

            or default_text
        )
    )


# =========================================================
# INICIAR SERVIDOR MCP
# =========================================================

if __name__ == "__main__":

    mcp.run()