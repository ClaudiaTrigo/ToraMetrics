"""
Nodo: Investigación.

Responsabilidad futura (Milestone 2, siguiente tarea): llamar a la API de
Tavily con el `nicho` del estado y guardar los resultados en
`resultados_busqueda`.

Por ahora es un stub sin lógica real: solo confirma que el nodo se
ejecuta dentro del grafo y no rompe el flujo.
"""

from __future__ import annotations

import logging

from src.state import EstadoGrafo

logger = logging.getLogger(__name__)


def investigar(state: EstadoGrafo) -> dict:
    logger.info("Nodo Investigación: nicho=%s (stub, sin llamada real a Tavily)", state.nicho)
    # TODO(Milestone 2): integrar Tavily y poblar resultados_busqueda
    return {}
