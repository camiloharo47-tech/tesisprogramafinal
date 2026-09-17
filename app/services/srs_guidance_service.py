"""Project-specific editorial guidance, never extracted or approved requirements."""


class SRSGuidanceService:
    MARKER = "(Fuera del alcance de la tesis)"

    def build(self, project, requirements):
        name = project.get("name") or "el proyecto"
        actors = list(dict.fromkeys(r.get("actor") for r in requirements if r.get("actor")))
        users = ", ".join(actors) if actors else "los usuarios responsables de las operaciones descritas en los RF"
        examples = "; ".join(f"{r.get('code', 'RF')}: {r.get('description', '')}" for r in requirements[:3])
        operations = ", ".join(r.get("code", "RF") for r in requirements[:3]) or "los RF identificados"
        description = project.get("description") or "El alcance funcional se describe mediante los RF identificados en las entrevistas."
        return {
            "purpose": f"Esta especificación de {name} reúne los requisitos funcionales identificados en las entrevistas. Está dirigida a los responsables del proyecto, analistas, desarrolladores y evaluadores. Las secciones complementarias ofrecen una guía de documentación pendiente de validación.",
            "scope": f"El sistema {name} se delimita por los RF de la sección 3.2. Descripción registrada: {description} Como objetivo orientativo, se propone apoyar la ejecución y organización de esas operaciones; no se consideran aprobadas otras funcionalidades ni beneficios cuantificados.",
            "product_perspective": f"Se propone describir {name} como una solución de apoyo a los procesos representados en sus RF. Antes del diseño, se confirmaría si funcionará de manera independiente o integrado con otros productos, identificando los datos intercambiados y las responsabilidades de cada sistema.",
            "users": f"Los actores identificados son: {users}. Como perfil orientativo, se considera conocimiento de las tareas del dominio y manejo básico de aplicaciones. El nivel educativo, la experiencia técnica y las necesidades de capacitación se confirmarían con cada grupo de usuarios.",
            "constraints": f"Para {name}, se propone revisar las políticas de la organización, los recursos disponibles, el presupuesto, los permisos de acceso y las condiciones de operación de {operations}. Las tecnologías, equipos y restricciones obligatorias deberán acordarse antes de la implementación; este documento no las da por confirmadas.",
            "assumptions": f"Como hipótesis de trabajo para {name}, se supone que los responsables facilitarán datos representativos y participarán en la validación de los RF. La disponibilidad de infraestructura y de posibles sistemas externos se comprobaría antes del despliegue. Un cambio en los procesos, actores o datos requeriría revisar la especificación.",
            "future": f"En una evolución de {name}, podrían estudiarse mejoras de usabilidad, ampliación de capacidad e integraciones que se justifiquen mediante nuevas entrevistas. Cada propuesta tendría que evaluarse y priorizarse por separado; no se incorpora como un RF aprobado en esta versión.",
            "interfaces": f"Para {name}, se propone documentar las entradas, salidas y mensajes vinculados con sus funciones. Operaciones de referencia: {examples}. Los siguientes puntos son orientaciones de diseño, no interfaces confirmadas.",
            "user_interface": f"Como propuesta para {name}, las pantallas presentarían de manera comprensible las operaciones de {operations}, los datos solicitados y el resultado de cada acción. Los prototipos, mensajes de validación y necesidades de accesibilidad se revisarían con {users}.",
            "hardware_interface": f"Se propone comprobar que los dispositivos destinados a operar {name} dispongan de recursos suficientes para las tareas de los RF. El inventario de equipos, periféricos y capacidades mínimas se definiría a partir del entorno real, sin asumir hardware especializado.",
            "software_interface": f"En caso de que {name} intercambie información con otros programas, se propone documentar el sistema de origen y destino, los formatos y el tratamiento de errores. La necesidad de tales integraciones se validaría antes de elegir productos, bases de datos o API.",
            "communications": f"Si {name} se utiliza mediante una red, se propone describir los canales, las condiciones de conectividad y la protección de los intercambios. Los protocolos y el comportamiento ante interrupciones se determinarían según el entorno acordado.",
            "performance": f"Para {name}, se propone evaluar el tiempo de respuesta de operaciones como {operations}, la concurrencia de usuarios y el crecimiento de los datos. Las pruebas utilizarían cargas representativas de las tareas de {users}. Los umbrales de aceptación, volúmenes de registros y transacciones por unidad de tiempo se acordarían con los responsables; no se presentan cifras supuestas como compromisos.",
            "design": f"Como orientación para el diseño de {name}, se propone separar la presentación, las reglas de las operaciones y el acceso a datos para facilitar cambios en los RF. La arquitectura definitiva, los lenguajes, las plataformas y las normas aplicables se decidirían según las restricciones verificadas del proyecto.",
            "quality": f"Para {name}, se proponen las siguientes líneas de evaluación de calidad, sujetas a definición y validación posteriores:",
            "reliability": f"Fiabilidad: evaluar la consistencia de los resultados de {operations} y definir cómo recuperar la operación después de fallos, evitando pérdida o duplicación de información.",
            "availability": f"Disponibilidad: acordar el horario de servicio de {name}, las ventanas de mantenimiento y los procedimientos de recuperación según las necesidades de sus usuarios.",
            "security": f"Seguridad: estudiar una matriz de permisos para {users}, mecanismos de identificación y protección de los datos según su sensibilidad. Los controles concretos no se consideran requisitos confirmados.",
            "maintainability": f"Mantenibilidad: proponer documentación de las reglas de {name} y pruebas que ayuden a revisar el impacto de cambios en los RF.",
            "portability": f"Portabilidad: identificar los entornos en los que se necesitaría ejecutar {name} y evaluar su compatibilidad antes de comprometer soporte para plataformas específicas.",
            "other": f"Como aspectos complementarios de {name}, se propone acordar documentación de uso, capacitación, conservación de datos y criterios de entrega. Su pertinencia y los requisitos legales u organizativos aplicables se revisarían con los responsables del proyecto.",
            "appendices": f"Como documentación adicional de {name}, podrían adjuntarse ejemplos de entradas y salidas asociados con {operations}, un glosario del dominio, prototipos y estimaciones de recursos. Estos materiales se elaborarían y validarían en una etapa posterior; no se presentan como anexos existentes.",
        }
