---
name: github-pm
description: Crea Issues, Milestones y Labels de GitHub para el repo ClaudiaTrigo/ToraMetrics siguiendo sus convenciones exactas de formato y el tablero Kanban (Todo/In Progress/Done). Usar SIEMPRE que Claudia pida crear un issue, planificar el tablero, traducir una tarea técnica en trabajo de GitHub, o diga cosas como "convierte esto en un issue" o "qué issues necesitamos para esto".
---

# Gestión de proyecto en GitHub — ToraMetrics

Repo: `ClaudiaTrigo/ToraMetrics`. Tablero Kanban con columnas Todo / In
Progress / Done.

## Formato de cada issue

Descripción breve (1-3 frases, qué se va a construir y por qué) +
checklist de **"Criterios de aceptación"** en Markdown (`- [ ] ...`), con
criterios concretos y verificables (no "que funcione bien", sino algo que se
pueda marcar como hecho sin ambigüedad).

Ejemplo de forma (no de contenido):

```markdown
Implementar `<algo concreto>` para que `<resultado esperado>`.

## Criterios de aceptación
- [ ] ...
- [ ] ...
- [ ] ...
```

## Milestones (4, fijos)

1. **Fundamentos** — arquitectura, entorno, cuentas/claves API, configuración
2. **Construcción del grafo** — esqueleto del proyecto + los 4 nodos del
   agente + pausa human-in-the-loop + persistencia
3. **API y Frontend** — endpoints, FastAPI, CORS, Next.js (calendario +
   formulario de generación), conexión, despliegue
4. **Pulido y portafolio** — logging/costes, documentación

## Labels (fijas)

`architecture`, `setup`, `node:investigacion`, `node:curacion`,
`node:redaccion`, `node:evaluacion`, `api`, `frontend`, `deploy`,
`observability`, `documentation`.

No inventes labels ni milestones nuevos sin preguntar primero — si una tarea
no encaja claramente en ninguno de los existentes, pregúntale a Claudia
antes de crear uno nuevo.

## Al proponer un issue

1. Identifica a qué milestone y qué label(s) pertenece.
2. Si no es evidente, pregunta en vez de asumir.
3. Escribe la descripción breve + criterios de aceptación con el formato de
   arriba.
4. Si la tarea es grande, propón dividirla en varios issues más pequeños en
   vez de uno enorme.
