---
name: nuevo-nodo-langgraph
description: Checklist para crear o modificar un nodo del grafo LangGraph de ToraMetrics (Investigación, Curación, Redacción, Evaluación), siguiendo el mismo patrón ya usado en el nodo de Investigación — capa de servicio, esquema Pydantic, función de nodo con logging y manejo de errores, script de prueba manual, y sincronización de docs. Usar SIEMPRE que Claudia pida crear, diseñar, implementar o modificar un nodo del grafo, mencione "el siguiente nodo", o hable de Curación, Redacción o Evaluación como tarea de código — no solo cuando lo pida explícitamente con esas palabras.
---

# Nuevo nodo del grafo LangGraph

Antes de escribir código, confirma el comportamiento esperado del nodo si no
está ya cerrado en `docs/estado-proyecto.md`. No asumas — pregunta (ver
`CLAUDE.md`: "Cómo trabajar conmigo").

Sigue este orden, en fases, esperando confirmación entre pasos importantes
(no entregues todo el código de golpe):

## 1. Estado (si el nodo necesita nuevos campos)

Actualiza `src/state.py` (Pydantic) con los campos nuevos. Explica qué
representa cada campo nuevo antes de tocar el resto del código.

## 2. Capa de servicio (si el nodo llama a algo externo: API, IA, etc.)

Crea o edita `src/services/<nombre>_service.py`:

- Reintentos automáticos con `tenacity` (patrón ya usado:
  3 intentos, backoff exponencial) antes de darse por vencido.
- Si la llamada externa falla incluso tras los reintentos, el servicio debe
  poder fallar de forma controlada — el nodo decide cómo degradarse (ver
  paso 3), pero el grafo **nunca** debe detenerse por un fallo externo.
- Si vas a fijar parámetros de una API externa (ej. Tavily, Gemini), no
  asumas su comportamiento por conocimiento previo: verifica contra la
  documentación oficial vigente y documenta la decisión en
  `docs/estado-proyecto.md`.

## 3. Función del nodo

Escribe `<nombre>_node(state)` en `src/nodes/<nombre>.py`:

- Mide el tiempo con `time.perf_counter()`.
- Si algo fallable falla, captura la excepción con
  `logger.error(exc_info=True)` y degrada el estado con un valor por defecto
  razonable (ej. lista vacía) en vez de propagar el error.
- Si todo va bien, loguea con `logger.info` al menos: el input relevante, un
  indicador del resultado (nº de resultados, éxito/fallo) y el tiempo.

## 4. Script de prueba manual

Crea `test_<nombre>_manual.py` en la raíz del repo, mismo espíritu que
`test_conexion.py` / `test_investigacion_manual.py`: corre el nodo o el
servicio con 2-3 casos de prueba representativos y muestra los resultados en
consola. Esto verifica el nodo de forma aislada antes de integrarlo al grafo
completo.

## 5. Dependencias

Si añadiste una librería nueva, actualiza `requirements.txt`.

## 6. Sincronizar documentación

- Actualiza `docs/estado-proyecto.md`: marca el progreso y añade cualquier
  decisión de diseño nueva (con la fecha).
- Si la decisión afecta a la documentación "de cara afuera" (arquitectura,
  cómo correr el proyecto, diagrama del grafo), actualiza también
  `README.md` en el mismo cambio.

## 7. Issue de GitHub

Propón el/los issue(s) correspondientes usando el skill `github-pm`, con
criterios de aceptación que reflejen los pasos anteriores.
