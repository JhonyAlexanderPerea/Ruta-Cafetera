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

- **Decidido por:** el grupo, según el enunciado (R2): "del mismo municipio o de municipios vecinos".
- **Qué:** un par es "cercano" si sus dos lugares están en el mismo municipio o en municipios vecinos. Sin límite en km.
- **Vecindad:** calculada con OSMnx (`geocode_to_gdf`) sobre los polígonos de los 12 municipios del Quindío, consulta del 2026-11-10. Dos municipios son vecinos si sus polígonos se tocan o comparten frontera.
- **Pares de vecinos (22):** Armenia–Calarcá, Armenia–Circasia, Armenia–La Tebaida, Armenia–Montenegro, Armenia–Salento, Buenavista–Calarcá, Buenavista–Córdoba, Buenavista–Pijao, Calarcá–Córdoba, Calarcá–La Tebaida, Calarcá–Pijao, Calarcá–Salento, Circasia–Filandia, Circasia–Montenegro, Circasia–Quimbaya, Circasia–Salento, Córdoba–Pijao, Filandia–Quimbaya, Filandia–Salento, Génova–Pijao, La Tebaida–Montenegro, Montenegro–Quimbaya.
- **Pendiente de revisar en mapa:** los polígonos de OSM pueden tener errores de frontera. Génova aparece con un solo vecino (Pijao); conviene confirmarlo antes de congelar la tabla.
- **Respaldo:** si la tabla de vecinos no se puede validar, usar 25 km en línea recta. Esa cifra es nuestra propuesta; el enunciado no la menciona.
- **Motivo del criterio:** la versión lineal de Dijkstra es O(V²) y en la red completa puede tardar minutos por consulta (enunciado R2). Los pares cercanos mantienen el costo bajo; la distancia en línea recta no controla el costo, porque lo que pesa son los nodos explorados.

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
