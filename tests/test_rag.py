from app.agents.enrichment_agent import (
    EnrichmentAgent
)


# =====================================================
# CONFIGURACIÓN
# =====================================================

INTERVIEW_ID = 1


# =====================================================
# EJECUTAR AGENTE 3
# =====================================================

agent = EnrichmentAgent()


print()
print(
    "========================================"
)

print(
    "PRUEBA AGENTE 3 + RAG"
)

print(
    "========================================"
)


results = agent.process_interview(
    INTERVIEW_ID
)


# =====================================================
# MOSTRAR RESULTADOS
# =====================================================

for result in results:

    print()
    print(
        "=" * 60
    )

    print(
        result.get(
            "code"
        )
    )


    context = result.get(
        "context",
        {}
    )


    print()
    print(
        "CONSULTA:"
    )

    print(
        context.get(
            "query"
        )
    )


    print()
    print(
        "CONTEXTO ENRIQUECIDO:"
    )

    print(
        context.get(
            "summary"
        )
    )


    print()
    print(
        "HECHOS:"
    )


    for fact in context.get(
        "facts",
        []
    ):

        print(
            "-"
        )

        print(
            fact.get(
                "text"
            )
        )

        print(
            "Evidencia:"
        )

        print(
            fact.get(
                "evidence"
            )
        )


    print()
    print(
        "FUENTES:"
    )


    for source in context.get(
        "sources",
        []
    ):

        print(
            "-"
        )

        print(
            source.get(
                "title"
            )
        )

        print(
            source.get(
                "url"
            )
        )