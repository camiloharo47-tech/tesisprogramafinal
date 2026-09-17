from app.mcp.client import (
    MCPClient
)


client = MCPClient()


# =====================================================
# PRUEBA 1
# =====================================================

print()
print(
    "=== PRUEBA MCP DATABASE ==="
)

result = (
    client.ping_database()
)

print(
    "PING:"
)

print(
    result
)


# =====================================================
# PRUEBA 2
# =====================================================

print()
print(
    "=== ENTREVISTA ==="
)

interview = (
    client.get_interview(
        1
    )
)

print(
    interview
)


# =====================================================
# PRUEBA 3
# =====================================================

print()
print(
    "=== REQUISITOS ==="
)

requirements = (
    client.get_requirements(
        1
    )
)

print(
    requirements
)