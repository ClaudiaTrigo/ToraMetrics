"""
Test de humo (smoke test) del grafo mínimo.

No prueba lógica de negocio (todavía no existe: los nodos son stubs).
Solo confirma que el grafo compila, se ejecuta de punta a punta sin
lanzar excepciones y devuelve un estado con la forma esperada. Esto es
justamente lo que pide el criterio de aceptación de esta tarea:
"Confirmar que el grafo mínimo se ejecuta sin errores".
"""

from __future__ import annotations

from src.graph import construir_grafo
from src.state import EstadoGrafo


def test_el_grafo_compila():
    grafo = construir_grafo()
    assert grafo is not None


def test_el_grafo_se_ejecuta_sin_errores():
    grafo = construir_grafo()

    entrada = EstadoGrafo(
        nicho="Finanzas personales",
        plataforma="TikTok",
        formato="Video corto",
    )

    resultado = grafo.invoke(entrada)

    # El resultado de .invoke() es un dict (aunque el estado sea un modelo Pydantic)
    assert resultado["nicho"] == "Finanzas personales"
    assert resultado["guion"] is not None
    assert resultado["resultado_evaluacion"] is not None
    assert resultado["intentos_redaccion"] >= 1


def test_el_guion_se_reescribe_hasta_max_intentos_si_no_se_aprueba(monkeypatch):
    """Verifica que la arista condicional realmente vuelve a Redacción
    cuando el guion no es aprobado, y que corta en MAX_INTENTOS_REDACCION
    en vez de hacer loop infinito."""
    import src.nodes.evaluacion as evaluacion_module

    monkeypatch.setattr(evaluacion_module, "SIEMPRE_APROBAR", False)

    grafo = construir_grafo()
    entrada = EstadoGrafo(
        nicho="Finanzas personales",
        plataforma="TikTok",
        formato="Video corto",
    )

    resultado = grafo.invoke(entrada)

    assert resultado["intentos_redaccion"] == 3
    assert resultado["resultado_evaluacion"]["aprobado"] is False
