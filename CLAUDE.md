# ToraMetrics

MVP de una plataforma SaaS estilo Syllaby.io / Sandcastles.ai: un agente de IA
orquestado con LangGraph que, a partir de un nicho, plataforma y formato de
contenido, investiga tendencias, presenta 5 candidatos de tema para que el
usuario elija, escribe un guion y se autoevalúa antes de entregarlo.

Objetivo del proyecto: pieza de portafolio para postular a puestos de AI
Project Manager. Debe demostrar arquitectura limpia y modular, buenas
prácticas de desarrollo (evaluaciones, manejo de estado, logging, control de
costes/tokens) y buen proceso de gestión de proyecto (Issues, Milestones,
tablero Kanban en GitHub).

Repo: ClaudiaTrigo/ToraMetrics

## Stack

- Backend del agente: Python 3.12, LangGraph, LangChain
- Modelo de IA: Google Gemini vía `langchain-google-genai` (Google rota los
  nombres de modelo con frecuencia — el identificador vigente y la fecha del
  último cambio están en `docs/estado-proyecto.md`, no lo asumas de memoria)
- Búsqueda web: Tavily API
- Base de datos: PostgreSQL (free tier de Supabase o Render)
- API: FastAPI + uvicorn
- Frontend: Next.js + Tailwind CSS
- Despliegue: Render (backend) + Vercel (frontend)
- Secretos: python-dotenv + `.env` (nunca commiteado)
- Entorno: Windows, terminal PowerShell, venv

## Arquitectura del grafo (resumen)

```
Inicio → Investigación → Curación [PAUSA human-in-the-loop] → Redacción → Evaluación
                                                                    ↑           │
                                                                    └── feedback ┘ (si no aprobado y intentos < 3)
```

El diagrama Mermaid completo, las decisiones de diseño de cada nodo y el
esquema de estado detallado viven en `README.md` y `src/state.py` (fuente de
verdad). No los dupliques aquí: si cambian, este resumen se desactualiza.

## Dónde vive cada documento

- `README.md` — documentación técnica "de cara afuera" del repo (stack,
  diagrama, cómo ejecutar el proyecto). La lee cualquiera que clone el repo.
- `docs/estado-proyecto.md` — bitácora viva de trabajo: progreso por
  milestone, decisiones tomadas y por qué, dudas abiertas. **Léela al empezar
  cada sesión** y actualízala cuando algo cambie.
- Cuando una decisión de diseño relevante cambie, actualiza `README.md` y
  `docs/estado-proyecto.md` en el mismo cambio — no dejes que se desincronicen.

## Cómo trabajar conmigo (Claudia)

- Es mi primer proyecto con agentes de IA/LangGraph — explica los conceptos
  de forma didáctica, con analogías si ayuda, antes de dar código.
- Trabajamos por fases: no des todo el código de golpe, espera mi
  confirmación entre pasos.
- Cuando surja una decisión de arquitectura o comportamiento, pregúntame
  explícitamente en vez de asumir.
- Antes de sugerir librerías o servicios, prioriza opciones con free tier
  real (esto es un portafolio, no producción) — salvo que una limitación real
  del free tier lo desaconseje (ej. pérdida de datos: por eso Postgres y no
  SQLite).
- Al trabajar con APIs externas (parámetros, límites, comportamiento),
  verifica contra la documentación oficial vigente en vez de asumir por
  conocimiento previo — cambian con frecuencia.
- Cada tarea técnica nueva debe poder traducirse en un issue de GitHub con
  criterios de aceptación claros (usa el skill `github-pm` para esto).
- Al crear o modificar un nodo del grafo, usa el skill `nuevo-nodo-langgraph`
  para seguir siempre el mismo patrón.
