# Recuperación académica del agente 3

El agente 3 consulta Crossref (artículos de revistas y congresos) por medio
de MCP. Genera un único contexto por proyecto a partir de su descripción,
los requisitos de todas sus entrevistas y sus transcripciones. Realiza un
conjunto acotado de consultas por proyecto, no una búsqueda por requisito. La extracción
de palabras del dominio es heurística; incluye algunas equivalencias en
inglés, como biblioteca/library. No realiza búsqueda web general.

Crossref devuelve metadatos depositados por editoriales; no garantiza que
un artículo esté indexado en Scopus ni que haya sido revisado por pares.
Se conservan título, autores, año, publicación, DOI y proveedor cuando existen.
Solo los resúmenes disponibles se utilizan como evidencia para generar
contexto. Los registros sin resumen se muestran como referencias, no como
evidencia. No se descarga ni se afirma haber leído el texto completo.

## Google Scholar

La búsqueda automática utiliza únicamente Crossref y no necesita una clave
de Scopus. La integración con Scopus fue retirada. El aviso de configuración
guardado en contextos anteriores tampoco se muestra en la interfaz.

Google Scholar se ofrece mediante un enlace para consulta manual. No se
consulta automáticamente y sus resultados no se incorporan al RAG.
La interfaz muestra qué proveedores respondieron y los fallos de consulta.
No hay sustitución silenciosa por resultados de la web general.

El contexto se guarda en `project_context`, con un único registro por proyecto.
La tabla se crea automáticamente al iniciar la aplicación; los datos existentes
no se borran. Los antiguos contextos por requisito se conservan en la base,
pero no se muestran ni se utilizan para generar nuevos documentos.

En la pantalla de requisitos funcionales, debajo del listado de RF, usar «Generar contexto académico del proyecto»
o «Actualizar contexto académico del proyecto». Actualizarlo cuando cambien
los requisitos o se incorporen entrevistas. El procesamiento completo de una
entrevista actualiza el contexto del proyecto antes de generar el SRS.

El SRS presenta la síntesis una sola vez en «4.2 Contexto académico del
proyecto», junto con su evidencia. La trazabilidad de cada requisito a la
entrevista permanece en «4.1». Los SRS anteriores no se modifican; regenerar
el documento para obtener el nuevo formato.

## Secciones complementarias del SRS

El generador incluye las secciones de la guía IEEE 830 proporcionada,
incluida «2.6 Requisitos futuros». `SRSGuidanceService` produce orientación
mediante plantillas adaptadas al nombre, descripción, actores y RF del
proyecto. No son requisitos nuevos extraídos por el modelo.

Las secciones complementarias llevan «(Fuera del alcance de la tesis)» y
se redactan como propuestas pendientes de validación. No se inventan
cifras de rendimiento, tecnologías obligatorias ni decisiones aprobadas.
Los RF de 3.2, su evidencia en 4.1 y el contexto académico de 4.2 conservan
su tratamiento propio. La exportación Word mantiene las mismas marcas.

## Verificación

`venv/Scripts/python.exe -X utf8 -m unittest discover -s tests -p test_academic_search.py -v`

`venv/Scripts/python.exe -X utf8 -m unittest discover -s tests -p test_project_rag.py -v`

Estas pruebas no requieren red, Ollama ni cambios en la base de datos.

Documentación: https://www.crossref.org/documentation/retrieve-metadata/rest-api/
