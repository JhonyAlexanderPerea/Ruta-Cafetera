# Decisiones de diseño

Registro de decisiones relevantes: qué se decidió, alternativas y por qué. Cada entrada indica quién la tomó.

## D1. Medición oficial en Windows (Python 3.12 con uv)

- **Decidido por:** el grupo (2026-11-09).
- **Qué:** todas las mediciones oficiales se hacen en el mismo equipo Windows 11 con Python 3.12.16 gestionado por `uv`.
- **Consecuencia para `bench/runner.py`:** no se usa `multiprocessing` con `fork` (no existe en Windows). Cada ejecución corre en un proceso hijo creado con `spawn`. El padre pasa al hijo la función y sus argumentos ya cargados (picklables), el hijo toma el tiempo solo alrededor de la llamada, y devuelve el tiempo por la conexión. La carga de datos queda fuera del cronómetro.
- **Alternativa descartada:** `fork` en Linux/macOS, porque la máquina oficial es Windows.
- **Registro:** CPU, RAM, SO y versiones en `results/_meta/` (con `py-cpuinfo` y `psutil`).

## D2. Timeouts de descarga por red

- **Decidido por:** nosotros, como propuesta del roadmap; el grupo puede ajustarlo.
- **Qué:** 90 s (2 km), 180 s (5 km), 360 s (10 km), 720 s (20 km) y 1800 s (departamento).
- **Por qué:** el roadmap fija los extremos (90 s y 1800 s); los intermedios se escalaron según el tamaño de la red. El timeout se aplica por llamada y se restaura al terminar.

## D3. Radio de descarga con `dist_type="bbox"`

- **Decidido por:** nosotros.
- **Qué:** `graph_from_point` se llama con `dist_type="bbox"` explícito. El radio es la mitad del lado de un cuadrado, no un círculo.
- **Por qué:** es el default de OSMnx 2.1.1 instalado; dejarlo explícito evita que una actualización cambie las redes sin aviso. Queda registrado en el `consulta` del `.meta.json`.

## D4. Criterio de "cercanos" para los pares de Dijkstra

- **Decidido por:** pendiente del grupo.
- **Propuesta:** mismo municipio o municipios vecinos y distancia en línea recta ≤ 25 km. El enunciado solo pide lo primero; los 25 km son nuestra propuesta.

## D5. Algoritmo de envolvente convexa

- **Decidido por:** pendiente del grupo (PARADA 5).
- **Opciones:** QuickHull (recomendado en el roadmap) o fusión por tangentes de divide y vencerás. El enunciado pide divide y vencerás; QuickHull se suele clasificar así, pero la fusión es la versión que no admite discusión.

## D6. Centro de los radios: plaza de Bolívar

- **Decidido por:** nosotros.
- **Qué:** `PLAZA_BOLIVAR = (4.5325757, -75.6730045)`.
- **Verificación:** el centroide del polígono "Plaza de Bolívar" en OpenStreetMap está a unos 4 m de ese punto. Es una comprobación contra los datos de OSM, no una verificación visual humana; la PARADA 1 la hace el grupo.

## D7. `make` no disponible en Windows

- **Decidido por:** nosotros.
- **Qué:** los comandos del `Makefile` se documentan como equivalentes de `uv` en el README. El `Makefile` se mantiene para Linux/macOS y CI.
