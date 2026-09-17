import re
import unicodedata
from difflib import SequenceMatcher

from app import db
from app.models import Interview, Requirement
from app.services.ollama_service import OllamaService


class RequirementsAgent:

    SCHEMA = {
        "type": "object",
        "properties": {
            "requirements": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string"
                        },
                        "actor": {
                            "type": "string"
                        },
                        "ambiguity_detected": {
                            "type": "boolean"
                        },
                        "ambiguity_reason": {
                            "type": "string"
                        },
                        "verifiable": {
                            "type": "boolean"
                        },
                        "verification_reason": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "description",
                        "actor",
                        "ambiguity_detected",
                        "ambiguity_reason",
                        "verifiable",
                        "verification_reason"
                    ],
                    "additionalProperties": False
                }
            }
        },
        "required": [
            "requirements"
        ],
        "additionalProperties": False
    }

    # =====================================================
    # ACCIONES GENERALES
    # =====================================================
    #
    # Esta lista NO contiene todas las posibles
    # funcionalidades de todos los sistemas.
    #
    # Solo sirve como apoyo de validación.
    #
    # Ollama puede identificar otros verbos
    # aunque no estén aquí.
    # =====================================================

    ACTIONS = {

        "crear": (
            "crear",
            "registr",
            "agreg",
            "anad",
            "insert",
            "guard",
            "almacen"
        ),

        "actualizar": (
            "actualiz",
            "modific",
            "edit",
            "cambi"
        ),

        "eliminar": (
            "elimin",
            "borr",
            "quit"
        ),

        "consultar": (
            "consult",
            "busc",
            "listar",
            "mostrar",
            "visualiz",
            "present"
        ),

        "enviar": (
            "envi",
            "notific",
            "avis",
            "comunic"
        ),

        "generar": (
            "gener",
            "produc",
            "emit"
        ),

        "definir": (
            "defin",
        ),

        "procesar": (
            "proces",
            "transform"
        ),

        "calcular": (
            "calcul",
            "comput"
        ),

        "validar": (
            "valid",
            "verific",
            "comprob"
        ),

        "aprobar": (
            "aprob",
            "autoriz"
        ),

        "rechazar": (
            "rechaz",
        ),

        "asignar": (
            "asign",
        ),

        "reservar": (
            "reserv",
        ),

        "programar": (
            "program",
            "agend"
        ),

        "cancelar": (
            "cancel",
            "anul"
        ),

        "pagar": (
            "pagar",
            "pago"
        ),

        "cobrar": (
            "cobr",
        ),

        "cargar": (
            "carg",
            "subir"
        ),

        "descargar": (
            "descarg",
        ),

        # No usar solo "import"
        # porque también coincide con "importante".
        "importar": (
            "importar",
            "importacion"
        ),

        "exportar": (
            "export",
        ),

        "autenticar": (
            "autentic",
            "login"
        ),

        "solicitar": (
            "solicit",
        ),

        "confirmar": (
            "confirm",
        ),

        "devolver": (
            "devol",
        )
    }

    # =====================================================
    # INICIALIZAR
    # =====================================================

    def __init__(self):

        self.ollama = OllamaService(
            model_name="llama3.2:3b"
        )

    # =====================================================
    # PROCESAR ENTREVISTA
    # =====================================================

    def process(
        self,
        interview_id
    ):

        interview = db.session.get(
            Interview,
            interview_id
        )

        if not interview:

            raise ValueError(
                "La entrevista no existe."
            )

        if not interview.transcription:

            raise ValueError(
                "La entrevista no tiene transcripción."
            )

        transcription = (
            interview.transcription.strip()
        )

        print()
        print("=" * 60)

        print(
            f"Agente 2 → entrevista "
            f"{interview.id} "
            f"| proyecto "
            f"{interview.project_id}"
        )

        print("=" * 60)

        print(
            "Transcripción actual → "
            f"{transcription[:250]}"
        )

        segments = self._split(
            transcription
        )

        requirements = []

        for index, segment in enumerate(
            segments,
            start=1
        ):

            print()

            print(
                f"Fragmento "
                f"{index}/"
                f"{len(segments)}:"
            )

            print(
                segment
            )

            # =============================================
            # FILTRO PREVIO
            # =============================================

            if not self._potential_function(
                segment
            ):

                print(
                    "→ omitido: no expresa "
                    "una funcionalidad."
                )

                continue

            # =============================================
            # OLLAMA
            # =============================================

            candidates = self._extract(
                segment
            )

            # =============================================
            # VALIDAR CANDIDATOS
            # =============================================

            for candidate in candidates:

                requirement = self._validate(
                    candidate,
                    segment,
                    requirements
                )

                if requirement:

                    requirements.append(
                        requirement
                    )

                    print(
                        "✓ RF:",
                        requirement[
                            "description"
                        ]
                    )

        # =============================================
        # GUARDAR
        # =============================================

        self._save(
            interview,
            requirements
        )

        print()

        print(
            f"Agente 2 → "
            f"{len(requirements)} "
            "RF guardado(s)."
        )

        return requirements

    # =====================================================
    # DIVIDIR TRANSCRIPCIÓN
    # =====================================================

    def _split(
        self,
        text
    ):

        return [

            segment.strip()

            for segment in re.split(
                r"(?<=[.!?])\s+",
                text
            )

            if segment.strip()
        ]

    # =====================================================
    # ¿PUEDE CONTENER UNA FUNCIÓN?
    # =====================================================

    def _potential_function(
        self,
        segment
    ):

        text = self._normalize(
            segment
        )

        # Acción conocida.
        if self._actions(
            text
        ):

            return True

        # Expresiones generales.
        #
        # Permiten detectar funciones cuyos verbos
        # no están incluidos en ACTIONS.
        signals = (

            "el sistema debe",
            "el sistema debera",
            "el sistema tiene que",

            "el software debe",
            "el software debera",

            "la aplicacion debe",
            "la aplicacion debera",

            "la plataforma debe",
            "la plataforma debera",

            "debe poder",
            "deben poder",

            "debera poder",
            "deberan poder",

            "debe permitir",
            "debera permitir",

            "necesito que",
            "necesitamos que",

            "quiero que",
            "queremos que",

            "se requiere",
            "se necesita",

            "seria bueno que",

            "es necesario que",
            "es indispensable que",

            "tiene que permitir",

            "pueda",
            "puedan"
        )

        return any(
            signal in text
            for signal in signals
        )

    # =====================================================
    # EXTRAER CON OLLAMA
    # =====================================================

    def _extract(
        self,
        segment
    ):

        prompt = f"""
Eres un analista especializado en Ingeniería
de Requisitos de Software.

Analiza ÚNICAMENTE este fragmento de una entrevista:

{segment}

La entrevista puede pertenecer a CUALQUIER tipo
de proyecto, organización, sistema o dominio.

REGLAS OBLIGATORIAS:

1. Extrae exclusivamente REQUISITOS FUNCIONALES
   explícitamente expresados en este fragmento.

2. Un requisito funcional describe una acción,
   servicio o comportamiento que el software
   debe realizar.

3. NO inventes funcionalidades.

4. NO completes información ausente.

5. NO uses información de otras entrevistas.

6. NO uses información de otros proyectos.

7. NO supongas el dominio.

8. NO inventes actores.

9. NO inventes objetos ni entidades.

10. Conserva los conceptos expresados
    por el entrevistado.

11. Si existen varias acciones funcionales
    realmente independientes, devuelve
    varios requisitos.

12. NO dividas una misma acción funcional
    en varios requisitos únicamente porque
    contiene varios atributos, campos o datos.

Ejemplo conceptual:

"Registrar una entidad con nombre,
correo y teléfono."

Es UNA funcionalidad de registro.

NO son tres funcionalidades.

13. Una condición realizada por una persona
    NO constituye automáticamente otra
    funcionalidad del sistema.

Ejemplo conceptual:

"Si una persona solicita abandonar el servicio,
el sistema debe eliminar su registro."

La función del sistema es:

"eliminar su registro"

La solicitud de la persona es una condición.

14. Si dentro de una condición existe otra acción
    explícita que EL SISTEMA debe ejecutar,
    sí puede considerarse una funcionalidad.

15. NO conviertas información pendiente
    de definir en un requisito funcional.

Ejemplos:

"todavía no hemos definido..."
"falta definir..."
"no sabemos todavía..."

Esto representa información pendiente.

16. NO conviertas requisitos no funcionales
    en requisitos funcionales.

17. Ignora características de calidad aisladas:

- rapidez
- rendimiento
- apariencia
- diseño visual
- usabilidad
- disponibilidad
- escalabilidad
- mantenibilidad
- portabilidad
- confiabilidad
- accesibilidad

cuando únicamente describan una cualidad.

18. Una opinión o comentario sobre algo
    anteriormente mencionado NO constituye
    un nuevo requisito.

Ejemplo:

"Ese reporte es importante para nosotros."

NO genera un requisito.

19. Una descripción general del proyecto
    NO debe convertirse en operaciones que
    no fueron expresadas explícitamente.

Ejemplo:

"Necesito un sistema para gestionar X."

NO autoriza a inventar:

crear X
actualizar X
eliminar X
listar X

20. Ignora funcionalidades rechazadas
    explícitamente.

21. Redacta cada requisito preferentemente:

"El sistema deberá..."

22. actor solamente puede contener un actor
    mencionado explícitamente en este fragmento.

23. Si no existe actor explícito:

actor = ""

24. ambiguity_detected = true cuando falte
    información necesaria para precisar
    completamente el comportamiento.

25. verifiable = false cuando esa ambigüedad
    impida establecer una prueba objetiva.

26. NO generes códigos RF.

27. NO intentes generar una cantidad
    determinada de requisitos.

28. Si el fragmento no contiene ninguna
    funcionalidad explícita:

requirements = []

Devuelve exclusivamente JSON válido.
"""

        try:

            result = self.ollama.generate_json(
                prompt,
                self.SCHEMA
            )

            return result.get(
                "requirements",
                []
            ) or []

        except Exception as error:

            print(
                f"Error Ollama: {error}"
            )

            return []

    # =====================================================
    # VALIDAR CANDIDATO
    # =====================================================

    def _validate(
        self,
        candidate,
        source,
        current
    ):

        if not isinstance(
            candidate,
            dict
        ):

            return None

        description = str(
            candidate.get(
                "description",
                ""
            )
            or ""
        ).strip()

        actor = str(
            candidate.get(
                "actor",
                ""
            )
            or ""
        ).strip()

        if not description:

            return None

        # =================================================
        # NO FUNCIONAL
        # =================================================

        if self._pure_nfr(
            description
        ):

            print(
                "✗ descartado: "
                "no funcional"
            )

            return None

        # =================================================
        # FUNCIONALIDAD RECHAZADA
        # =================================================

        if self._rejected(
            description,
            source
        ):

            print(
                "✗ descartado: "
                "funcionalidad rechazada"
            )

            return None

        # =================================================
        # INFORMACIÓN PENDIENTE
        # =================================================

        if self._pending_function(
            description,
            source
        ):

            print(
                "✗ descartado: "
                "información pendiente "
                "convertida en RF"
            )

            return None

        # =================================================
        # ACCIÓN EXTERNA COMO CONDICIÓN
        # =================================================

        if self._condition_only_function(
            description,
            source
        ):

            print(
                "✗ descartado: "
                "acción externa utilizada "
                "únicamente como condición"
            )

            return None

        # =================================================
        # RESPALDO EN LA EVIDENCIA
        # =================================================

        if not self._supported(
            description,
            source
        ):

            print(
                "✗ descartado: "
                "el RF no está respaldado "
                "por este fragmento"
            )

            return None

        # =================================================
        # DUPLICADOS
        # =================================================

        if self._duplicate(
            description,
            current
        ):

            print(
                "✗ descartado: duplicado"
            )

            return None

        # =================================================
        # ACTOR
        # =================================================

        # Si Ollama devuelve actor,
        # debe existir realmente en la evidencia.
        if (
            actor
            and not self._actor_in_source(
                actor,
                source
            )
        ):

            actor = ""

        # Si Ollama no lo devuelve,
        # buscar únicamente actor explícito.
        if not actor:

            actor = self._explicit_actor(
                source
            )

        # =================================================
        # PRIORIDAD
        # =================================================

        priority, priority_reason = (
            self._priority(
                source
            )
        )

        # =================================================
        # AMBIGÜEDAD
        # =================================================

        ambiguity_reason = (
            self._ambiguity(
                source
            )
        )

        ambiguity = bool(
            candidate.get(
                "ambiguity_detected",
                False
            )
        )

        if ambiguity_reason:

            ambiguity = True

        if not ambiguity:

            ambiguity_reason = (
                "No se identificaron "
                "ambigüedades relevantes."
            )

        elif not ambiguity_reason:

            ambiguity_reason = str(
                candidate.get(
                    "ambiguity_reason",
                    ""
                )
                or
                "La funcionalidad requiere "
                "mayor precisión."
            )

        # =================================================
        # VERIFICABILIDAD
        # =================================================

        verifiable = bool(
            candidate.get(
                "verifiable",
                True
            )
        )

        if ambiguity:

            verifiable = False

        if verifiable:

            verification_reason = (
                "El comportamiento puede "
                "comprobarse mediante una "
                "prueba funcional."
            )

        else:

            verification_reason = (
                "La información disponible no "
                "permite establecer completamente "
                "un criterio objetivo de verificación."
            )

        return {

            "description":
                description,

            "actor":
                actor or None,

            "priority":
                priority,

            "priority_reason":
                priority_reason,

            "source_excerpt":
                source,

            "ambiguity_detected":
                ambiguity,

            "ambiguity_reason":
                ambiguity_reason,

            "verifiable":
                verifiable,

            "verification_reason":
                verification_reason
        }

    # =====================================================
    # RESPALDO CONTRA EL FRAGMENTO
    # =====================================================

    def _supported(
        self,
        description,
        source
    ):

        candidate_action = (
            self._action(
                description
            )
        )

        source_actions = (
            self._actions(
                source
            )
        )

        # ACTIONS no es una lista cerrada.
        #
        # Solo comparamos acciones cuando
        # ambas partes contienen acciones conocidas.
        if (
            candidate_action
            and source_actions
            and candidate_action
            not in source_actions
        ):

            return False

        candidate_words = (
            self._content_words(
                description
            )
        )

        source_words = (
            self._content_words(
                source
            )
        )

        if not candidate_words:

            return bool(
                candidate_action
                and candidate_action
                in source_actions
            )

        common = (
            candidate_words
            & source_words
        )

        if not common:

            return False

        return True

    # =====================================================
    # ACCIÓN EXTERNA USADA COMO CONDICIÓN
    # =====================================================

    def _condition_only_function(
        self,
        description,
        source
    ):

        text = self._normalize(
            source
        )

        candidate_action = (
            self._action(
                description
            )
        )

        if not candidate_action:

            return False

        condition_markers = (
            "si ",
            "cuando ",
            "en caso de "
        )

        condition_position = None

        for marker in condition_markers:

            position = text.find(
                marker
            )

            if position >= 0:

                if (
                    condition_position is None
                    or position
                    < condition_position
                ):

                    condition_position = (
                        position
                    )

        if condition_position is None:

            return False

        system_markers = (
            "el sistema ",
            "el software ",
            "la aplicacion ",
            "la plataforma "
        )

        system_position = None

        for marker in system_markers:

            position = text.find(
                marker,
                condition_position + 1
            )

            if position >= 0:

                if (
                    system_position is None
                    or position
                    < system_position
                ):

                    system_position = (
                        position
                    )

        if system_position is None:

            return False

        condition_part = text[
            condition_position:
            system_position
        ]

        system_part = text[
            system_position:
        ]

        condition_actions = (
            self._actions(
                condition_part
            )
        )

        system_actions = (
            self._actions(
                system_part
            )
        )

        return (
            candidate_action
            in condition_actions
            and candidate_action
            not in system_actions
        )

    # =====================================================
    # ACTOR EXPLÍCITO
    # =====================================================

    def _explicit_actor(
        self,
        source
    ):

        text = str(
            source or ""
        ).strip()

        if not text:

            return ""

        # =================================================
        # SOLO ACTORES EXPLÍCITOS
        # =================================================
        #
        # Ejemplos válidos:
        #
        # El bibliotecario debe registrar...
        # Los estudiantes deben consultar...
        # La secretaria puede registrar...
        # El administrador deberá aprobar...
        #
        # IMPORTANTE:
        #
        # El patrón NO puede atravesar:
        #
        # ,
        # .
        # ;
        # :
        # ?
        # !
        #
        # Esto evita errores como:
        #
        # "los préstamos de libros, aunque todavía
        # no hemos definido qué datos se deben..."
        #
        # =================================================

        pattern = (
            r"\b(?:el|la|los|las)\s+"
            r"([^,.;:!?]{1,50}?)\s+"
            r"(?:"
            r"debe|deben|"
            r"deberá|deberán|"
            r"puede|pueden|"
            r"podrá|podrán|"
            r"pueda|puedan|"
            r"necesita|necesitan|"
            r"tiene que|tienen que"
            r")\b"
        )

        matches = re.finditer(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        for match in matches:

            actor = (
                match.group(1)
                .strip()
            )

            normalized = self._normalize(
                actor
            )

            # El sistema no es un actor humano
            # o externo del requisito.
            if normalized in {
                "sistema",
                "software",
                "aplicacion",
                "plataforma"
            }:

                continue

            # Evitar construcciones pasivas:
            #
            # "los datos se deben guardar"
            #
            # Aquí "datos se" NO es un actor.
            if (
                normalized == "se"
                or normalized.endswith(" se")
            ):

                continue

            return actor

        return ""

    # =====================================================
    # PRIMERA ACCIÓN
    # =====================================================

    def _action(
        self,
        text
    ):

        text = self._normalize(
            text
        )

        words = re.findall(
            r"[a-z0-9]+",
            text
        )

        best_action = None
        best_position = 999999

        for action, patterns in (
            self.ACTIONS.items()
        ):

            for pattern in patterns:

                for position, word in enumerate(
                    words
                ):

                    if word.startswith(
                        pattern
                    ):

                        if position < best_position:

                            best_action = (
                                action
                            )

                            best_position = (
                                position
                            )

        return best_action

    # =====================================================
    # TODAS LAS ACCIONES
    # =====================================================

    def _actions(
        self,
        text
    ):

        words = re.findall(
            r"[a-z0-9]+",
            self._normalize(
                text
            )
        )

        result = set()

        for action, patterns in (
            self.ACTIONS.items()
        ):

            if any(

                word.startswith(
                    pattern
                )

                for word in words

                for pattern in patterns
            ):

                result.add(
                    action
                )

        return result

    # =====================================================
    # PALABRAS DE CONTENIDO
    # =====================================================

    def _content_words(
        self,
        text
    ):

        stopwords = {

            "el",
            "la",
            "los",
            "las",

            "un",
            "una",

            "de",
            "del",

            "al",
            "a",

            "en",
            "con",

            "por",
            "para",

            "y",
            "o",

            "que",

            "su",
            "sus",

            "este",
            "esta",

            "sistema",
            "software",
            "aplicacion",
            "plataforma",

            "debe",
            "deben",
            "debera",
            "deberan",

            "permitir",

            "puede",
            "pueda",
            "puedan",

            "poder",

            "necesito",
            "necesitamos",

            "quiero",
            "queremos"
        }

        action_patterns = {

            pattern

            for patterns
            in self.ACTIONS.values()

            for pattern
            in patterns
        }

        result = set()

        for word in re.findall(
            r"[a-z0-9]+",
            self._normalize(
                text
            )
        ):

            if word in stopwords:

                continue

            if len(
                word
            ) < 4:

                continue

            if any(

                word.startswith(
                    pattern
                )

                for pattern
                in action_patterns
            ):

                continue

            result.add(
                self._stem(
                    word
                )
            )

        return result

    # =====================================================
    # INFORMACIÓN PENDIENTE
    # =====================================================

    def _pending_function(
        self,
        description,
        source
    ):

        text = self._normalize(
            source
        )

        markers = (

            "no hemos definido",

            "no se ha definido",

            "todavia no hemos definido",

            "aun no hemos definido",

            "falta definir",

            "queda por definir",

            "todavia no sabemos",

            "aun no sabemos"
        )

        positions = [

            text.find(
                marker
            )

            for marker
            in markers

            if text.find(
                marker
            ) >= 0
        ]

        if not positions:

            return False

        position = min(
            positions
        )

        before = text[
            :position
        ]

        pending = text[
            position:
        ]

        action = self._action(
            description
        )

        if not action:

            return False

        return (
            action
            in self._actions(
                pending
            )
            and
            action
            not in self._actions(
                before
            )
        )

    # =====================================================
    # FUNCIONALIDAD RECHAZADA
    # =====================================================

    def _rejected(
        self,
        description,
        source
    ):

        text = self._normalize(
            source
        )

        markers = (

            "no necesitamos",

            "no queremos",

            "no requerimos",

            "no hace falta"
        )

        if not any(

            marker in text

            for marker
            in markers
        ):

            return False

        if any(

            contrast in text

            for contrast in (

                " pero ",

                " aunque ",

                " sin embargo "
            )
        ):

            return False

        action = self._action(
            description
        )

        return bool(

            action

            and action
            in self._actions(
                source
            )
        )

    # =====================================================
    # REQUISITO NO FUNCIONAL
    # =====================================================

    def _pure_nfr(
        self,
        description
    ):

        text = self._normalize(
            description
        )

        patterns = (

            # Rendimiento
            r"\bresponder\b.*\b(?:rapido|rapida)\b",

            r"\bfuncionar\b.*\b(?:rapido|rapida)\b",

            r"\btiempo de respuesta\b",

            # Interfaz / apariencia
            r"\binterfaz\s+(?:moderna|amigable)\b",

            r"\bfacil de usar\b",

            # Calidad general
            r"\b(?:ser|debe ser|debera ser)\b.*"
            r"\b(?:rapido|rapida|escalable|"
            r"confiable|mantenible|portable|"
            r"accesible)\b",

            # Disponibilidad
            r"\b(?:alta )?disponibilidad\b",

            # Propiedades generales
            r"\b(?:tener|contar con)\b.*"
            r"\b(?:escalabilidad|mantenibilidad|"
            r"portabilidad|confiabilidad)\b"
        )

        return any(

            re.search(
                pattern,
                text
            )

            for pattern
            in patterns
        )

    # =====================================================
    # DUPLICADOS
    # =====================================================

    def _duplicate(
        self,
        description,
        current
    ):

        normalized = (
            self._normalize(
                description
            )
        )

        for item in current:

            existing = (
                self._normalize(
                    item[
                        "description"
                    ]
                )
            )

            similarity = (
                SequenceMatcher(
                    None,
                    normalized,
                    existing
                ).ratio()
            )

            if similarity >= 0.88:

                return True

        return False

    # =====================================================
    # VALIDAR ACTOR
    # =====================================================

    def _actor_in_source(
        self,
        actor,
        source
    ):

        actor_words = (
            self._content_words(
                actor
            )
        )

        source_words = (
            self._content_words(
                source
            )
        )

        if not actor_words:

            return False

        return bool(
            actor_words
            & source_words
        )

    # =====================================================
    # PRIORIDAD
    # =====================================================

    def _priority(
        self,
        source
    ):

        text = self._normalize(
            source
        )

        # =============================================
        # ESENCIAL
        # =============================================

        if any(

            marker in text

            for marker in (

                "indispensable",

                "obligatorio",
                "obligatoria",

                "esencial",

                "fundamental",

                "critico",
                "critica"
            )
        ):

            return (
                "esencial",

                "La entrevista expresa "
                "una prioridad esencial."
            )

        # =============================================
        # OPCIONAL
        # =============================================

        if any(

            marker in text

            for marker in (

                "seria bueno",

                "opcional",

                "podria incluirse",

                "podria tener"
            )
        ):

            return (
                "opcional",

                "La entrevista presenta la "
                "funcionalidad como opcional."
            )

        # =============================================
        # CONDICIONAL
        # =============================================

        if any(

            marker in text

            for marker in (

                "solo si",

                "en caso de",

                "dependiendo de"
            )
        ):

            return (
                "condicional",

                "La funcionalidad depende "
                "de una condición."
            )

        # =============================================
        # NO ESPECIFICADA
        # =============================================

        return (
            "no_especificada",

            "La entrevista no expresa "
            "una prioridad explícita."
        )

    # =====================================================
    # AMBIGÜEDAD
    # =====================================================

    def _ambiguity(
        self,
        source
    ):

        text = self._normalize(
            source
        )

        # =============================================
        # INFORMACIÓN PENDIENTE
        # =============================================

        pending = (

            "no hemos definido",

            "no se ha definido",

            "todavia no hemos definido",

            "aun no hemos definido",

            "falta definir",

            "queda por definir",

            "todavia no sabemos",

            "aun no sabemos"
        )

        if any(

            marker in text

            for marker
            in pending
        ):

            return (
                "La entrevista indica que existe "
                "información necesaria todavía "
                "sin definir."
            )

        # =============================================
        # EXPRESIONES VAGAS
        # =============================================

        vague = {

            "proximo":
                "No se especifica qué se "
                "considera próximo.",

            "rapido":
                "No se establece una medida "
                "objetiva de rapidez.",

            "facil":
                "No se establece un criterio "
                "objetivo de facilidad.",

            "adecuado":
                "No se define qué se "
                "considera adecuado.",

            "frecuentemente":
                "No se define una frecuencia.",

            "normalmente":
                "No se definen las condiciones "
                "exactas.",

            "lo antes posible":
                "No se establece un tiempo máximo."
        }

        for marker, reason in (
            vague.items()
        ):

            if marker in text:

                return reason

        return ""

    # =====================================================
    # STEM SIMPLE
    # =====================================================

    def _stem(
        self,
        word
    ):

        if (
            word.endswith(
                "es"
            )
            and len(
                word
            ) > 6
        ):

            return word[
                :-2
            ]

        if (
            word.endswith(
                "s"
            )
            and len(
                word
            ) > 5
        ):

            return word[
                :-1
            ]

        return word

    # =====================================================
    # NORMALIZAR
    # =====================================================

    def _normalize(
        self,
        text
    ):

        text = str(
            text
            or ""
        ).lower()

        text = unicodedata.normalize(
            "NFD",
            text
        )

        text = "".join(

            character

            for character
            in text

            if unicodedata.category(
                character
            ) != "Mn"
        )

        return re.sub(
            r"\s+",
            " ",
            text
        ).strip()

    # =====================================================
    # GUARDAR
    # =====================================================

    def _save(
        self,
        interview,
        requirements
    ):

        # =================================================
        # BORRAR SOLO RF DE ESTA ENTREVISTA
        # =================================================

        Requirement.query.filter_by(
            interview_id=interview.id
        ).delete()

        db.session.flush()

        # =================================================
        # MANTENER RF DE LAS OTRAS ENTREVISTAS
        # DEL MISMO PROYECTO
        # =================================================

        existing = (

            Requirement.query

            .filter_by(
                project_id=
                    interview.project_id
            )

            .all()
        )

        max_number = 0

        for item in existing:

            try:

                number = int(
                    item.code.replace(
                        "RF-",
                        ""
                    )
                )

                max_number = max(
                    max_number,
                    number
                )

            except Exception:

                pass

        # =================================================
        # GUARDAR RF DE ESTA ENTREVISTA
        # =================================================

        for data in requirements:

            max_number += 1

            requirement = Requirement(

                project_id=
                    interview.project_id,

                interview_id=
                    interview.id,

                code=
                    f"RF-{max_number:03d}",

                description=
                    data[
                        "description"
                    ],

                actor=
                    data[
                        "actor"
                    ],

                priority=
                    data[
                        "priority"
                    ],

                priority_reason=
                    data[
                        "priority_reason"
                    ],

                source_excerpt=
                    data[
                        "source_excerpt"
                    ],

                ambiguity_detected=
                    data[
                        "ambiguity_detected"
                    ],

                ambiguity_reason=
                    data[
                        "ambiguity_reason"
                    ],

                verifiable=
                    data[
                        "verifiable"
                    ],

                verification_reason=
                    data[
                        "verification_reason"
                    ]
            )

            db.session.add(
                requirement
            )

        db.session.commit()