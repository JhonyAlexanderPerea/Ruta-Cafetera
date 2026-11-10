# Documentación del uso de IA dentro del proyecto
## 2026-11-10 — Aplicación demostrativa (Fase 7, R5)

- **Herramienta:** Claude Code (Claude Haiku 5.5), con subagentes de implementación (escritura de la app, de las figuras y de los servicios) y revisión propia del resultado.
- **Para qué:** redactar `specs/r5_aplicacion.md`, escribir `src/rutas/app_servicios.py`, `app/streamlit_app.py`, `src/rutas/report/figuras.py` y sus pruebas, y generar `figures/` desde `results/`.
- **Cómo se verificó:** `uv run pytest -q` (169 pasan), `uv run ruff check .` (sin errores), la app levantada y recorrida en el navegador, y cada figura abierta y revisada visualmente (se corrigió el solapamiento de etiquetas en R1). El caso de prueba 3 compara `ruta_optima` contra `results/r2_dijkstra.csv` con el grafo real.
- **Límites:** no se usó IA para las mediciones de R2 a R4; las decisiones de la spec las aprobó el grupo. Un subagente afirmó que la rama era `develop` y no lo era: se verificó con git.

## 2026-11-09 — Auditoría del repositorio (Fase A)

- **Herramienta:** Claude Code (Claude Haiku 5.5), sin subagentes.
- **Para qué:** revisar el estado del repo frente a ROADMAP_AGENTE.md y generar docs/auditoria_repo.md.
- **Cómo se verificó:** los comandos de `make install`, `make test` y `make lint` se ejecutaron con `uv` directamente (`make` no está instalado). Pytest: 3 passed. Ruff: All checks passed. La firma de `ox.graph_from_point` se consultó en OSMnx 2.1.1 instalado.
