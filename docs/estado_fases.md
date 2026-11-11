# Estado del proyecto por fase

Actualizado: 2026-11-10. Fase actual: **Fase 7 (R5 aplicación), lista para PARADA 7**.

| Fase | Estado | Evidencia |
|---|---|---|
| A. Auditoría | Hecha | `docs/auditoria_repo.md`, PR #2 (mergeado a `develop`) |
| 1. Datos crudos | **Cerrada** (tag `fase-1-datos`). Spec aprobada en PARADA 1; falta la firma del revisor | `specs/f1_datos_crudos.md`, PR #1 y #3 |
| 2. R1 modelo de red | Hecha. PARADA 2 aprobada (D9, D10). Spec sin actualizar (sigue "borrador") | `specs/r1_modelo_red.md`, PR #2 |
| 3. Medición (F3) | Hecha, revisión pendiente | `specs/f3_medicion.md`, PR #5 |
| 3b. Tiempos R1.3 | Hecho | `results/r1_tiempos_componente.csv`, PR #4 |
| 4. R2 Dijkstra | Hecha, revisión pendiente. No hay PARADA 4 registrada en `docs/decisiones.md` | `specs/r2_caminos_minimos.md`, PR #6 |
| 5. R3 envolvente | Hecha. PARADA 5 aprobada (D12). **Spec vacía** (`specs/r3_envolvente.md` no tiene contenido) | PR #7, `results/r3_envolvente.csv` |
| 6. R4 viajante | Hecha. PARADA 6 aprobada (D13, D14). Spec sin actualizar (sigue "borrador") | `specs/r4_recorrido.md`, PR #8 |
| 7. R5 aplicación | **Lista para PARADA 7**: app, servicios, figuras y tests hechos (169 pasan). Falta que una persona ajena la levante con el README y revise la spec | `specs/r5_aplicacion.md`, PR #9 (abierto) |
| 8. Documento técnico | Pendiente | Redacción con el grupo |

## PR
- #1 a #8: mergeados a `develop`.
- #9 (`feat/f7-app` hacia `main`): abierto, esperando revisión. Incluye los commits de R1 a R4 porque `main` aún no los tiene.

## Pendientes del grupo
- Revisor de las specs F1, R1, F3, R2, R4 y R5.
- Escribir el contenido de `specs/r3_envolvente.md`.
- PARADA 7 de la app (R5).
- Decidir la base de integración: `develop` ya tiene R1 a R4, pero el PR #9 apunta a `main`.
- Vecinos de Génova: la regla OSM se mantiene (D11); falta cita oficial opcional.
