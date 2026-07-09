---
name: 001-proyecto-analize-02
---

Actualiza plan.md para que el contrato del endpoint GET /health
sea explícito y no ambiguo.

En la sección que describe el endpoint /health, especifica
el shape exacto de ambas respuestas:

Éxito (HTTP 200):
{"status": "ok", "db": "ok"}

Error de DB (HTTP 503):
{"status": "degraded", "db": "error", "detail": "<mensaje breve>"}

Esto debe quedar documentado en plan.md como contrato
de implementación obligatorio, no como sugerencia.
Idioma: español.