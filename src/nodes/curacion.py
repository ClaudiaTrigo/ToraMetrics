"""
Nodo: Curación y Estrategia.

Responsabilidad futura: filtrar `resultados_busqueda`, elegir el
`tema_elegido` con mayor potencial de engagement y definir la
`estructura_narrativa` (ej. Gancho -> Retención -> CTA) según la
`plataforma`.

Por ahora es un stub sin lógica real.
"""

from __future__ import annotations

import logging

from src.state import EstadoGrafo

logger = logging.getLogger(__name__)


def curar_y_definir_estrategia(state: EstadoGrafo) -> dict:
    logger.info("Nodo Curación y Estrategia: plataforma=%s (stub)", state.plataforma)
    # TODO(Milestone 2): elegir tema_elegido y estructura_narrativa
    return {}
