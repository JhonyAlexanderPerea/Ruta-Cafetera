# Deuda técnica y pendientes (cierre de Fase 1, avance de Fases 2 y 3)

Fecha: 2026-11-10. Estado al cierre de la Fase 1 (tag `fase-1-datos`).

## Cerrado en la Fase 1
- Descarga de las 5 redes (GraphML + metadatos con V, E y SHA-256 verificados).
- Catálogo de 40 lugares, todos verificados por el grupo en el mapa (PARADA 1).
- Pares de Dijkstra generados con la regla de municipios vecinos (D4).
- Spec F1 y README actualizados.

## Pendientes que requieren al grupo
1. **Revisor de la spec F1 y de la spec R1:** el campo "Revisor" debe llenarlo una persona distinta del autor.
2. **Tabla de municipios vecinos (D4):** se calculó con los polígonos de OSM. Génova aparece con un solo vecino (Pijao). Hay que confirmarlo en el mapa.
3. **Fincas y atractivos con tarifa "premium" o "económica":** es una estimación por el tipo de lugar, no un dato verificado.
4. **Duraciones de visita sin fuente (13 atractivos):** son criterio del grupo (propuesta por tipo de lugar), no medidas.
5. **Rancho San Antonio:** el pin de Google queda a unos 40 m de Ecohotel Piedemonte. El grupo lo aprobó tal como está.

## Pendientes técnicos
6. **Cita de complejidad de componentes fuertes (R1.3):** sigue como `[CITA POR VERIFICAR]` en `specs/r1_modelo_red.md`.
7. **Supuesto de rutas nacionales (D10):** 50 km/h sin dato explícito; aprobado como supuesto, no verificado.
8. **Medición de `largest_component` (Fase 3):** no está hecha. El runner está listo (`src/rutas/bench/runner.py`), pero faltan `bench/machine_info.py` y `bench/io.py`.
9. **Timeouts intermedios de descarga (D2):** 180, 360 y 720 s son propuesta nuestra; el grupo debe confirmarlos.
10. **Makefile:** el spec F1 menciona `make validar-catalogo`, que no existe. El validador se corre con `uv run python -m rutas.data.catalogo`. Hay que corregir el spec o agregar el target.
11. **Target `make app`:** apunta a `app/streamlit_app.py`, que aún no existe (Fase 7).
12. **Formato automático:** `ruff format` tocó `src/rutas/data/descarga.py` (commit de estilo separado, sin cambios de lógica).

## Riesgos conocidos
- **Release `data-v1`** apunta a la rama `fix/auditoria-discrepancias`, no a `develop` ni a `main`. Al mergear el PR conviene revisar que el tag y el release sigan bien.
- **Medición en Windows:** `spawn` obliga a que la función y sus argumentos sean serializables. Por eso las funciones medidas deben estar en módulos importables.
- **Overpass:** la descarga depende de servidores públicos que no siempre responden (en esta sesión `overpass-api.de` estuvo inaccesible). Si se vuelve a descargar, puede tardar más de una hora.
