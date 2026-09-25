"""
Nodo: Investigación.

Responsabilidad: llamar al servicio de Tavily (src/services/tavily_service.py)
con el `nicho` del estado y poblar `resultados_busqueda`.

Diseño acordado (Milestone 2, plan del nodo de Investigación):
- Si Tavily falla incluso tras los reintentos automáticos que ya maneja
  tavily_service.buscar_tendencias(), este nodo NO deja que el error tumbe
  el grafo: lo captura, lo registra en el log, y devuelve una lista vacía.
  Un fallo de un proveedor externo no debería romper la generación de
  contenido completa para el usuario.
- Si Tavily responde pero no encuentra nada, eso ya viene como lista vacía
  desde el servicio -- no es un caso de error, simplemente se loguea junto
  con el resto de métricas (nº de resultados = 0).
"""

from __future__ import annotations

import logging
import time

from src.services.tavily_service import buscar_tendencias
from src.state import EstadoGrafo

logger = logging.getLogger(__name__)


def investigar(state: EstadoGrafo) -> dict:
    inicio = time.perf_counter()

    try:
        resultados = buscar_tendencias(state.nicho)
    except Exception:
        tiempo_transcurrido = time.perf_counter() - inicio
        logger.error(
            "Nodo Investigación: fallo al buscar tendencias para nicho=%r "
            "(tiempo transcurrido=%.2fs). Se continúa con resultados_busqueda "
            "vacío.",
            state.nicho,
            tiempo_transcurrido,
            exc_info=True,
        )
        return {"resultados_busqueda": []}

    tiempo_transcurrido = time.perf_counter() - inicio
    logger.info(
        "Nodo Investigación: nicho=%r -> %d resultado(s) en %.2fs",
        state.nicho,
        len(resultados),
        tiempo_transcurrido,
    )
    return {"resultados_busqueda": resultados}
