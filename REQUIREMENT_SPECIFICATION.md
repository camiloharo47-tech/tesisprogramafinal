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
