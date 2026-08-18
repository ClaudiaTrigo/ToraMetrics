"""
Definición del grafo de ToraMetrics.

Nodos: Investigación -> Curación y Estrategia -> Redacción -> Evaluación
Arista condicional: desde Evaluación, si el guion es aprobado (o se
agotan los reintentos) el grafo termina; si no, vuelve a Redacción con
feedback.

Nota de diseño: el nodo conceptual "Inicio" del diseño original no se
implementa como un nodo propio. LangGraph ya provee un pseudo-nodo START
que representa el punto de entrada del grafo -- conectarlo directamente
a "investigacion" es el equivalente idiomático a "Inicio -> Investigación"
y evita un nodo que no haría nada más que pasar el estado inicial.

Este archivo, por ahora, monta el grafo mínimo con los nodos stub de
src/nodes/*.py (sin lógica real) solo para validar que la estructura del
grafo -- nodos, aristas, arista condicional -- compila y se ejecuta sin
errores. La lógica real de cada nodo se implementará en tareas
posteriores del Milestone 2.
"""

from __future__ import annotations

from langgraph.graph import StateGraph, START, END

from src.state import EstadoGrafo
from src.nodes.curacion import curar_y_definir_estrategia
from src.nodes.evaluacion import evaluar_guion
from src.nodes.investigacion import investigar
from src.nodes.redaccion import redactar_guion

MAX_INTENTOS_REDACCION = 3


def decidir_siguiente_paso(state: EstadoGrafo) -> str:
    """Arista condicional que sale del nodo Evaluación.

    Devuelve el nombre del siguiente nodo ("redaccion") o el pseudo-nodo
    final (END) según el resultado de la evaluación y el número de
    intentos ya realizados.
    """
    if state.resultado_evaluacion is not None and state.resultado_evaluacion.aprobado:
        return END
    if state.intentos_redaccion >= MAX_INTENTOS_REDACCION:
        return END
    return "redaccion"


def construir_grafo():
    """Construye y compila el StateGraph de ToraMetrics."""
    builder = StateGraph(EstadoGrafo)

    builder.add_node("investigacion", investigar)
    builder.add_node("curacion", curar_y_definir_estrategia)
    builder.add_node("redaccion", redactar_guion)
    builder.add_node("evaluacion", evaluar_guion)

    builder.add_edge(START, "investigacion")
    builder.add_edge("investigacion", "curacion")
    builder.add_edge("curacion", "redaccion")
    builder.add_edge("redaccion", "evaluacion")

    builder.add_conditional_edges(
        "evaluacion",
        decidir_siguiente_paso,
        {"redaccion": "redaccion", END: END},
    )

    return builder.compile()


# Instancia compilada, lista para invocar: grafo.invoke({...})
grafo = construir_grafo()
