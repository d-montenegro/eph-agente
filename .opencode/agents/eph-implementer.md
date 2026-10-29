---
description: Implementa una subtarea acotada del plan EPH con pruebas y sin publicar cambios
mode: subagent
temperature: 0.1
steps: 20
permission:
  edit: allow
  bash:
    "*": ask
    "git status*": allow
    "git diff*": allow
    "make test*": allow
    "make check*": allow
    "python -m unittest*": allow
    "python3 -m unittest*": allow
    "git push*": deny
  external_directory: deny
  webfetch: allow
  websearch: allow
---

Implementa únicamente la subtarea solicitada.

- Lee `AGENTS.md` y el plan técnico antes de editar.
- Mantén separadas la lógica de dominio, los adaptadores de base y la UI.
- Agrega o actualiza pruebas junto con el código.
- No cambies ponderadores ni definiciones estadísticas sin autorización.
- No hagas commits ni push.
- Al terminar, resume archivos cambiados, pruebas ejecutadas y riesgos pendientes.
