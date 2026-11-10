# Spec: F3 · Infraestructura de medición

**Autor:** Claude (borrador con el grupo) · **Revisor:** <pendiente: nombre distinto del autor> · **Estado:** implementada (revisión pendiente)

## Objetivo
Un único módulo que aplique el protocolo de la sección 6 del enunciado a cualquier algoritmo, y que registre la máquina y el entorno de cada medición.

## Entradas y salidas
- **Entrada:** una función sin argumentos (o con argumentos ya enlazados con `functools.partial`), las repeticiones, el límite de tiempo y el umbral de ejecución larga.
- **Salida:** `Measurement(median_ms, runs_ms, completed, extra)`. Los resultados se escriben a CSV con columnas fijas (`rutas.bench.io`). El entorno se registra en `results/_meta/<nombre>.json` (`rutas.bench.machine_info`).
- **Código:** `src/rutas/bench/runner.py`, `io.py`, `machine_info.py`.

## Comportamiento esperado
1. **Máquina oficial (D1):** Windows, con `spawn` (no hay `fork`).
2. **Proceso hijo por ejecución:** el hijo cronometra solo la llamada con `time.perf_counter_ns`. Los argumentos se transfieren antes de empezar el cronómetro.
3. **Repeticiones:** 5 por defecto (`REPETITIONS`). Si una ejecución supera `long_run_s` (60 s), no se repite. La mediana es el resultado.
4. **Límite de tiempo:** 300 s (`TIME_LIMIT_S`). Si se supera, el proceso se termina y la medición queda como `completed=False` ("no completada").
5. **Recolector de basura:** desactivado durante la medición y reactivado al terminar.
6. **Entradas inválidas:** si la función lanza una excepción, el hijo la reporta al padre con su texto; la medición queda como no completada, con el error en `extra`.
7. **Registro:** `machine_info.recolectar()` devuelve procesador, núcleos, RAM, SO, Python, versiones de OSMnx, NetworkX, NumPy, pyproj y SciPy, y el commit de git.

## Complejidad esperada (con fuente)
- **Overhead de `spawn`:** arranque de un intérprete nuevo por repetición, del orden de decenas a cientos de milisegundos. No entra en el cronómetro, porque solo se mide la llamada.
- **Límite de tiempo:** el padre espera hasta `timeout_s` con `Pipe.poll` y termina el hijo; la complejidad no aplica.

## Casos de prueba
1. **Función que duerme 10 ms:** mediana entre 9 y 80 ms (`test_runner.py`).
2. **Función que supera el límite:** `completed=False` y mediana `None` (`test_runner.py`).
3. **Función larga:** se mide una sola vez (`test_runner.py`).
4. **Preparación de datos fuera del cronómetro:** una llamada trivial sobre datos grandes mide menos de 200 ms, aunque la transferencia tarde más (`test_runner.py`).
5. **Escritura de CSV y validación de columnas** (`test_bench_io.py`).
6. **Campos del registro de máquina** (`test_bench_io.py`).

## Cómo se mide
No aplica a la propia infraestructura: sus tiempos no son resultados del proyecto. Sí se valida con los casos anteriores.

## Criterio de terminado
- [x] Runner con `spawn`, repeticiones, límite y no completadas.
- [x] Registro de máquina y entorno en `results/_meta/`.
- [x] CSV con columnas fijas y validación del anexo.
- [x] Tests de los casos 1 a 6 en verde.
- [ ] Revisión por una persona distinta del autor.
- [ ] Medición de R1.3 registrada con esta infraestructura (hecha: `results/r1_tiempos_componente.csv`).
