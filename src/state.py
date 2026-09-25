"""
Esquema del estado compartido del grafo de ToraMetrics.

Usamos Pydantic (BaseModel) en lugar de TypedDict porque:
1. Valida los tipos en tiempo de ejecución (si un nodo intenta guardar
    un dato con el tipo equivocado, falla rápido y con un error claro,
    en vez de arrastrar un bug silencioso hasta el final del grafo).
2. Permite documentar cada campo con Field(description=...), lo cual
    sirve como documentación viva del contrato entre nodos.
3. LangGraph soporta Pydantic de forma nativa: basta con pasar la
    clase a StateGraph(EstadoGrafo).

Cada nodo del grafo recibe una instancia de EstadoGrafo y devuelve un
diccionario parcial con los campos que actualiza (no el objeto completo).
LangGraph fusiona ese diccionario sobre el estado existente.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class ResultadoBusqueda(BaseModel):
    """Un resultado individual devuelto por la herramienta de búsqueda (Tavily)."""

    titulo: str
    url: str
    contenido: str
    score: Optional[float] = None
    fecha: Optional[str] = Field(
        default=None,
        description="Fecha de publicación de la fuente, si Tavily la provee "
        "(campo published_date). Puede venir vacía -- no todas las fuentes "
        "la reportan.",
    )


class ResultadoEvaluacion(BaseModel):
    """Veredicto del nodo Evaluación sobre el guion generado."""

    aprobado: bool
    feedback: str = Field(
        description="Motivo del rechazo o comentarios de mejora. "
        "Se reinyecta al nodo de Redacción si aprobado=False."
    )


class EstadoGrafo(BaseModel):
    """Estado que fluye entre todos los nodos del grafo de generación de contenido."""

    # --- Inputs del usuario (equivalentes al nodo conceptual "Inicio") ---
    nicho: str = Field(description="Ej. 'Finanzas personales'")
    plataforma: str = Field(description="Ej. 'TikTok', 'Instagram', 'YouTube Shorts'")
    formato: str = Field(description="Ej. 'Video corto', 'Carrusel'")

    # --- Nodo Investigación ---
    resultados_busqueda: list[ResultadoBusqueda] = Field(default_factory=list)

    # --- Nodo Curación y Estrategia ---
    tema_elegido: Optional[str] = None
    estructura_narrativa: Optional[str] = None

    # --- Nodo Redacción del guion ---
    guion: Optional[str] = None
    intentos_redaccion: int = 0

    # --- Nodo Evaluación ---
    resultado_evaluacion: Optional[ResultadoEvaluacion] = None
