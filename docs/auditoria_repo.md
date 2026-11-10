# Auditoría del repositorio (Fase A)

**Fecha:** 2026-11-09 · **Rama:** `develop` (commit base `bcfb368`) · **Python:** 3.12.16 (vía `uv`)

## 1. Verificación ejecutada

| Comando | Resultado |
|---|---|
| `uv sync --all-groups` (equivale a `make install`) | OK. Dependencias bloqueadas en `uv.lock` (osmnx 2.1.1, networkx 3.7, scipy 1.18.1, numpy 2.5.4) |
| `uv run pytest -q` (equivale a `make test`) | **3 passed** (`test_smoke.py`, 2 tests de `test_descarga.py`) |
| `uv run ruff check .` (equivale a `make lint`) | **All checks passed** |
| `make` | **No instalado** en este equipo Windows. Los comandos se ejecutan directamente con `uv` |

Nota: `make validar-catalogo`, que aparece en la spec F1, **no existe** en el `Makefile`.

## 2. Estado por fase

| Fase | Estado | Evidencia |
|---|---|---|
| Scaffold (pyproject, CI, Makefile, config) | **Hecho** | `pyproject.toml`, `Makefile`, `.github/workflows/ci.yml`, `src/rutas/config.py` (SEED=42, TIME_LIMIT_S=300, REPETITIONS=5, UTM 32618) |
| F1 Datos crudos | **Parcial** | Existe `descarga.py` con tests y 5 `*.meta.json`. Faltan los GraphML, `catalogo_semilla.csv`, `catalogo.csv`, `pares_dijkstra.csv`, y los módulos `catalogo.py`, `catalogo_borrador.py`, `pares.py` |
| F2 R1 Modelo de red | **Pendiente** | `algorithms/`, `graph/`: solo `__init__.py` vacíos. `specs/r1_modelo_red.md` vacía (0 bytes) |
| F3 Medición | **Pendiente** | `bench/`: solo `__init__.py` |
| F4 R2 Dijkstra | **Pendiente** | `specs/r2_caminos_minimos.md` vacía. Sin código |
| F5 R3 Envolvente | **Pendiente** | `specs/r3_envolvente.md` vacía. Sin código |
| F6 R4 Recorrido | **Pendiente** | `specs/r4_recorrido.md` vacía. Sin código |
| F7 R5 App | **Pendiente** | No existe `app/`, aunque el `Makefile` tiene `make app` |
| F8 Documento | **Pendiente** | `report/`: solo `__init__.py`. No existe `docs/decisiones.md` ni `docs/preguntas_sustentacion.md` |

## 3. Discrepancias con ROADMAP_AGENTE.md

1. **Rutas referenciadas que no existen:** `docs/enunciado/` (los PDF del enunciado), `catalogo_semilla.csv`, `catalogo.csv`, `pares_dijkstra.csv`, `app/streamlit_app.py`, `docs/decisiones.md`.
2. **Specs vacías:** `r1` a `r4` tienen 0 bytes. Solo `f1_datos_crudos.md` tiene contenido (83 líneas, bien estructurada).
3. **`docs/ai_usage.md`** solo tiene el título. La regla 8 exige una entrada por PR; esta auditoría añade la primera.
4. **Timeouts de descarga:** `descarga.py` fija `ox.settings.requests_timeout = 180` para todas las redes. El roadmap pide un timeout por red (2 km: 90 s … departamento: 1800 s).
5. **Descarga del departamento:** el `quindio.meta.json` registra un tiempo de 513 s y el servidor `maps.mail.ru`, pero **el GraphML correspondiente no está en `data/raw/`**. Sin el archivo no se puede verificar el `sha256` registrado.
6. **Centro de los radios sin verificar:** `PLAZA_BOLIVAR = (4.5325757, -75.6730045)` tiene el comentario `VERIFICAR en el mapa`. Ningún documento registra esa verificación. Es el PARADA 1 del roadmap.
7. **`dist_type` implícito:** la spec F1 dice que `graph_from_point` usa `bbox`. Confirmado en OSMnx 2.1.1 instalado (default `bbox`), pero `descarga.py` no lo fija explícitamente. Conviene pasarlo para que sea evidente.
8. **`src/rutas/data/` sin `__init__.py`:** funciona como namespace package y los tests pasan, pero es inconsistente con el resto de paquetes.
9. **`make` ausente en Windows:** el flujo del roadmap depende de `make`. Opciones: instalarlo (p. ej. `scoop install make`) o usar los comandos de `uv` directamente.

### Estado tras las correcciones (rama `fix/auditoria-discrepancias`)

- Punto 4 (timeouts): **resuelto**. Timeout por red en `descarga.py` (D2 en `docs/decisiones.md`).
- Punto 7 (`dist_type`): **resuelto**. Explícito en `descarga.py` (D3).
- Punto 8 (`data/__init__.py`): **resuelto**.
- Punto 9 (`make` en Windows): **resuelto** con comandos `uv` en el README (D7).
- Punto 6 (plaza de Bolívar): comprobada contra OSM (≈4 m, D6). Falta la verificación humana (PARADA 1).
- Riesgo de `fork`: **resuelto** por decisión del grupo: medición en Windows con `spawn` (D1).
- Pendientes del grupo: criterio de "cercanos" (D4) y algoritmo de envolvente (D5).

## 4. Riesgos

- **Medición en Windows (bloqueante para Fase 3):** el roadmap prescribe `multiprocessing` con `fork`, que no existe en Windows. Si la máquina oficial no es Linux/macOS, `measure()` no funciona tal como está especificado. Hay que decidir antes de implementar: máquina Linux/macOS para las mediciones oficiales, o un fallback con `spawn` documentado.
- **Datos grandes y versionado:** `.gitignore` excluye `data/raw/*.graphml` pero **no** `data/processed/`. Un `graph_csr.npz` podría entrar al repo por accidente. Conviene ignorarlo y publicarlo como Release (`data-v1`, como indica la spec F1).
- **`results/` y `figures/` no están ignorados:** es correcto para los resultados oficiales, pero hay que vigilar que no se suban salidas de pruebas.
- **`.atl/`** (carpeta de configuración de agente, sin seguimiento): decidir si se agrega al `.gitignore` o se deja fuera del repo.
- **Código de algoritmos:** aún no existe, así que no hay violaciones de pureza (lectura de archivos, OSMnx o impresión dentro de `algorithms/`). La regla debe revisarse en F2.
- **Sin evidencia de verificación de catálogo:** `make validar-catalogo` y el validador no existen. Ningún lugar tiene `verificado=True`.

## 5. Correcciones propuestas

Triviales (en este PR, `chore/auditoria`):
- Añadir la entrada de uso de IA en `docs/ai_usage.md` (hecho en este commit).
- Ignorar `data/processed/*.npz` y `.atl/` en `.gitignore`. (Pendiente de decisión sobre `.atl/`.)

Para discutir (no se tocan en esta fase):
- Timeouts por red en `descarga.py` (punto 4).
- Pasar `dist_type="bbox"` explícito en `descarga.py` (punto 7).
- Decisión de máquina oficial y de `fork` vs `spawn` (riesgo de Windows).
- Localizar o redescargar `quindio.graphml` para validar su `sha256`.
- Instalar `make` o documentar los comandos equivalentes del `Makefile` en el README.

## 6. Resumen para PARADA A

- Verde: instalación, tests (3/3) y lint.
- Hecho: scaffold, descarga de radios y departamento (metadatos), spec F1.
- Pendiente de F1: GraphML, catálogo, pares y sus módulos.
- Pendiente de F2 en adelante: código y specs vacías.
- Decisiones del grupo que bloquean: máquina oficial de medición (Windows/`fork`) y verificación de la plaza de Bolívar.
