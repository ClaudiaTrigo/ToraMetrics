# Registro de decisiones técnicas — ToraMetrics

Este documento recoge las decisiones de arquitectura e implementación tomadas durante el desarrollo, con su motivo, para no tener que volver a discutirlas y para que quede constancia del razonamiento (útil también como evidencia de proceso para el portafolio). El README se mantiene a nivel de resumen; el detalle vive aquí.

## Stack y proveedores

**Modelo de IA: Google Gemini en vez de la API de Anthropic.**
Google AI Studio ofrece un free tier real y permanente sin tarjeta de crédito; la API de Anthropic no tiene free tier, solo créditos prepago desde $5. Modelo en uso: `gemini-3.6-flash` (`gemini-2.5-flash` quedó descontinuado para cuentas nuevas — Google rota los nombres de modelo con frecuencia, revisar el identificador vigente si vuelve a fallar con `404 NOT_FOUND`).

**Base de datos: PostgreSQL en vez de SQLite.**
Decisión tomada el 2026-08-20 para persistir los guiones generados (con su fecha) y alimentar el calendario del frontend. Se descartó SQLite pese a ser más simple de arrancar porque el archivo se puede perder con el spin-down del backend en el free tier de Render.

## Nodo de Investigación

**Estrategia de búsqueda en Tavily.**
Query simple, sin mes/año en el texto (para evitar problemas de locale en Windows); `time_range="month"` acota la ventana temporal en su lugar.

**Cambio de query: de "tendencias virales" a "noticias" (2026-09-25).**
La query original, `"tendencias virales en {nicho}"`, nunca calzaba con cómo se escribe periodismo real: una noticia sobre el resultado de una competición no se autodescribe como "tendencia viral", así que Tavily (que puntúa por coincidencia de texto con la query, no por calidad) siempre prefería listicles genéricos de "tendencias 2026" sobre la cobertura real y relevante. Se verificó con un caso concreto: la cobertura de Nadia Erostarbe en la WSL no aparecía con la query vieja, pero sí con `"noticias de surf"` (score 0.7+, resultados de AS.com, World Surf League, Surf News Network). Query actual: `f"noticias de {nicho}"`.

**Selector de modo de búsqueda (idea de producto, pendiente — 2026-09-25).**
A futuro, cuando exista el frontend, la idea es que el usuario elija en un desplegable la "intención" de la búsqueda (tendencias, noticias, curiosidades, opiniones, guías...) y cada opción mapee a una plantilla de query distinta en `tavily_service.py` — un campo nuevo en el estado (`modo_busqueda`). No implementado todavía: `"noticias de {nicho}"` queda como único default mientras tanto.

**Calidad de fuente: `topic`, `exclude_domains` y el score (revisado 2026-09-25).**
Verificación manual con nichos reales (surf, tecnología) mostró que `topic="general"` traía sobre todo posts sueltos de redes sociales (Instagram, TikTok, Facebook) sin contenido real. Se probó `topic="news"` (índice periodístico de Tavily) para priorizar diarios/blogs, pero sus scores de relevancia resultaron estructuralmente más bajos (máximo observado 0.47, vs. hasta 0.90 con `topic="general"`), y por debajo del propio umbral que Tavily recomienda en su documentación (`score > 0.7`).

Se probó filtrar por score (primero 0.25, luego el 0.7 recomendado por Tavily) y en ambos casos el filtro fue contraproducente: descartó cobertura real y reciente (una competición importante de surf, el Mundial Junior de Surf 2026) mientras dejaba pasar spam con score alto — una página con el título "Tendencias Virales en Tecnología 2025" cuyo contenido real hablaba del aeropuerto de Barajas llegó a 0.90. Conclusión: **el score de Tavily mide coincidencia de texto con la query (vía su "IA propietaria", no documentada en detalle), no calidad editorial ni si algo es realmente una tendencia** — no es un filtro de relevancia confiable.

Decisión final: `topic="general"` (sin filtro de score) + `exclude_domains` para bloquear explícitamente las plataformas que en las pruebas devolvían posts sin contenido real: `tiktok.com`, `instagram.com`, `facebook.com`, `youtube.com`, `reddit.com`, `pinterest.com`. YouTube se sumó a la lista el 2026-09-25 (decisión de Claudia). X/Twitter, Threads y LinkedIn se dejan fuera de esa lista a propósito (decisión de Claudia, 2026-09-25: sí quiere que esas plataformas puedan aparecer como fuente). El ruido que igual pasa (spam, contenido tangencial) queda para que el nodo de Curación lo filtre leyendo el contenido con Gemini — un filtro mecánico de texto no puede sustituir ese juicio.

**Búsqueda por país.**
`country="spain"` está activo (`_PAIS_POR_DEFECTO` en `tavily_service.py`) y solo funciona con `topic="general"` (verificado en la documentación oficial). Se había perdido sin querer al probar y descartar `topic="news"`, y quedó sin reactivar al volver a `"general"` -- se detectó porque empezaron a aparecer noticias de Perú sin acotar por país. Corregido el 2026-09-25.

Importante -- verificado en la documentación oficial de Tavily: `country` **no es un filtro excluyente, es un boost de ranking** ("Boost search results from a specific country. This will prioritize content from the selected country"). No garantiza que solo aparezcan fuentes españolas; solo les da prioridad frente a las demás. Decisión de Claudia (2026-09-25): aceptar ese comportamiento (boost, no filtro estricto) en vez de forzar una restricción dura con `include_domains` + una lista cerrada de medios españoles, que sería más estricta pero requeriría mantener esa lista a mano.

El país sigue hardcodeado (no es input del usuario ni campo del `EstadoGrafo`) -- si el producto necesita soportar varios países, este valor pasaría a venir del estado (nuevo campo `pais`) y del formulario del frontend.

**Manejo de fallos.**
Si Tavily falla o devuelve 0 resultados, el nodo se degrada con lista vacía y el grafo continúa; no se considera un error fatal — un fallo de una API externa no debe tumbar todo el flujo. Antes de darse por vencido, se reintenta automáticamente con `tenacity` (3 intentos, backoff exponencial).

**Esquema `ResultadoBusqueda`.**
Se añadió el campo `fecha` (`Optional[str]`), poblado desde `published_date` de Tavily.

## Nodo de Curación y Estrategia

**Cambio de rol respecto al diseño original (2026-08-20).**
En el diseño inicial, este nodo elegía automáticamente 1 tema. Con la definición de producto actual, ya no elige por sí solo: filtra los `resultados_busqueda`, usa Gemini para resumir cada candidato relevante en título + resumen breve, y se queda con los 5 mejores (`candidatos_tema`). El grafo se **pausa** en este punto (patrón *human-in-the-loop*: `interrupt()` de LangGraph + un checkpointer que persiste el estado congelado) hasta que el usuario elige uno de los 5 vía la API. Tras la selección, el estado se actualiza con `tema_elegido` y el grafo continúa. La definición de `estructura_narrativa` (Gancho → Retención → CTA según la plataforma) sigue ocurriendo en este nodo, pero ahora después de conocer el tema ya elegido por el usuario, no antes.

## Gestión de errores y reintentos (regla general)

Ante fallos de APIs externas, el criterio del proyecto es: reintentar automáticamente con backoff antes de rendirse, y si aun así falla, degradar de forma controlada (nunca detener el grafo completo por un fallo externo puntual) — registrando el error con `logger.error(exc_info=True)` para que quede trazado en los logs sin romper la ejecución.
