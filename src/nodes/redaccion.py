"""
Nodo: Redacción del guion.

Responsabilidad futura: convertir `estructura_narrativa` en el guion
literal adaptado al `formato`. Si `resultado_evaluacion.feedback` existe
de un intento anterior, debe usarlo para corregir el guion. Debe
incrementar `intentos_redaccion` en cada paso.

Por ahora es un stub sin lógica real, pero sí incrementa el contador de
intentos para que el ciclo de reintento (Redacción <-> Evaluación) sea
comprobable en el grafo mínimo.
"""

from __future__ import annotations

import logging

from src.state import EstadoGrafo

logger = logging.getLogger(__name__)


def redactar_guion(state: EstadoGrafo) -> dict:
    intento = state.intentos_redaccion + 1
    logger.info("Nodo Redacción: intento=%d (stub, guion placeholder)", intento)
    # TODO(Milestone 2): generar el guion real con el LLM, usando feedback si existe
    return {
        "guion": f"[guion placeholder - intento {intento}]",
        "intentos_redaccion": intento,
    }
