"""
Script de prueba manual — Nodo de Investigación, Milestone 2, ToraMetrics.

Ejecuta el nodo investigar() de forma aislada (sin montar el grafo completo,
sin LLM de por medio) para 2-3 nichos distintos y muestra los resultados en
consola. Sirve para verificar "a ojo" que Tavily trae resultados razonables
y que el nodo se comporta como esperamos, antes de integrarlo al resto del
grafo.

Uso (con el venv activado, desde la raíz del proyecto):
    python test_investigacion_manual.py

Nota: cada ejecución consume búsquedas reales de tu cuota de Tavily (free
tier: 1.000/mes), por eso este script no forma parte de la suite de pytest
-- se ejecuta a mano cuando queremos confirmar el comportamiento real.
"""

from __future__ import annotations

import logging

from src.nodes.investigacion import investigar
from src.state import EstadoGrafo

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")

NICHOS_DE_PRUEBA = [
    "Actualidad en el surf",
    "Tecnología",
]


def probar_nicho(nicho: str) -> None:
    print(f"\n{'=' * 60}\nNicho: {nicho}\n{'=' * 60}")
    estado = EstadoGrafo(nicho=nicho, plataforma="TikTok", formato="Video corto")

    resultado = investigar(estado)
    resultados_busqueda = resultado.get("resultados_busqueda", [])

    if not resultados_busqueda:
        print(
            "⚠️  No se encontraron resultados (o Tavily falló -- revisa el "
            "log de arriba para ver si fue un error o simplemente 0 "
            "resultados)."
        )
        return

    for i, r in enumerate(resultados_busqueda, start=1):
        print(f"\n{i}. {r.titulo}")
        print(f"   URL: {r.url}")
        print(f"   Fecha: {r.fecha or 'sin fecha'}")
        print(f"   Score: {r.score}")
        print(f"   Contenido (primeros 150 caracteres): {r.contenido[:150]}...")


if __name__ == "__main__":
    for nicho in NICHOS_DE_PRUEBA:
        probar_nicho(nicho)

    print(
        "\n\n✅ Prueba manual completada. Revisa arriba que cada nicho trajo "
        "resultados razonables (títulos relevantes, fechas recientes cuando "
        "estén disponibles, sin errores en el log)."
    )
