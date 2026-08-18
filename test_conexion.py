"""
Script de prueba de conexión — Milestone 1, ToraMetrics
Verifica que las credenciales de Gemini y Tavily funcionan correctamente,
de forma aislada, antes de construir el grafo del agente con LangGraph.
"""

import os
from dotenv import load_dotenv

# 1. Cargar las variables definidas en el archivo .env al entorno del proceso
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


def probar_gemini() -> bool:
    print("\n--- Probando conexión con Gemini ---")
    if not GOOGLE_API_KEY:
        print("❌ No se encontró GOOGLE_API_KEY en el archivo .env")
        return False

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI

        llm = ChatGoogleGenerativeAI(
            model="gemini-3.6-flash",
            google_api_key=GOOGLE_API_KEY,
        )
        respuesta = llm.invoke("Responde únicamente con la palabra: OK")
        # .content puede ser str o una lista de bloques según el modelo;
        # .text normaliza ambos casos a texto plano.
        texto = str(respuesta.text).strip()
        print(f"✅ Gemini respondió correctamente: {texto}")
        return True
    except Exception as e:
        print(f"❌ Error al conectar con Gemini: {e}")
        return False


def probar_tavily() -> bool:
    print("\n--- Probando conexión con Tavily ---")
    if not TAVILY_API_KEY:
        print("❌ No se encontró TAVILY_API_KEY en el archivo .env")
        return False

    try:
        from tavily import TavilyClient

        cliente = TavilyClient(api_key=TAVILY_API_KEY)
        resultado = cliente.search(
            query="noticias de inteligencia artificial hoy",
            max_results=1,
        )
        titulo = resultado["results"][0]["title"]
        print(f"✅ Tavily respondió correctamente. Primer resultado: {titulo}")
        return True
    except Exception as e:
        print(f"❌ Error al conectar con Tavily: {e}")
        return False


if __name__ == "__main__":
    gemini_ok = probar_gemini()
    tavily_ok = probar_tavily()

    print("\n--- Resumen ---")
    print(f"Gemini: {'OK' if gemini_ok else 'FALLÓ'}")
    print(f"Tavily: {'OK' if tavily_ok else 'FALLÓ'}")

    if gemini_ok and tavily_ok:
        print("\n🎉 Todo listo. Milestone 1 completado — podemos pasar a construir el grafo.")
    else:
        print("\n⚠️ Revisa las claves en tu archivo .env antes de continuar.")