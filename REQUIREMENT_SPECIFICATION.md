# Ficha de requisitos funcionales para desarrollo

Se mantiene el SRS basado en IEEE 830-1998. La ficha es una adaptación práctica,
no una plantilla literal ni una declaración de cumplimiento de ISO/IEC/IEEE 29148.

## Contenido visible

- Identificador y nombre, enunciado, actor y prioridad.
- Precondiciones.
- Datos de entrada y validaciones.
- Comportamiento principal.
- Reglas de negocio y permisos explícitos.
- Excepciones y alternativas.
- Resultado esperado.
- Criterios de aceptación.

La evidencia, el origen y los indicadores de revisión están en un desplegable
cerrado por defecto. No se muestran campos administrativos pendientes ni bloques
separados de objetivo, disparador o anexos. El comportamiento principal conserva las acciones explícitas, sin inventar pasos. En el SRS los indicadores pasan
al apéndice de trazabilidad. Las condiciones relevantes no se eliminan del enunciado.

## Compatibilidad y uso

Las fichas anteriores se presentan en bloques de componentes sin cambiar los
datos guardados. Los permisos se agrupan con las reglas y las postcondiciones con
las salidas. Precondiciones y excepciones tienen su propio apartado. Cuando falta
el comportamiento principal, se recuperan acciones literales del contexto del RF. Se eliminan citas duplicadas dentro
de cada bloque y se verifica que la evidencia exista en la entrevista.

Reiniciar Flask y actualizar la página basta para ver la nueva estructura.
Generar un nuevo SRS aplica el formato de componentes al documento y al Word. Los documentos
históricos no se modifican. «Analizar nuevamente» extrae los siete campos del
formato nuevo (schema_version 3), pero, como antes, reemplaza los RF de esa entrevista.

## Extracción y límites

El modelo selecciona números de fragmentos de la misma entrevista y el código copia
el texto original. No se emplea contexto académico para completar las fichas.
Se solicitan preconditions, inputs, main_flow, business_rules, alternatives,
outputs y acceptance_criteria. Cada campo vacío muestra una orientación concreta
para su aclaración. No se completa con supuestos para aparentar una ficha terminada.
Se rechazan índices inválidos y se conservan negaciones, condiciones y límites
presentes en los fragmentos. La clasificación semántica requiere revisión humana.
Los campos sin evidencia identificada muestran «Pendiente de aclaración».

La extracción identifica solicitudes principales y agrupa sus explicaciones hasta
la siguiente solicitud o un cambio explícito de tema. No extrae RF separados de
precondiciones, campos o casos de aceptación. Los enunciados explícitos del sistema
se conservan literalmente, incluyendo negaciones y condiciones. El actor se obtiene
de una construcción gramatical explícita; la obligatoriedad de un campo no establece
la prioridad de la función. La llamada adicional utiliza hasta 6500 caracteres del
bloque. En fichas antiguas sin un ancla reconocible se conserva el filtro local
conservador. Las acciones coordinadas siguen requiriendo revisión.
La clasificación combina selección de evidencias por el modelo y reglas de discurso
para recuperar precondiciones, entradas, reglas, excepciones, resultados y casos
explícitos de aceptación. Si el modelo falla, se mantienen esas evidencias literales
y se muestra una advertencia. No se reparan automáticamente errores del audio.
El mismo filtro se aplica a fichas guardadas en la web y al generar un SRS.
Las reglas, resultados y criterios deben contener indicios propios de ese campo;
una repetición del enunciado no basta. Los detalles declarados sin definir se omiten.
Son controles conservadores basados en patrones: pueden omitir información válida
distante o expresada de otra manera, y no sustituyen una revisión semántica humana.
Si la extracción falla, se conserva el requisito y se presenta una advertencia.
No se inventan escenarios de aceptación. Los RF rechazados ya guardados requieren
reanálisis para que se vuelva a construir la lista; no se borran automáticamente.

Las enumeraciones introductorias no generan RF adicionales cuando una solicitud
posterior desarrolla el mismo objetivo; se conservan los elementos sin desarrollo.
La correspondencia usa la acción y el objeto, o una única solicitud posterior con
esa acción. Esta última asociación es heurística y requiere revisión si hay
objetivos distintos expresados con el mismo verbo. No se impone una cantidad fija.
Las frases «no hemos acordado los criterios» y las reuniones de aclaración no son
criterios de aceptación. Los RF con aspectos explícitamente pendientes se marcan
como ambiguos y no completamente verificables, conservando los resultados conocidos.

## Pruebas

`venv/Scripts/python.exe -X utf8 -m unittest discover -s tests -p test_requirement_specification.py -v`

Pruebas con base temporal y respuestas simuladas de Ollama: conservación de datos,
compatibilidad de fichas anteriores, evidencia, vista compacta, MCP, SRS y Word.
Incluye la transcripción de registro bibliotecario como regresión: un RF, actor y
prioridad explícitos, siete componentes y cinco casos de aceptación. También se
comprueba que solicitudes distintas y obligaciones negativas permanezcan separadas.
La transcripción real de cuatro funciones comprueba dos fichas completas y dos
incompletas, tres casos de aceptación en cada función detallada, prioridades y
ausencia de reuniones en los criterios. Se prueba también con selección errónea
de todas las frases como inicios de requisitos.

## Tesis

Actualizar la descripción de la ficha en 3.4.2 y 3.4.4, las capturas de la interfaz
y los criterios de aceptación. La columna JSON de la base de datos no cambia.

## Restauración del flujo anterior

Se restauró la extracción schema_version 3. El flujo experimental de agrupación,
redacción y revisiones sucesivas no se ejecuta. Se conservan los ajustes de lenguaje
cotidiano, la interfaz y los datos. Copia del experimento: tmp/semantic_rollback_20261022/.

## Aclaraciones por audio

Cada ficha permite subir un nuevo audio y transcribirlo con Whisper sin seleccionar
campos manualmente. El modelo identifica automáticamente los componentes aclarados. Una sola consulta a Ollama selecciona
fragmentos literales para los siete componentes de la ficha. Si hay contenido identificado,
reemplaza esos campos; los demás se conservan. Si no se identifica contenido para
un campo, mantiene su valor anterior. Se conservan el código y el enunciado del RF y no se vuelve a extraer la entrevista
completa. El actor puede actualizarse cuando el modelo identifica un nombre o rol
literal respaldado por la aclaración; si no se menciona, conserva el anterior. La prioridad se actualiza
cuando el audio expresa una prioridad para ese RF y el modelo identifica su evidencia.
Si no se menciona, se conservan la prioridad y su justificación anteriores.

La primera aclaración conserva `original_transcription` como versión 1. La columna
`transcription` contiene una vista consolidada del original y las aclaraciones en
orden, identificadas por RF. Cada entrevista del proyecto conserva su propio historial.
Los audios siguen separados. `requirement_clarification` guarda transcripción, campos,
estado y ficha previa. La tabla se crea y la columna se añade al iniciar la aplicación.

La transcripción se guarda antes de actualizar el RF. Si Ollama falla, se conserva
para reintentar sin transcribir ni cargar de nuevo. Un reintento aplicado no duplica
cambios; una aclaración antigua no sobrescribe campos con aclaraciones posteriores.
Las entrevistas con aclaraciones no admiten regeneración masiva de RF ni retranscripción
del original, para preservar sus identificadores y el historial. El SRS existente
no se modifica: hay que generar uno nuevo para incorporar los campos aclarados.

Las fichas aclaradas (schema_version 5) se muestran y exportan comprobando que sus
fragmentos existan en la transcripción consolidada. El modelo puede asociar contenido
incorrectamente: la clasificación con IA incluye los atributos de claridad y verificabilidad. No equivale a garantizar exactitud.
Las pruebas de integración
usan Whisper y Ollama simulados; no constituyen una evaluación de precisión de voz o IA.

El contexto académico se consulta y genera en `/projects/<id>/context`, separado
de la pantalla de requisitos. Sus datos y fuentes siguen asociados al proyecto.

La vista señala en rojo los componentes vacíos, el actor pendiente y la prioridad
no especificada. Cada RF muestra una lista de los campos pendientes y un enlace
para subir otra aclaración. El estado sin pendientes solo indica presencia de
información: no equivale a una validación de coherencia o calidad. Identificador y
nombre se generan por el sistema; no se solicitan como datos de entrevista.

## Ejecución completa con historial
El orquestador ejecuta los cuatro agentes en entrevistas sin aclaraciones. Si ya
hay aclaraciones, conserva la transcripción consolidada y los RF existentes,
intenta aplicar los audios pendientes y regenera RAG y SRS. No reextrae ni borra
las fichas aclaradas. Si un audio pendiente falla, informa el error en pantalla
y no continúa a generar un documento que omita silenciosamente esa aclaración.

## Flujo vigente: extracción y aclaración
La claridad (ausencia de ambigüedad) y la verificabilidad son atributos de la
ficha con estado Sí o Por aclarar. Se extraen en la misma consulta que clasifica
los siete componentes, tanto en la entrevista inicial como al actualizar mediante
un audio. No hay una revisión posterior, botón de comprobación ni lista de preguntas
que crezca. Las propiedades JSON `quality.clarity` y `quality.verifiability`
guardan el estado y su motivo breve; los indicadores relacionales se sincronizan
para mantener el contenido del SRS. No cambia la estructura documental IEEE 830.

La claridad necesita un comportamiento descrito y una valoración suficiente de la
IA; la verificabilidad necesita comportamiento, resultado y criterios de aceptación,
además de esa valoración. No se exige una especificación exhaustiva. Los campos
vacíos y ambos atributos pendientes se incluyen en el resumen de la ficha.
El audio debe aportar la información que falta; subir un segundo audio no garantiza
por sí solo completar todos los campos. Los valores anteriores sin nueva información
se conservan. El texto consolidado sigue en la vista de entrevista.

Las fichas antiguas sin estos atributos aparecen Por aclarar hasta actualizarlas
con audio. Los metadatos del proceso de revisión anterior dejan de usarse y se
retiran al guardar una aclaración. No se ejecutan consultas de IA al abrir la página.

Cada atributo pendiente muestra una guía de entrevista referida al RF. Claridad
orienta a explicar quién usa la función, su comportamiento y las interpretaciones
confusas; verificabilidad orienta a describir una acción, su resultado observable
y un ejemplo de aceptación, según los campos que falten. Es ayuda de la interfaz,
no evidencia ni contenido del SRS. No se guarda como respuesta, no añade llamadas
al modelo y deja de mostrarse cuando el atributo es suficiente.

La guía también cubre actor, prioridad y los siete componentes de contenido. Solo
se muestran las preguntas de los campos pendientes, dentro de la sección única
de audio. Son ayudas para la entrevista y no respuestas ni evidencia del RF.

La segmentación respeta secciones narradas explícitamente (por ejemplo, «Primero,
necesitamos…», «La segunda cosa es…»). Las restricciones de datos y los casos de
prueba permanecen con su función. Excluir un dato opcional no interrumpe el contexto
de la explicación. Se reconocen roles cotidianos como «mi recepcionista y yo» y
expresiones de resultados y pruebas como «se guarda correctamente» o «lo
comprobaríamos». La transcripción del taller se conserva como prueba de regresión:
cuatro funciones, dos con todos los componentes y dos con información pendiente.
La calidad semántica de Ollama se simula en estas pruebas; no se certifica con ellas.

### Cobertura de funciones con transcripción irregular
Las transiciones se reconocen también dentro de una frase, sin depender del punto
anterior. Al encontrar apartados numerados ya no se descarta la introducción.
Una recuperación complementaria recorre el texto por fragmentos y solicita citas
literales de objetivos omitidos; los detalles pendientes no excluyen una petición.
Las citas deben existir exactamente en la fuente y pasan por la validación habitual
antes de guardarse. No se fija un mínimo artificial de RF ni se inventan funciones
para llegar a una cuota. La consulta complementaria tiene salida y espera limitadas;
un fallo conserva los objetivos reconocidos por las reglas y se registra en consola.
La transcripción de la tienda, con transiciones mal puntuadas, es otra regresión:
cinco apartados reconocibles y un objetivo recuperado semánticamente. Los errores
léxicos del audio no se sustituyen silenciosamente por palabras supuestas.

### Recuperación de atributos de calidad
Una valoración inválida no se interpreta como falta de información de la persona.
Se toleran booleanos serializados como texto y explicaciones largas, conservando
el significado de la decisión. Si no hay una valoración utilizable y los componentes
necesarios sí tienen contenido, se permite una única recuperación interna de los
atributos sobre la ficha actual, con citas deduplicadas y esquema plano. No se
envía la valoración anterior como información de la entrevista. Esta recuperación
también se aplica a la extracción inicial y a cualquier proyecto, sin reglas de dominio.
Un fallo persistente aparece como «Pendiente de procesamiento» y permite reintentar
la aclaración guardada aunque sus otros campos ya se hayan aplicado. El reintento
no retranscribe, no reemplaza campos y no cambia otros requisitos. Las dudas reales
o los componentes ausentes siguen «Por aclarar». Tener texto en todos los campos
no aprueba automáticamente su calidad.
