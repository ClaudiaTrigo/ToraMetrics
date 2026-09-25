"""
Servicio: integración con la API de Tavily.

Esta capa aísla toda la lógica de infraestructura externa (llamar a Tavily,
manejar reintentos, parsear su respuesta) para que el nodo de Investigación
del grafo (src/nodes/investigacion.py) no tenga que saber nada sobre cómo
se comunica con Tavily -- solo le pide "dame tendencias de este nicho" y
recibe una lista de ResultadoBusqueda ya validada.

Diseño acordado (revisado 2026-09-25, ver docs/DECISIONS.md):
- topic="general": se probó topic="news" (índice periodístico/editorial de
  Tavily) para evitar posts sueltos de redes sociales, pero sus scores de
  relevancia resultaron estructuralmente más bajos -- en pruebas manuales,
  ningún resultado con topic="news" superó 0.47, mientras que con
  topic="general" se vieron resultados de hasta 0.83. La guía oficial de
  Tavily recomienda `score > 0.7` como punto de partida razonable, y ese
  rango solo es alcanzable con topic="general". Se decidió volver a
  "general" y resolver el ruido de redes sociales con exclude_domains
  en su lugar (ver abajo), no con el topic.
- country="spain" (reactivado 2026-09-25): solo funciona con
  topic="general" (verificado en la documentación oficial) -- se había
  quitado al probar topic="news" y quedó sin reactivar por error al volver
  a "general", lo que dejó pasar resultados de otros países (ej. Perú) sin
  querer. Corregido: vuelve a estar activo.
- exclude_domains: bloquea explícitamente tiktok.com, instagram.com,
  facebook.com, youtube.com, reddit.com y pinterest.com -- las plataformas
  que en pruebas manuales devolvían posts sueltos sin contenido real
  (hashtags genéricos, sin texto sustancial). YouTube se añadió el
  2026-09-25 (decisión de Claudia) tras verse en las pruebas resultados
  como transmisiones en vivo o shorts con solo hashtags en la descripción.
  X/Twitter, Threads y LinkedIn se dejan fuera de esta lista a propósito
  -- decisión de Claudia (2026-09-25): sí quiere que esas plataformas
  puedan aparecer como fuente.
- Sin filtro de score: se probó un umbral mínimo (incluso el `score > 0.7`
  que recomienda la guía oficial de Tavily) y en ambos casos descartó
  resultados reales y relevantes -- incluida cobertura de una competición
  de surf reciente -- mientras dejaba pasar spam con score alto (una
  página con contenido irrelevante llegó a 0.90 solo por repetir palabras
  de la query). El score mide coincidencia de texto con la IA propietaria
  de Tavily, no calidad editorial ni que algo sea realmente una tendencia
  (ver docs/DECISIONS.md para el detalle). Juzgar relevancia real es
  trabajo del nodo de Curación con Gemini, no de un filtro mecánico aquí.
- Query = "noticias de {nicho}" (cambiado 2026-09-25, antes "tendencias
  virales en {nicho}"): la query vieja nunca calzaba con cómo se escribe
  periodismo real -- una noticia sobre el resultado de una competición no
  se autodescribe como "tendencia viral", así que Tavily (que puntúa por
  coincidencia de texto, ver arriba) siempre prefería listicles genéricos
  de "tendencias 2026" sobre la noticia real y relevante. Verificado con
  un caso real: la cobertura de Nadia Erostarbe en la WSL no aparecía con
  la query vieja pero sí con "noticias de surf" (score 0.7+). Pendiente a
  futuro (no implementado aún): un campo `modo_busqueda` en el estado,
  elegido por el usuario en el frontend (desplegable con opciones como
  "tendencias", "noticias", "curiosidades"...), que mapee a distintas
  plantillas de query -- "noticias de {nicho}" queda como default único
  mientras tanto.
- time_range="month": acota la ventana temporal a resultados recientes.
- Reintentos automáticos con tenacity: absorben fallos transitorios de red
  (timeouts, rate limits puntuales) antes de darse por vencido.
- Si Tavily responde pero sin resultados, NO es un error: se devuelve una
  lista vacía. Solo se relanza una excepción si los reintentos se agotan
  sin conseguir respuesta -- decidir qué hacer con ese fallo le corresponde
  a quien llama a esta función (el nodo), no a este servicio.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from tavily import TavilyClient
from tenacity import retry, stop_after_attempt, wait_exponential

from src.state import ResultadoBusqueda

load_dotenv()

_SEARCH_DEPTH = "advanced"
_TOPIC = "general"
_TIME_RANGE = "month"
_DOMINIOS_EXCLUIDOS = [
    "tiktok.com",
    "instagram.com",
    "facebook.com",
    "youtube.com",
    "reddit.com",
    "pinterest.com",
]
_PAIS_POR_DEFECTO = "spain"


def _crear_cliente() -> TavilyClient:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise RuntimeError("TAVILY_API_KEY no está definida. Revisa tu archivo .env.")
    return TavilyClient(api_key=api_key)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    reraise=True,
)
def _buscar_en_tavily(cliente: TavilyClient, query: str, max_results: int) -> dict:
    """Llama a Tavily con reintentos (hasta 3 intentos, con backoff
    exponencial). Si los 3 fallan, relanza la última excepción tal cual
    (reraise=True) para que buscar_tendencias() -- y en última instancia el
    nodo de Investigación -- decida qué hacer con el fallo."""
    return cliente.search(
        query=query,
        search_depth=_SEARCH_DEPTH,
        topic=_TOPIC,
        time_range=_TIME_RANGE,
        max_results=max_results,
        exclude_domains=_DOMINIOS_EXCLUIDOS,
        country=_PAIS_POR_DEFECTO,
    )


def buscar_tendencias(nicho: str, max_results: int = 8) -> list[ResultadoBusqueda]:
    """Busca noticias/tendencias recientes sobre un nicho usando Tavily,
    priorizando fuentes periodísticas y de blogs (topic="news") sobre
    redes sociales.

    Devuelve una lista de ResultadoBusqueda (puede estar vacía si Tavily no
    encontró nada -- eso no se considera un error). No se filtra por score:
    en pruebas manuales, el score de Tavily resultó ser una señal de
    coincidencia de texto con la query, no de calidad real -- páginas con
    contenido irrelevante o de spam sacaban scores altos (hasta 0.90) por
    repetir las palabras de la query, mientras que noticias genuinas podían
    quedar con scores bajos. Filtrar por score llegó a descartar resultados
    reales (ej. cobertura de una competición de surf reciente) mientras
    dejaba pasar spam. Juzgar relevancia real es trabajo del nodo de
    Curación (lee el contenido con Gemini), no de este filtro mecánico. Si
    Tavily falla incluso tras los reintentos, la excepción sube tal cual:
    esta función no la atrapa.
    """
    cliente = _crear_cliente()
    query = f"noticias de {nicho}"

    respuesta = _buscar_en_tavily(cliente, query, max_results)
    resultados_crudos = respuesta.get("results", [])

    return [
        ResultadoBusqueda(
            titulo=r["title"],
            url=r["url"],
            contenido=r["content"],
            score=r.get("score"),
            fecha=r.get("published_date"),
        )
        for r in resultados_crudos
    ]
