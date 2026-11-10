# Estado del proyecto por fase

Actualizado: 2026-11-10. Fase actual: **Fase 4 (R2, caminos mínimos)**.

| Fase | Estado | Evidencia |
|---|---|---|
| A. Auditoría | Hecha | `docs/auditoria_repo.md`, PR #2 |
| 1. Datos crudos | **Cerrada** (tag `fase-1-datos`) | Release `data-v1`, catálogo de 40 verificados, PR #2 y #3 |
| 2. R1 modelo de red | Código y spec hechos; PARADA 2 aprobada | `specs/r1_modelo_red.md`, PR #2 |
| 3. Medición | En revisión | Spec `specs/f3_medicion.md` pendiente de revisión (PR #5) |
| 3b. Tiempos R1.3 | Hechos | `results/r1_tiempos_componente.csv`, PR #4 |
| 4. R2 Dijkstra | **En curso** | Rama `feat/f4-dijkstra` |
| 5. R3 envolvente | Pendiente | PARADA 5 |
| 6. R4 viajante | Pendiente | PARADA 6 |
| 7. R5 aplicación | Pendiente | Carpeta `app/` no creada |
| 8. Documento técnico | Pendiente | Redacción con el grupo |

## PR abiertos
- #2 código de R1 y correcciones (base `develop`).
- #3 deuda técnica y README (base `develop`).
- #4 tiempos de R1.3 (apoyado en #2).
- #5 infraestructura de medición de la Fase 3 (apoyado en #4 y #2). Revisor pendiente: @JhonyAlexanderPerea.

## Decisiones del grupo pendientes
- Revisor de las specs F1, R1 y F3.
- Vecinos de Génova: la regla OSM se mantiene (D11); falta cita oficial opcional.
