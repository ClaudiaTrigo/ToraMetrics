# Estado del proyecto — bitácora

> Este archivo es la fuente de verdad del progreso y las decisiones tomadas.
> Se actualiza en cada sesión relevante. `CLAUDE.md` explica cómo se usa esto
> junto al resto de la documentación.

Última actualización: 2026-09-25

## Flujo de producto (definido 2026-08-20)

- **Pantalla Calendario**: vista mensual con los videos por fecha (solo
  título). Clic en un día/título abre el guion completo.
- **Pantalla "Generar guion"**: formulario (nicho, plataforma, formato) → el
  agente investiga y presenta 5 candidatos (título + resumen breve) → el
  usuario elige uno manualmente → el agente continúa hasta el guion final
  (con ciclo de evaluación/reintento) y lo guarda para el calendario.

Esta definición cambió el rol del nodo de Curación (ver más abajo).

## Arquitectura del grafo — detalle por nodo

- **Inicio**: recibe nicho, plataforma, formato.
- **Investigación**: usa Tavily, guarda en `resultados_busqueda`. No elige ni
  resume nada — eso es trabajo de Curación.
- **Curación y Estrategia** (rol actualizado 2026-08-20): filtra
  `resultados_busqueda`, usa Gemini para resumir cada candidato relevante en
  título + resumen breve, se queda con los 5 mejores (`candidatos_tema`, en
  el estado). El grafo se **pausa** aquí (patrón human-in-the-loop:
  `interrupt()` de LangGraph + checkpointer) hasta que el usuario elige uno
  vía la API → `tema_elegido`. La `estructura_narrativa` se define después de
  conocer el tema elegido, no antes.
- **Redacción del guion**: convierte la estructura narrativa en guion
  literal; usa `feedback_evaluador` si existe; incrementa
  `intentos_redaccion`. Sin cambios respecto al diseño original.
- **Evaluación**: juzga si el guion cumple las reglas de la plataforma
  (duración, gancho, claridad del CTA, coherencia); devuelve
  `resultado_evaluacion` (`aprobado: bool`, `feedback`).

Aristas: Inicio → Investigación → Curación → [PAUSA] → Redacción → Evaluación
→ (Fin si `aprobado` o `intentos_redaccion >= 3`; si no, vuelve a Redacción).

## Esquema del estado (resumen — `src/state.py` es la fuente de verdad)

`nicho`, `plataforma`, `formato`, `resultados_busqueda` (list de
`ResultadoBusqueda`: título, url, contenido, score, fecha),
`candidatos_tema` (pendiente de implementar), `tema_elegido`,
`estructura_narrativa`, `guion`, `resultado_evaluacion`,
`intentos_redaccion`.

Nota: `pais` NO es (todavía) un campo del estado — ver decisiones del nodo de
Investigación más abajo.

## Arquitectura de despliegue (3 capas)

```
Usuario (navegador)
  → Frontend Next.js (calendario, formulario, selección de 5 candidatos)
    → Backend FastAPI (lanzar investigación+curación → 5 candidatos;
       recibir selección → reanudar grafo hasta el guion; listar guiones
       por fecha; CORS configurado)
      → Agente LangGraph (pipeline con pausa human-in-the-loop)
        → PostgreSQL (persiste cada guion: nicho, plataforma, formato,
           fecha, título, guion, estado de evaluación)
```

## Gestión de proyecto en GitHub

Ver el skill `github-pm` para el formato exacto de issues, labels y
milestones — no lo dupliques aquí.

## Progreso por milestone

### Milestone 1 — Fundamentos (6/6) ✅ CERRADO

- [x] Diseñar arquitectura del grafo
- [x] Crear y activar entorno virtual
- [x] Instalar librerías base (langgraph, langchain, langchain-google-genai,
      python-dotenv, tavily-python)
- [x] Crear cuentas y API keys (Google Gemini + Tavily)
- [x] Configurar `.env` (`.gitignore` con `.env` y `venv/` creado primero)
- [x] Script de prueba de conexión (`test_conexion.py`, ✅ Gemini y Tavily)

Nota: no hay issue de "verificar Python" — ya estaba instalado con la
versión correcta; fue una decisión de alcance deliberada, no un olvido.

### Milestone 2 — Construcción del grafo — EN CURSO

Esqueleto iniciado: `src/`, `tests/`, `.gitignore`, `requirements.txt`,
`test_conexion.py` commiteados. `src/graph.py` montado con los 4 nodos como
stubs (solo Investigación tiene lógica real).

**Nodo de Investigación — código base ✅ CERRADO** (duda de calidad de
resultados ✅ RESUELTA, ver sección "RESUELTO" más abajo):

- [x] Estrategia de búsqueda: query simple "tendencias virales en {nicho}",
      sin mes/año en texto (evita problemas de locale en Windows);
      `time_range="month"` acota la ventana en su lugar
- [x] `src/services/tavily_service.py` con `buscar_tendencias(nicho) ->
      list[ResultadoBusqueda]`: reintentos con `tenacity` (3 intentos,
      backoff exponencial); `search_depth="advanced"`, `topic="general"`,
      `exclude_domains` (ver sección "RESUELTO" para la config vigente)
- [x] Esquema `ResultadoBusqueda` en Pydantic (con campo `fecha: Optional[str]`
      desde `published_date` de Tavily)
- [x] `investigacion_node(state)` en `src/nodes/investigacion.py`: mide
      tiempo con `time.perf_counter()`; si Tavily falla tras los reintentos,
      captura con `logger.error(exc_info=True)` y devuelve
      `resultados_busqueda=[]` (el grafo no se detiene); loguea con
      `logger.info` nicho/nº resultados/tiempo si va bien
- [x] `tenacity` añadido a `requirements.txt`
- [x] `test_investigacion_manual.py` (raíz, mismo espíritu que
      `test_conexion.py`; corre `investigar()` con nichos de prueba reales
      -- actualmente "Actualidad en el surf" y "Tecnología") — ejecutado
      varias veces durante la verificación manual de 2026-09-25
- [x] `README.md` con documentación técnica completa
- [x] Logging básico (nicho, nº de resultados, tiempo de respuesta)

## Decisiones tomadas — nodo de Investigación (2026-08-20)

- Fallo de Tavily o 0 resultados → el nodo se degrada con lista vacía, el
  grafo sigue.
- Reintentos automáticos con `tenacity` antes de darse por vencido.
- Se añade el campo `fecha` a `ResultadoBusqueda`.
- `nicho` es y siempre fue texto completamente libre (no una lista fija),
  combina sin problema con el filtro de país.
- `topic` en Tavily: `"news"` prioriza fuentes periodísticas (más estricto);
  `"general"` busca en toda la web indexada (más amplio, no garantiza
  actualidad periodística).
- Búsqueda por país: el parámetro `country` de Tavily **solo funciona si
  `topic="general"`** — no es compatible con `topic="news"` (verificado en
  la documentación oficial de Tavily). *(Ver la sección "RESUELTO" más
  abajo para la configuración vigente: `country="spain"` está activo de
  nuevo, y se descubrió que es un boost de ranking, no un filtro
  excluyente.)*

## RESUELTO (2026-09-25) — calidad de resultados del nodo de Investigación

La duda abierta sobre `topic="general"` vs `"news"` se resolvió con pruebas
manuales reales (`test_investigacion_manual.py`, nichos "Actualidad en el
surf" y "Tecnología"). Recorrido completo en `docs/DECISIONS.md`; resumen:

- Se probó `topic="news"` para evitar redes sociales, pero sus scores de
  relevancia quedaron muy por debajo del umbral que la propia Tavily
  recomienda (`score > 0.7`) — máximo observado 0.47.
- Se probó filtrar por score (0.25 y luego 0.7) y en ambos casos el filtro
  descartó cobertura real (una competición importante de surf, el Mundial
  Junior de Surf 2026) mientras dejaba pasar spam con score alto. El score
  de Tavily resultó ser una señal de coincidencia de texto, no de calidad
  editorial — decisión final: **no filtrar por score**.
- Configuración final: `topic="general"` + `exclude_domains` (bloquea
  tiktok.com, instagram.com, facebook.com, youtube.com, reddit.com,
  pinterest.com; deja pasar X/Twitter, Threads y LinkedIn a propósito) +
  `country="spain"`.
  Este último se había perdido sin querer al probar `topic="news"` y no se
  reactivó al volver a "general" -- se detectó porque aparecían noticias de
  Perú sin acotar. Al reactivarlo se confirmó (documentación oficial de
  Tavily) que `country` es un **boost de ranking, no un filtro
  excluyente** -- prioriza España pero no garantiza excluir otros países.
  Decisión de Claudia: aceptar ese comportamiento en vez de forzar una
  restricción dura con `include_domains` + lista cerrada de medios
  españoles.
- Con esta configuración, "Actualidad en el surf" sí trae cobertura real y
  reciente del Mundial Junior de Surf 2026. Sigue entrando algo de ruido
  (spam de SEO, contenido tangencial) — se decidió dejar ese filtrado más
  fino para el nodo de Curación (lee contenido con Gemini), no seguir
  ajustando parámetros mecánicos de Tavily.
- **Cambio de query (2026-09-25):** incluso con todo lo anterior resuelto,
  seguía sin aparecer cobertura de un hecho real y reciente que Claudia
  sabía que existía (Nadia Erostarbe compitiendo en la WSL). Diagnóstico:
  la query fija `"tendencias virales en {nicho}"` nunca calza con cómo se
  escribe periodismo real -- una noticia de resultado deportivo no se
  autodescribe como "tendencia viral", así que Tavily premiaba listicles
  genéricos por sobre la noticia real. Verificado probando la misma query
  con texto distinto: `"noticias de surf"` sí la encontró (score 0.7+).
  Query actual: `f"noticias de {nicho}"`. No era un problema de la API --
  se descartó cambiar de proveedor de búsqueda.
- **Idea de producto pendiente:** un desplegable en el frontend (cuando
  exista) para que el usuario elija la "intención" de búsqueda -- tendencias,
  noticias, curiosidades, opiniones, guías... -- cada una con su propia
  plantilla de query (nuevo campo `modo_busqueda` en el estado). No
  implementado todavía; queda para cuando se diseñe el frontend.
- `prueba_tavily_comparativa.py` cumplió su función exploratoria (comparar
  parámetros antes de decidir) y se borró del repo el 2026-09-25 — su
  razonamiento ya queda capturado en prosa en este documento y en
  `DECISIONS.md`, y el archivo en sí ya no reflejaba la configuración
  vigente (usaba `topic`/`country`/query viejos).

**Siguiente paso acordado**: rediseñar el nodo de Curación con el flujo de 5
candidatos + selección humana, y después el mecanismo de pausa
human-in-the-loop en el grafo.

### Milestones 3 y 4 — sin iniciar

Alcance de Milestone 3 ya ampliado: modelo de datos en PostgreSQL, endpoints
para el flujo de selección de 5 candidatos, pantallas de Calendario y
"Generar guion" en el frontend. El desglose de issues previo a esta
ampliación está en `issues-toralytics.md` (de una conversación anterior) —
revisar y actualizar al llegar a este milestone.
