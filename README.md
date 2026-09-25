# ToraMetrics

**Estado:** en desarrollo activo — Milestone 2 de 4

MVP de una plataforma SaaS de generación de contenido para redes sociales (estilo Syllaby.io / Sandcastles.ai), construida con un agente de IA orquestado con **LangGraph**. A partir de un nicho, una plataforma (TikTok, Instagram, etc.) y un formato de contenido, el agente investiga tendencias actuales, propone temas, redacta un guion y se autoevalúa antes de entregarlo.

Este proyecto se está construyendo como **pieza de portafolio** para postular a puestos de AI Project Manager, por lo que — además del código — importa demostrar una arquitectura limpia y modular, buenas prácticas de desarrollo (evaluaciones automáticas, manejo de estado, logging, control de costes/tokens) y un proceso de gestión de proyecto real y trazable en GitHub.

## Índice

- [Objetivos del proyecto](#objetivos-del-proyecto)
- [Base del proyecto: arquitectura y stack](#base-del-proyecto-arquitectura-y-stack)
- [Instalación](#instalación)
- [Uso](#uso)
- [Lo que tenemos hecho](#lo-que-tenemos-hecho)
- [Lo que aún está por hacer](#lo-que-aún-está-por-hacer)
- [Cómo se gestiona el proyecto (pestaña Projects de GitHub)](#cómo-se-gestiona-el-proyecto-pestaña-projects-de-github)
- [Convenciones de trabajo](#convenciones-de-trabajo)
- [Licencia](#licencia)
- [Contacto](#contacto)

## Objetivos del proyecto

- Construir un agente funcional con LangGraph que resuelva un flujo completo de producción de contenido: investigación → curación → redacción → evaluación, con reintentos automáticos cuando el guion no cumple las reglas de la plataforma.
- Incorporar un punto de decisión humana (*human-in-the-loop*) real dentro del grafo: el usuario elige entre varios temas candidatos antes de que el agente escriba el guion.
- Exponer el agente como una API (FastAPI) consumida por un frontend (Next.js) con dos pantallas: un calendario de contenido y un formulario de generación de guiones.
- Persistir los guiones generados en una base de datos relacional (PostgreSQL) para alimentar ese calendario.
- Demostrar buenas prácticas de ingeniería: estado tipado con Pydantic, logging estructurado, manejo de errores y reintentos ante fallos de APIs externas, y control de costes/tokens.
- Llevar la gestión del proyecto en GitHub de forma profesional: issues con criterios de aceptación, milestones, labels y un tablero Kanban.

## Base del proyecto: arquitectura y stack

### Flujo de producto

1. **Pantalla "Generar guion"**: el usuario define nicho, plataforma y formato de contenido.
2. El agente busca en internet temas de actualidad/tendencia sobre ese nicho y presenta **5 candidatos** (título + resumen breve).
3. El usuario elige manualmente uno de los 5 candidatos.
4. El agente continúa: define la estructura narrativa según la plataforma (Gancho → Retención → CTA), escribe el guion completo y lo evalúa; si no cumple las reglas de la plataforma, reintenta la redacción con el feedback del evaluador (hasta 3 intentos).
5. El guion final se guarda en la base de datos y aparece en la **pantalla Calendario**, organizado por fecha.

> **Demo:** próximamente — se añadirá un enlace cuando el frontend esté desplegado en Vercel.

### Arquitectura del grafo (LangGraph)

> Esta sección describe el **diseño objetivo** de los 4 nodos. El estado real de cada uno — qué está implementado y qué es todavía un *stub* — está en [Lo que tenemos hecho](#lo-que-tenemos-hecho).

**Nodos:**

- `Inicio` — recibe los inputs del usuario: nicho, plataforma, formato.
- `Investigación` — usa la API de Tavily para buscar noticias/tendencias del nicho; guarda los resultados crudos, sin elegir ni resumir nada.
- `Curación y Estrategia` — filtra los resultados, usa Gemini para resumir los candidatos relevantes en título + resumen, y selecciona los 5 mejores. Aquí el grafo **se pausa** (patrón *human-in-the-loop* con `interrupt()` de LangGraph + checkpointer) hasta que el usuario elige un tema desde la API. Tras la selección, define la estructura narrativa (Gancho → Retención → CTA) según la plataforma.
- `Redacción del guion` — convierte la estructura narrativa en el guion literal adaptado al formato; si existe feedback de un intento anterior, lo usa para corregir.
- `Evaluación` — juzga si el guion cumple las reglas de la plataforma (duración estimada, fuerza del gancho, claridad del CTA, coherencia) y devuelve un veredicto (`aprobado`) más feedback.

**Aristas:**

- Secuenciales: `Inicio → Investigación → Curación → [pausa human-in-the-loop] → Redacción → Evaluación`
- Condicional desde `Evaluación`: si `aprobado = True` o se alcanzan 3 intentos de redacción → Fin; si no → vuelve a `Redacción` con el feedback del evaluador.

**Estado del grafo** (Pydantic, fuente de verdad en `src/state.py`):

`nicho`, `plataforma`, `formato`, `resultados_busqueda` (lista de `ResultadoBusqueda`: título, url, contenido, score, fecha), `tema_elegido`, `estructura_narrativa`, `guion`, `resultado_evaluacion`, `intentos_redaccion`.

> `candidatos_tema` (los 5 candidatos para elegir) está diseñado pero **todavía no implementado** en `src/state.py` — se añadirá junto con el rediseño del nodo de Curación (ver [Lo que aún está por hacer](#lo-que-aún-está-por-hacer)).

### Arquitectura de despliegue

```
Usuario (navegador)
  → Frontend Next.js (calendario, formulario, selección de candidatos)
    → Backend FastAPI (endpoints REST, CORS)
      → Agente LangGraph (pipeline de nodos + pausa human-in-the-loop)
        → PostgreSQL (persiste cada guion: nicho, plataforma, formato, fecha, título, guion, evaluación)
```

### Stack tecnológico

| Capa | Tecnología | Motivo |
|---|---|---|
| Orquestación del agente | Python 3.12, LangGraph, LangChain | Framework estándar de la industria para grafos de agentes con estado |
| Modelo de IA | Google Gemini (`langchain-google-genai`) | Free tier real y permanente sin tarjeta de crédito |
| Búsqueda web | Tavily API | Free tier de 1.000 búsquedas/mes, sin tarjeta |
| Base de datos | PostgreSQL (Supabase o Render free tier) | Se descartó SQLite: el archivo se perdería con el spin-down del backend en el free tier de Render |
| API | FastAPI + uvicorn | Expone el grafo como endpoints REST |
| Frontend | Next.js + Tailwind CSS | — |
| Despliegue | Render (backend) + Vercel (frontend) | Ambos con free tier |
| Secretos | `python-dotenv` + `.env` (no commiteado) | — |
| Reintentos ante fallos externos | `tenacity` | Backoff exponencial en llamadas a Tavily |

Las decisiones técnicas más detalladas (por qué se tomó cada camino, alternativas descartadas) están en [`docs/DECISIONS.md`](docs/DECISIONS.md).

## Instalación

Requisitos previos: Python 3.12, una cuenta de [Google AI Studio](https://aistudio.google.com/) (para la API key de Gemini) y una cuenta de [Tavily](https://tavily.com/) (para la API key de búsqueda). Ambas tienen free tier sin tarjeta.

```powershell
# 1. Clonar el repositorio
git clone https://github.com/ClaudiaTrigo/ToraMetrics.git
cd ToraMetrics

# 2. Crear y activar el entorno virtual (Windows / PowerShell)
python -m venv venv
venv\Scripts\Activate.ps1

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
# Crea un archivo .env en la raíz del proyecto con:
#   GOOGLE_API_KEY=tu_clave_de_gemini
#   TAVILY_API_KEY=tu_clave_de_tavily
```

> El `.env` nunca se commitea (está en `.gitignore`); cada quien usa sus propias claves.

## Uso

El proyecto está en construcción y todavía no expone una API ni un frontend funcionales (ver [Lo que aún está por hacer](#lo-que-aún-está-por-hacer)). Por ahora, lo que se puede ejecutar y verificar es:

```powershell
# Verifica que las credenciales de Gemini y Tavily funcionan correctamente
python test_conexion.py

# Prueba manual del nodo de Investigación con 3 nichos de ejemplo
python test_investigacion_manual.py
```

Esta sección se irá ampliando con ejemplos de uso del grafo completo y, más adelante, con cómo levantar la API y el frontend en local.

## Lo que tenemos hecho

**Milestone 1 — Fundamentos: cerrado (6/6).** Arquitectura del grafo diseñada, entorno virtual creado, librerías base instaladas, cuentas y API keys de Google Gemini y Tavily configuradas en `.env` (con `.gitignore` protegiéndolo), y script de prueba de conexión (`test_conexion.py`) confirmando que ambas APIs responden correctamente.

**Milestone 2 — Construcción del grafo: en curso.**

- Esqueleto del proyecto iniciado: carpetas `src/` y `tests/`, `.gitignore`, `requirements.txt` y `test_conexion.py` ya commiteados.
- `src/graph.py` monta el grafo mínimo con los 4 nodos; por ahora solo el nodo de Investigación tiene lógica real, los otros tres siguen siendo *stubs*.
- **Nodo de Investigación**: capa de servicio `src/services/tavily_service.py` con `buscar_tendencias(nicho)`, reintentos automáticos con `tenacity` (3 intentos, backoff exponencial), `topic="general"` con `country="spain"` (boost, no filtro estricto) y `exclude_domains` para descartar redes sociales de bajo contenido (tiktok.com, instagram.com, facebook.com, youtube.com, reddit.com, pinterest.com) y ventana temporal `time_range="month"`; esquema `ResultadoBusqueda` en Pydantic con el campo `fecha`; `investigacion_node(state)` en `src/nodes/investigacion.py` con logging de nicho, número de resultados y tiempo de respuesta, y degradación controlada (lista vacía) si Tavily falla incluso tras los reintentos, sin detener el grafo. Verificado manualmente con `test_investigacion_manual.py` (nichos "Actualidad en el surf" y "Tecnología").

El detalle de por qué se tomó cada decisión está en [`docs/DECISIONS.md`](docs/DECISIONS.md).

## Lo que aún está por hacer

- Rediseñar e implementar el nodo de Curación y Estrategia con el flujo de 5 candidatos + selección humana (incluye el nuevo campo `candidatos_tema` en el estado).
- Implementar el mecanismo de pausa *human-in-the-loop* en el grafo (`interrupt()` + checkpointer que persista el estado congelado).
- Implementar los nodos de Redacción del guion y Evaluación (hoy son *stubs*).
- Diseñar el modelo de datos en PostgreSQL para persistir los guiones generados.
- **Milestone 3 — API y Frontend** (no iniciado): endpoints FastAPI (lanzar investigación+curación devolviendo los 5 candidatos, recibir la selección y reanudar el grafo, listar guiones por fecha), configuración de CORS, pantallas Next.js de Calendario y "Generar guion", conexión frontend-backend, despliegue en Render + Vercel.
- **Milestone 4 — Pulido y portafolio** (no iniciado): logging y control de costes/tokens de forma sistemática, documentación final del proyecto.

## Cómo se gestiona el proyecto (pestaña Projects de GitHub)

Todo el trabajo se planifica y trackea en el repositorio **[ClaudiaTrigo/ToraMetrics](https://github.com/ClaudiaTrigo/ToraMetrics)**, usando la pestaña **Projects** de GitHub como tablero Kanban, en vez de llevar el seguimiento solo en la conversación con el agente. Esto es intencional: parte del valor de portafolio de este proyecto es mostrar un proceso de gestión real y auditable.

**Tablero Kanban:** tres columnas — `Todo`, `In Progress`, `Done` — donde cada tarjeta es un issue de GitHub.

**4 Milestones**, cada uno agrupando los issues de una fase del proyecto:

1. **Fundamentos** — arquitectura, entorno, cuentas/claves API, configuración. *(cerrado)*
2. **Construcción del grafo** — esqueleto del proyecto, los 4 nodos del agente, pausa human-in-the-loop, persistencia. *(en curso)*
3. **API y Frontend** — endpoints, FastAPI, CORS, Next.js (calendario + formulario), conexión, despliegue.
4. **Pulido y portafolio** — logging/costes, documentación.

**Labels:** `architecture`, `setup`, `node:investigacion`, `node:curacion`, `node:redaccion`, `node:evaluacion`, `api`, `frontend`, `deploy`, `observability`, `documentation`.

**Formato de cada issue:** descripción breve + checklist de "Criterios de aceptación", de forma que cada tarea técnica se pueda marcar como completada de forma objetiva y verificable — no solo "hecho" de palabra.

Este mismo README se actualizará a medida que avancen los milestones, para que siempre refleje el estado real del tablero.

## Convenciones de trabajo

- El proyecto avanza por fases: no se implementa código de golpe, se espera confirmación entre pasos.
- Las decisiones de arquitectura o comportamiento se preguntan explícitamente en vez de asumirse.
- Cada tarea técnica nueva se traduce en un issue de GitHub con criterios de aceptación claros.
- Se prioriza software con free tier real cuando el objetivo es de portafolio/demo, salvo que una limitación real del free tier (p. ej. pérdida de datos) lo desaconseje.
- Al integrar APIs externas, se verifica el comportamiento contra la documentación oficial vigente en lugar de asumir por conocimiento previo, ya que estas APIs cambian con frecuencia.
- Entorno de desarrollo: Windows, terminal PowerShell, entorno virtual (venv), editor VS Code.

## Licencia

Este proyecto usa la licencia MIT (ver [`LICENSE`](LICENSE)) — de uso libre para fines de aprendizaje, revisión técnica o como referencia de portafolio.

## Contacto

Proyecto desarrollado por Claudia Trigo
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/claudia-trigo/) [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/ClaudiaTrigo)

