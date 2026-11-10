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

## D8. Velocidad de cada tramo y tiempo de viaje (R1.2)

- **Estado:** velocidades aprobadas en PARADA 2 con el ajuste de troncales urbanas (50 km/h). El supuesto de rutas nacionales queda marcado para revisión.
- **Qué:** `time_s = dist_m / velocidad`, con la velocidad de cada arista obtenida así:
  1. **Velocidad explícita de OSM** (`maxspeed`) cuando la arista la tiene. Hay 1.307 de 20.153 aristas en el departamento (6,5 %).
  2. **Vías residenciales** sin velocidad explícita: **30 km/h**. Es el máximo que fija la ley para zonas residenciales.
  3. **Otros tipos de vía sin velocidad explícita:** mediana de las velocidades explícitas de su tipo de vía en el departamento: no clasificada, terciaria y secundaria 30 km/h; primaria 50 km/h.
  3a. **Troncales (`trunk`) sin velocidad explícita:**
     - **Dentro de ciudad** (nombre de calle urbana, p. ej. Carrera 23 o Carrera 16 en Armenia): **50 km/h**. Decisión del grupo.
     - **Rutas nacionales** (ref 40 o 29, p. ej. Autopista del Café) sin velocidad explícita: **50 km/h**, igual que la primaria. Es un supuesto a revisar; la mediana de las rutas nacionales con velocidad explícita (30 km/h) mezcla tramos urbanos y no sirve.
  4. **Respaldo:** 30 km/h, si el tipo de vía no tiene datos.
- **Techos de verificación** (no se aplican como velocidad, sirven para comprobar que el resultado no los supera): 30 km/h en zonas residenciales y escolares; 80 km/h en vías urbanas para servicio público, carga y transporte escolar, y 80 km/h en carreteras nacionales y departamentales para esos mismos vehículos; 120 km/h como máximo general en carreteras nacionales y departamentales.
- **Fuente de los techos:** Ley 1239 de 2008, que modifica los artículos 106 y 107 del Código Nacional de Tránsito (Ley 769 de 2002). La velocidad real de cada vía la fija la autoridad municipal, el Ministerio de Transporte o la Gobernación, no la ley.
- **Limitaciones que hay que escribir en el informe:**
  - Las velocidades son una **estimación del modelo**, no tiempos reales de recorrido.
  - La mediana de las troncales (30 km/h) sale de pocos datos y etiquetas de OSM, y parece baja para una troncal. Se debe mencionar.
  - La regla de 50 km/h para vías urbanas que aparece en resúmenes de búsqueda no está en la Ley 1239; no se usa hasta confirmar la norma posterior.

## D9. Lugares a más de 500 m de su nodo (PARADA 2)

- **Decidido por:** el grupo, en PARADA 2. Se acepta la propuesta.
- **Qué:** se conservan y se documentan. Son `at_03` (Valle de Cocora) y `at_11` (El Paraíso del Bambú y La Guadua), con distancias de hasta 1.063 m.
- **Por qué:** ambos están en zona rural. El nodo más cercano de la componente es el acceso real por vía. Reubicarlos o reemplazarlos cambiaría el catálogo sin una razón de datos.
- **En el informe:** se marca `a_mas_de_500m = True` en `places.csv` y se explica que la distancia al nodo es mayor que el umbral por la ubicación rural.

## D10. Supuesto de velocidad en rutas nacionales sin dato (PARADA 2)

- **Decidido por:** el grupo, en PARADA 2. Se acepta el supuesto.
- **Qué:** troncales de ruta nacional (ref 40 o 29) sin `maxspeed` usan 50 km/h, igual que la primaria.
- **Se documenta como supuesto**, no como dato. La mediana de las rutas nacionales con velocidad explícita (30 km/h) mezcla tramos urbanos y no sirve como referencia.

## D12. Algoritmo de envolvente convexa (R3, PARADA 5)

- **Decidido por:** el grupo, tras comparar las dos opciones (fusión por tangentes y QuickHull).
- **Qué:** divide y vencerás con **fusión por tangentes**. Puntos ordenados por (x, y), mitades recursivas, y en la fusión se buscan las tangentes inferior y superior entre las dos envolventes.
- **Por qué:** es divide y vencerás en su forma clásica, sin discusión sobre la clasificación. La recurrencia es T(n) = 2T(n/2) + O(n), así que O(n log n) en el peor caso, sin depender de la distribución de los puntos. La profundidad de la recursión es log₂ n.
- **Alternativa descartada:** QuickHull. Es más simple y puede ser más rápido en la práctica, pero su peor caso es O(n²) y su clasificación como divide y vencerás se debe justificar.
- **Coordenadas:** enteros (UTM redondeado), aritmética exacta. Puntos colineales sobre un lado no son vértices. Si todos son colineales, se devuelven los dos extremos.
- **Verificación:** 49 tests (casos a mano, colineales, duplicados, 1, 2 y 3 puntos, circunferencia, 40 nubes aleatorias contra SciPy) y 300 casos de estrés (nubes uniformes, rejillas con muchas colineales y cúmulos). Todos coinciden con `scipy.spatial.ConvexHull`.
- **Resultados:** `results/r3_envolvente.csv`. El tiempo propio es entre 3 y 40 veces el de SciPy, porque SciPy/Qhull está implementado en C y el nuestro en Python puro. Para 10.000 → 50.000 puntos el tiempo crece unas 5,9 veces, coherente con n log n.
