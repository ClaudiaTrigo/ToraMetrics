"""
Nodo: Evaluación.

Responsabilidad futura: juzgar si `guion` cumple las reglas de la
`plataforma` (duración estimada, fuerza del gancho inicial, claridad del
CTA, coherencia) y devolver un `ResultadoEvaluacion` con `aprobado` y
`feedback`.

Por ahora es un stub: aprueba automáticamente en el primer intento para
que el grafo mínimo termine (Fin) sin necesitar lógica real ni llamadas
al LLM. Esto permite comprobar tanto el camino feliz como, cambiando
`SIEMPRE_APROBAR` a False, el ciclo de reintento hacia Redacción.
"""

from __future__ import annotations

import logging

from src.state import EstadoGrafo, ResultadoEvaluacion

logger = logging.getLogger(__name__)

SIEMPRE_APROBAR = True  # flag temporal, solo para probar el esqueleto del grafo


def evaluar_guion(state: EstadoGrafo) -> dict:
    logger.info("Nodo Evaluación: intentos_redaccion=%d (stub)", state.intentos_redaccion)
    # TODO(Milestone 2): evaluar el guion real con el LLM contra las reglas de la plataforma
    aprobado = SIEMPRE_APROBAR
    feedback = "OK (stub)" if aprobado else "Falta un gancho más fuerte en los primeros 3s (stub)"
    return {"resultado_evaluacion": ResultadoEvaluacion(aprobado=aprobado, feedback=feedback)}
