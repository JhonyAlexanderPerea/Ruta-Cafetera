"""Medición de algoritmos según el protocolo de la sección 6 del enunciado (D1: Windows, spawn).

- Cada ejecución corre en un proceso hijo creado con `spawn` (no existe `fork` en Windows).
- El hijo cronometra solo la llamada a `fn` con `perf_counter_ns`. Los datos deben estar cargados
  antes: `fn` es una función sin argumentos, o con argumentos ya enlazados mediante `functools.partial`.
  Los argumentos se transfieren al hijo serializados, pero esa transferencia queda fuera del cronómetro.
- Recolector de basura desactivado durante la medición (se reactiva al terminar).
- Límite de tiempo por ejecución: si pasa, se mata el hijo y la medición queda `completed=False`.
- Si la primera ejecución supera `long_run_s`, no se repite (regla de ejecuciones largas).
"""

from __future__ import annotations

import gc
import multiprocessing as mp
import statistics
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from rutas.config import REPETITIONS, TIME_LIMIT_S

_CONTEXTO = mp.get_context("spawn")


@dataclass
class Measurement:
    median_ms: float | None
    runs_ms: list[float]
    completed: bool
    extra: dict[str, Any] = field(default_factory=dict)


def _ejecutar_en_hijo(conn, fn: Callable[[], Any]) -> None:
    gc.disable()
    try:
        t0 = time.perf_counter_ns()
        resultado = fn()
        t1 = time.perf_counter_ns()
        conn.send(((t1 - t0) / 1e6, {"resultado_tipo": type(resultado).__name__}))
    except BaseException as exc:  # noqa: BLE001 - se reporta al padre
        conn.send((None, {"error": repr(exc)}))
    finally:
        gc.enable()
        conn.close()


def _una_ejecucion(fn: Callable[[], Any], timeout_s: float) -> tuple[float | None, dict]:
    padre, hijo = _CONTEXTO.Pipe(duplex=False)
    proc = _CONTEXTO.Process(target=_ejecutar_en_hijo, args=(hijo, fn))
    proc.start()
    hijo.close()
    if not padre.poll(timeout_s):
        proc.terminate()
        proc.join()
        return None, {"timeout": True}
    ms, extra = padre.recv()
    proc.join()
    return ms, extra


def measure(
    fn: Callable[[], Any],
    *,
    reps: int = REPETITIONS,
    timeout_s: float = TIME_LIMIT_S,
    long_run_s: float = 60.0,
) -> Measurement:
    tiempos: list[float] = []
    extra: dict[str, Any] = {}
    for _ in range(reps):
        ms, info = _una_ejecucion(fn, timeout_s)
        extra.update(info)
        if ms is None:
            return Measurement(median_ms=None, runs_ms=tiempos, completed=False, extra=extra)
        tiempos.append(ms)
        if ms / 1000 > long_run_s:
            break
    return Measurement(
        median_ms=statistics.median(tiempos), runs_ms=tiempos, completed=True, extra=extra
    )
