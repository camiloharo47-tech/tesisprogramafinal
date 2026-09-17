from app.services.ollama_service import OllamaService


ollama = OllamaService()

response = ollama.generate(
    """
    Responde solamente con una oración.

    Redacta un requisito funcional para un sistema
    que permita registrar clientes.
    """
)

print(response)